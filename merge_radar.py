#!/usr/bin/env python3
"""
merge_radar.py — Market Radar 数据合并 & 发布脚本

职责：读取 Claude 本次生成的 new_items.json，与 GitHub 上的历史 data.json 合并，
     剪枝后通过 GitHub Contents API 写回 main 分支。

Claude 的上下文里永远不需要载入历史条目。
用法：python3 merge_radar.py

v4 改动（2026-07-25 上午）：新增发布日期硬性过滤，防止把过期新闻（原文发布已数周/数月）
当作"新增"收录进雷达。触发原因：2026-07-25 发现"阿里巴巴全年收入首破1万亿元"
（原文发布于 2026-05-13）、"小米汽车6月销量"（原文 2026-07-08）、"腾讯混元Hy3"
（原文 2026-07-07）三条新闻被当作当日新增收录，实际都是旧闻。
详见 routine-prompt.md 2.6/2.7 节。

v6 改动（2026-08-11）：新增 schema 校验闸门 validate_item_schema()。触发原因：
2026-08-11 08:11 那轮 Routine 输出用了另一套字段名（type/entry/tags），漏掉了
why/markets/keywords/group，脚本原样发布、前端又是 `${it.why ? ... : ""}` 这种
写法——缺字段不报错、只安静地少渲染一块，结果当天 7 条新闻全都没有"为何相关"，
市场标签和关键词筛选也一并失效，直到用户自己打开 App 才发现。根因是 Routine 的
prompt 与 routine-prompt.md §6 脱节，而脚本这层完全没有把关。修复：
  (a) 发布前逐条校验前端必需字段，缺失即拒绝该条；
  (b) type→group、tags→keywords 做别名兼容，能救的先救；
  (c) 全部候选都不合格 → 判定为系统性漂移，联网写入前直接 exit(1)，不推降级数据；
      仅部分不合格 → 好的照常发布，末尾以非 0 退出码告警，当天就能发现。

v5 改动（2026-07-25 下午）：把发布目标分支从 claude/radar-data 改回 main，并新增
"陈旧分支保护"。触发原因：v4 上线后 Routine 当天首次真正跑通 merge_radar.py，
写入的是 claude/radar-data 分支——但这个分支自 2026-07-06 起就没人碰过（此前
main 分支一直由另一条"radar: HH:MM batch"命名的旧管线持续更新，直到今天
2026-07-25 08:18 才停）。claude/radar-data 里躺了 19 天的旧数据一夜之间被
prune() 的 KEEP_DAYS=7 逻辑几乎清空，只剩当天新增的 8 条，而这个分支的
updated_at 又比 main 新，于是页面改成展示这个几乎清空的分支——用户看到"之前
推送全没了"。核心问题：两个分支各自独立累积历史，一旦其中一个长期没人写，
下次一写就会被自己的"7天保留期"规则误杀。修复：
  (a) 把 BRANCH 改回 main，与过去19天实际在用、持续更新的分支保持一致，
      不再维护一个可能被遗忘的第二分支；
  (b) prune() 增加陈旧分支保护：如果现有条目里最新的 first_seen 本身已经
      超过 KEEP_DAYS，说明这个数据源已经很久没更新，这次直接跳过按日期
      剪枝（只按 MAX_ITEMS 数量上限裁剪），避免"长期没跑 + 一朝跑通"的
      组合再次清空历史。
"""

import json
import os
import sys
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

REPO    = "dzkeke-tech/market-radar"
BRANCH  = "main"
API_URL = f"https://api.github.com/repos/{REPO}/contents"
TOKEN   = os.environ.get("GITHUB_TOKEN", "")

MAX_ITEMS = 150
KEEP_DAYS = 7
STALE_BRANCH_GRACE_DAYS = KEEP_DAYS  # 若现有数据的最新 first_seen 已超过这个天数，视为“陈旧分支”，本轮跳过按日期剪枝

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


# ── Schema 校验闸门（v6 新增）────────────────────────────────────────────────

