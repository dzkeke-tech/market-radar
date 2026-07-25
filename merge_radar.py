#!/usr/bin/env python3
"""
merge_radar.py — Market Radar 数据合并 & 发布脚本

职责：读取 Claude 本次生成的 new_items.json，与 GitHub 上的历史 data.json 合并，
     剪枝后通过 GitHub Contents API 写回 claude/radar-data 分支。

Claude 的上下文里永远不需要载入历史条目。
用法：python3 merge_radar.py

v4 改动（2026-07-25）：新增发布日期硬性过滤，防止把过期新闻（原文发布已数周/数月）
当作"新增"收录进雷达。触发原因：2026-07-25 发现"阿里巴巴全年收入首破1万亿元"
（原文发布于 2026-05-13）、"小米汽车6月销量"（原文 2026-07-08）、"腾讯混元Hy3"
（原文 2026-07-07）三条新闻被当作当日新增收录，实际都是旧闻。
详见 routine-prompt-fixed.md 2.6/2.7 节。
"""

import json
import os
import sys
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

REPO    = "dzkeke-tech/market-radar"
BRANCH  = "claude/radar-data"
API_URL = f"https://api.github.com/repos/{REPO}/contents"
TOKEN   = os.environ.get("GITHUB_TOKEN", "")

MAX_ITEMS = 150
KEEP_DAYS = 7

# 发布日期硬性过滤（v4 新增）：
#   - MAX_AGE_SOFT_DAYS：默认时间窗。超过则要求 still_developing=true 才放行。
#   - MAX_AGE_HARD_DAYS：硬上限。无论是否 still_developing，超过一律丢弃。
#   - 缺失/无法解析 published_date 的候选：暂不硬性丢弃（避免 Claude 端 prompt
#     还没升级、字段缺失时把新流水线打断），只打印警告。等 routine 稳定产出
#     published_date 后，可把 REQUIRE_PUBLISHED_DATE 改成 True 转为硬性拦截。
MAX_AGE_SOFT_DAYS = 2
MAX_AGE_HARD_DAYS = 5
REQUIRE_PUBLISHED_DATE = False

TZ_BJ = timezone(timedelta(hours=8))


# ── GitHub API helpers ────────────────────────────────────────────────────────