# 前端 index.html 渲染每张卡片时依赖的字段。缺任何一个都会导致该条静默降级
# （最典型的是 why 缺失 → "为何相关"整块不渲染，markets 缺失 → 市场标签消失、
# 港股/美股/A股筛选页漏掉这条）。因为前端是 `${it.why ? ... : ""}` 这种写法，
# 缺字段不会报错、只会安静地少一块，所以必须在发布前拦住。
REQUIRED_FIELDS = ["id", "tier", "title", "summary", "why", "source", "url", "markets", "keywords"]

# 机械可推导的字段：缺了不算错，自动补上并打印提示，不阻断发布。
AUTOFILL_DEFAULTS = {"group": "个股", "translated": False, "verified": False}

# 历史别名 → 规范字段名。2026-08-11 那次 Routine 漂移写的是 type/tags，
# 这里做一次兼容映射，能救回来的就救，救不回来的（why/markets）交给下面拦截。
FIELD_ALIASES = {"type": "group", "tags": "keywords"}

VALID_MARKETS = {"HK", "US", "A"}
MIN_WHY_LEN = 8  # 挡住 why 为 ""、"-"、"n/a" 这种敷衍值


def _has_cjk(s):
    return any("\u4e00" <= ch <= "\u9fff" for ch in str(s))


def validate_item_schema(items, now_bj):
    """校验每条候选是否具备前端渲染所需的全部字段。

    返回 (valid, rejected)，rejected 为 [(item, [问题描述, ...]), ...]。

    设计取舍：不是一有问题就整轮 exit(1)。
      - 少数条目有问题 → 丢弃这几条，其余照常发布，最后以非 0 退出码报警；
        否则一条坏数据就会害得当天整份雷达都推不出来。
      - 全部条目都有问题 → 判定为 schema 系统性漂移（就像 2026-08-11 那次
        7/7 全错），在联网写入前直接 exit(1)，绝不把整份降级数据推上线。
    """
    valid, rejected = [], []

    for it in items:
        # 1) 别名兼容：canonical 字段缺失时，从旧字段名搬过来
        for old, new in FIELD_ALIASES.items():
            if old in it and not it.get(new):
                it[new] = it.pop(old)
                print(f"  ⚠ [{it.get('id','?')}] 字段别名 {old} → {new}（Routine prompt 可能已漂移，请核对 routine-prompt.md §6）")

        problems = []

        # 2) 必填字段检查
        for f in REQUIRED_FIELDS:
            v = it.get(f)
            if v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, list) and not v):
                problems.append(f"缺少必填字段 {f}")

        # 3) 关键字段的取值合法性
        if it.get("tier") not in (1, 2, 3, "1", "2", "3"):
            problems.append(f"tier 非法: {it.get('tier')!r}（应为 1/2/3）")

        why = it.get("why")
        if isinstance(why, str) and 0 < len(why.strip()) < MIN_WHY_LEN:
            problems.append(f"why 过短（{len(why.strip())} 字符），疑似占位值: {why!r}")

        mk = it.get("markets")
        if isinstance(mk, list) and mk:
            bad = [m for m in mk if m not in VALID_MARKETS]
            if bad:
                problems.append(f"markets 含非法值 {bad}（只允许 HK/US/A）")

        url = it.get("url")
        if isinstance(url, str) and url.strip() and not url.strip().startswith("http"):
            problems.append(f"url 不是可点击链接: {url!r}")

        if problems:
            rejected.append((it, problems))
            continue

        # 4) 可推导字段自动补齐（不阻断）
        for f, default in AUTOFILL_DEFAULTS.items():
            if f not in it:
                it[f] = default
                print(f"  · [{it.get('id','?')}] 自动补 {f}={default!r}")
        if not it.get("lang"):
            it["lang"] = "zh" if _has_cjk(it.get("title", "")) else "en"
            print(f"  · [{it.get('id','?')}] 自动补 lang={it['lang']!r}")
        if not it.get("time"):
            it["time"] = now_bj.strftime("%H:%M")
            print(f"  · [{it.get('id','?')}] 自动补 time={it['time']!r}")

        valid.append(it)

    return valid, rejected

def is_stale_branch(existing_items, today_str):
    """陈旧分支保护（v5 新增）。

    如果现有历史里"最新"的 first_seen 本身已经比 KEEP_DAYS 还早，说明这批数据
    已经很久没有被追加更新过（分支/流水线曾经断更）。这种情况下如果照常按
    "first_seen < today - KEEP_DAYS 就丢弃"来剪枝，会把全部旧历史一次性清空
    ——这正是 2026-07-25 claude/radar-data 分支history被误删的原因。

    检测到这种情况时，本轮跳过按日期剪枝，只保留按 MAX_ITEMS 的数量上限裁剪，
    避免"断更很久 + 突然又跑通"的组合再次清空历史。
    """
    non_new = [i for i in existing_items if not i.get("is_new") and i.get("first_seen")]
    if not non_new:
        return False
    newest_first_seen = max(i["first_seen"] for i in non_new)
    try:
        gap_days = (datetime.strptime(today_str, "%Y-%m-%d")
                    - datetime.strptime(newest_first_seen, "%Y-%m-%d")).days
    except ValueError:
        return False
    return gap_days > STALE_BRANCH_GRACE_DAYS


def prune(items, today_str, skip_date_prune=False):
    """Drop items older than KEEP_DAYS (never drop is_new=True); trim to MAX_ITEMS.

    skip_date_prune=True（陈旧分支保护触发时）会跳过按日期丢弃这一步，只按
    MAX_ITEMS 数量上限裁剪，防止长期断更的分支一朝更新就被清空历史。
    """
    if not skip_date_prune:
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

    # Schema 校验闸门（v6 新增）——必须在任何联网写入之前，见 validate_item_schema 说明
    candidate_count = len(new_items)
    new_items, rejected = validate_item_schema(new_items, now_bj)
    if rejected:
        print(f"\nSchema 校验拒绝 {len(rejected)}/{candidate_count} 条候选：")
        for it, problems in rejected:
            print(f"  ✗ [{it.get('id','?')}] {str(it.get('title',''))[:40]}")
            for p in problems:
                print(f"      → {p}")
    if candidate_count and not new_items:
        print(
            "\n" + "=" * 68
            + f"\n✗ 中止发布：{candidate_count} 条候选全部未通过 schema 校验。"
              "\n  这通常意味着 Routine 的 prompt 已经漂移，输出结构和前端对不上了。"
              "\n  请照 routine-prompt.md §6 的字段结构核对 Routine prompt 后重跑。"
              "\n  （本轮未写入任何数据，线上仍是上一轮的完好数据。）\n"
            + "=" * 68,
            file=sys.stderr,
        )
        sys.exit(1)

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

    # 陈旧分支保护（v5 新增）：现有历史很久没更新过时，本轮跳过按日期剪枝
    skip_date_prune = is_stale_branch(existing_items, today_str)
    if skip_date_prune:
        print(f"⚠ 检测到陈旧分支（现有历史最新 first_seen 距今超过 {STALE_BRANCH_GRACE_DAYS} 天），"
              f"本轮跳过按日期剪枝，只按 MAX_ITEMS={MAX_ITEMS} 裁剪，避免清空历史。")

    # Merge → prune → sort
    merged = prune(truly_new + existing_items, today_str, skip_date_prune=skip_date_prune)
    merged = sort_items(merged)

    # Update seen IDs（校验环节丢弃的候选也一并计入 seen，避免下一轮重复抓取/重复丢弃同一条）
    all_candidate_ids = ({i["id"] for i in new_items if i.get("id")}
                         | {i["id"] for i, _ in dropped if i.get("id")}
                         | {i["id"] for i, _ in rejected if i.get("id")})
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
          + (f" | {len(dropped)} dropped by date-validation" if dropped else "")
          + (f" | {len(rejected)} rejected by schema-gate" if rejected else ""))

    # 部分条目被 schema 闸门拒绝：好的条目已经发出去了，但仍以非 0 退出码报警，
    # 让 Routine 的运行自检当天就暴露问题，而不是攒着等用户自己发现少了内容。
    if rejected:
        print(
            "\n" + "=" * 68
            + f"\n⚠ 本轮有 {len(rejected)} 条候选因字段缺失被拒绝（其余已正常发布）。"
              "\n  请照 routine-prompt.md §6 核对 Routine prompt 的输出字段。"
              "\n  退出码置为 1 仅作告警，data.json 已成功写入。\n"
            + "=" * 68,
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