def gh_get(filename):
    """Fetch a file from BRANCH. Returns (parsed_json, sha) or (None, None) on 404."""
    url = f"{API_URL}/{filename}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept":        "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(req) as r:
            meta = json.loads(r.read())
        data = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
        return data, meta["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise


def gh_put(filename, obj, sha, message):
    """PUT a JSON object to BRANCH. Exits with code 1 on failure."""
    content_b64 = base64.b64encode(
        json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode()
    body = {"message": message, "content": content_b64, "branch": BRANCH}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(
        f"{API_URL}/{filename}",
        data=json.dumps(body).encode(),
        method="PUT",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept":        "application/vnd.github+json",
            "Content-Type":  "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            code = r.status
        print(f"  PUT {filename} → HTTP {code}")
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"  PUT {filename} FAILED HTTP {e.code}: {err}", file=sys.stderr)
        sys.exit(1)


# ── Item helpers ──────────────────────────────────────────────────────────────

def validate_new_items(items, today_str):
    """发布日期硬性过滤（v4 新增）。

    Claude 在 new_items.json 里应为每条候选填 published_date（原文发布日期，
    YYYY-MM-DD，从原文页面的时间戳/作者栏读取，而不是"今天发现它"的日期）。

    规则：
      - published_date 距今 > MAX_AGE_HARD_DAYS：无条件丢弃（防"1-3个月前旧闻"复发）。
      - published_date 距今 > MAX_AGE_SOFT_DAYS 且未标 still_developing=true：丢弃。
      - published_date 格式无法解析：丢弃并警告。
      - published_date 缺失：REQUIRE_PUBLISHED_DATE=False 时仅警告放行（过渡期，
        避免 routine 侧 prompt 还没升级导致整条流水线被打断）；改成 True 后转硬性丢弃。

    返回 (valid_items, dropped)，dropped 为 [(item, reason), ...] 供日志打印。
    """
    today = datetime.strptime(today_str, "%Y-%m-%d")
    valid, dropped = [], []

    for it in items:
        pub = it.get("published_date")

        if not pub:
            if REQUIRE_PUBLISHED_DATE:
                dropped.append((it, "缺少 published_date（硬性要求已开启）"))
                continue
            print(f"  ⚠ [{it.get('id','?')}] 缺少 published_date，暂按放行处理（过渡期）：{it.get('title','')[:40]}")
            valid.append(it)
            continue

        try:
            pub_dt = datetime.strptime(str(pub)[:10], "%Y-%m-%d")
        except ValueError:
            dropped.append((it, f"published_date 格式无法解析: {pub!r}"))
            continue

        age_days = (today - pub_dt).days
        if age_days < 0:
            age_days = 0  # 允许时区/剪辑误差

        if age_days > MAX_AGE_HARD_DAYS:
            dropped.append((it, f"原文发布于 {pub}，距今 {age_days} 天，超过硬上限 {MAX_AGE_HARD_DAYS} 天"))
            continue

        if age_days > MAX_AGE_SOFT_DAYS and not it.get("still_developing"):
            dropped.append((it, f"原文发布于 {pub}，距今 {age_days} 天，超过默认时间窗 {MAX_AGE_SOFT_DAYS} 天且未标 still_developing"))
            continue

        valid.append(it)

    return valid, dropped


def prune(items, today_str):
    """Drop items older than KEEP_DAYS (never drop is_new=True); trim to MAX_ITEMS."""
    cutoff = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")

    # 1. Drop stale items (keep all is_new=True regardless)
    items = [i for i in items if i.get("is_new") or i.get("first_seen", "9999") >= cutoff]

    # 2. If still over limit, trim oldest low-tier items first
    for tier in [3, 2]:
        if len(items) <= MAX_ITEMS:
            break
        candidates = sorted(
            [i for i in items if not i.get("is_new") and i.get("tier") == tier],
            key=lambda x: x.get("first_seen", ""),
        )
        to_remove = {i["id"] for i in candidates[:len(items) - MAX_ITEMS]}
        items = [i for i in items if i["id"] not in to_remove]

    return items


def sort_items(items):
    tier_rank = {1: 0, 2: 1, 3: 2, "1": 0, "2": 1, "3": 2}
    return sorted(items, key=lambda x: (
        0 if x.get("is_new") else 1,
        tier_rank.get(x.get("tier", 3), 2),
        x.get("first_seen", ""),
    ))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        print("Error: GITHUB_TOKEN not set.", file=sys.stderr)
        sys.exit(1)

    # new_items.json lives next to this script
    here = os.path.dirname(os.path.abspath(__file__))
    new_items_path = os.path.join(here, "new_items.json")
    if not os.path.exists(new_items_path):
        print(f"Error: {new_items_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(new_items_path, encoding="utf-8") as f:
        new_items = json.load(f)
    print(f"Loaded {len(new_items)} candidate new items from new_items.json")

    now_bj    = datetime.now(TZ_BJ)
    today_str = now_bj.strftime("%Y-%m-%d")
    updated_at = now_bj.strftime("%Y-%m-%d %H:%M") + " (北京时间)"

    # 发布日期硬性过滤（v4 新增）——见 validate_new_items 说明
    new_items, dropped = validate_new_items(new_items, today_str)
    if dropped:
        print(f"Validation dropped {len(dropped)} candidate(s):")
        for it, reason in dropped:
            print(f"  ✗ [{it.get('id','?')}] {it.get('title','')[:40]} → {reason}")

    # Fetch history from branch
    print("Fetching data.json …")
    data_json, data_sha = gh_get("data.json")
    print("Fetching seen.json …")
    seen_json, seen_sha = gh_get("seen.json")

    existing_items = (data_json or {}).get("items", [])
    seen_ids       = set((seen_json or {}).get("ids", []))

    # Deduplicate
    existing_ids = {i["id"] for i in existing_items}
    truly_new = [i for i in new_items if i.get("id") not in seen_ids and i.get("id") not in existing_ids]
    skipped = len(new_items) - len(truly_new)
    print(f"After dedup: {len(truly_new)} new, {skipped} skipped")

    # Stamp new items
    for item in truly_new:
        item.setdefault("first_seen", today_str)
        item["is_new"] = True

    # Mark existing items as old
    for item in existing_items:
        item["is_new"] = False

    # Merge → prune → sort
    merged = prune(truly_new + existing_items, today_str)
    merged = sort_items(merged)

    # Update seen IDs（校验环节丢弃的候选也一并计入 seen，避免下一轮重复抓取/重复丢弃同一条）
    all_candidate_ids = {i["id"] for i in new_items if i.get("id")} | {i["id"] for i, _ in dropped if i.get("id")}
    new_seen_ids = list(seen_ids | all_candidate_ids)
    if len(new_seen_ids) > 1000:
        new_seen_ids = new_seen_ids[-1000:]

    # Build output objects (preserve meta from existing data.json)
    meta = data_json or {}
    new_data = {
        "is_sample":  False,
        "updated_at": updated_at,
        "next_runs":  meta.get("next_runs", ["08:00", "13:00", "18:00"]),
        "watchlist":  meta.get("watchlist", []),
        "positions":  [],
        "items":      merged,
    }
    new_seen = {
        "updated_at": updated_at,
        "ids":        new_seen_ids,
    }

    # Publish
    date_tag = now_bj.strftime("%Y-%m-%d")
    print("Publishing …")
    gh_put("data.json", new_data, data_sha,
           f"chore(radar): update market radar {date_tag} (+{len(truly_new)} items)")
    gh_put("seen.json", new_seen, seen_sha,
           f"chore(radar): update seen {date_tag}")

    print(f"\n✓ +{len(truly_new)} new | {len(existing_items)} existing | {len(merged)} total in data.json"
          + (f" | {len(dropped)} dropped by date-validation" if dropped else ""))


if __name__ == "__main__":
    main()
