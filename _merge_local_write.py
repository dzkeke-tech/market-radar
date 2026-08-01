#!/usr/bin/env python3
"""
Same merge logic as merge_radar.py but writes to local files instead of GitHub API.
The caller (Claude) will then push the files via MCP tools.
"""
import json, os, sys, base64, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

REPO    = "dzkeke-tech/market-radar"
BRANCH  = "main"
API_URL = f"https://api.github.com/repos/{REPO}/contents"
TOKEN   = os.environ.get("GITHUB_TOKEN", "")

MAX_ITEMS = 150
KEEP_DAYS = 7
STALE_BRANCH_GRACE_DAYS = KEEP_DAYS
MAX_AGE_SOFT_DAYS = 2
MAX_AGE_HARD_DAYS = 5
REQUIRE_PUBLISHED_DATE = False
TZ_BJ = timezone(timedelta(hours=8))


def gh_get(filename):
    url = f"{API_URL}/{filename}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
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


def validate_new_items(items, today_str):
    today = datetime.strptime(today_str, "%Y-%m-%d")
    valid, dropped = [], []
    for it in items:
        pub = it.get("published_date")
        if not pub:
            if REQUIRE_PUBLISHED_DATE:
                dropped.append((it, "缺少 published_date"))
                continue
            print(f"  ⚠ [{it.get('id','?')}] 缺少 published_date，暂按放行处理")
            valid.append(it)
            continue
        try:
            pub_dt = datetime.strptime(str(pub)[:10], "%Y-%m-%d")
        except ValueError:
            dropped.append((it, f"published_date 格式无法解析: {pub!r}"))
            continue
        age_days = max(0, (today - pub_dt).days)
        if age_days > MAX_AGE_HARD_DAYS:
            dropped.append((it, f"原文发布于 {pub}，距今 {age_days} 天，超过硬上限 {MAX_AGE_HARD_DAYS} 天"))
            continue
        if age_days > MAX_AGE_SOFT_DAYS and not it.get("still_developing"):
            dropped.append((it, f"原文发布于 {pub}，距今 {age_days} 天，超过默认时间窗 {MAX_AGE_SOFT_DAYS} 天且未标 still_developing"))
            continue
        valid.append(it)
    return valid, dropped


def is_stale_branch(existing_items, today_str):
    non_new = [i for i in existing_items if not i.get("is_new") and i.get("first_seen")]
    if not non_new:
        return False
    newest = max(i["first_seen"] for i in non_new)
    try:
        gap = (datetime.strptime(today_str, "%Y-%m-%d") - datetime.strptime(newest, "%Y-%m-%d")).days
    except ValueError:
        return False
    return gap > STALE_BRANCH_GRACE_DAYS


def prune(items, today_str, skip_date_prune=False):
    if not skip_date_prune:
        cutoff = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")
        items = [i for i in items if i.get("is_new") or i.get("first_seen", "9999") >= cutoff]
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


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    new_items_path = os.path.join(here, "new_items.json")
    with open(new_items_path, encoding="utf-8") as f:
        new_items = json.load(f)
    print(f"Loaded {len(new_items)} candidate new items")

    now_bj = datetime.now(TZ_BJ)
    today_str = now_bj.strftime("%Y-%m-%d")
    updated_at = now_bj.strftime("%Y-%m-%d %H:%M") + " (北京时间)"

    new_items, dropped = validate_new_items(new_items, today_str)
    if dropped:
        print(f"Validation dropped {len(dropped)} candidate(s):")
        for it, reason in dropped:
            print(f"  ✗ [{it.get('id','?')}] {it.get('title','')[:40]} → {reason}")

    print("Fetching data.json …")
    data_json, data_sha = gh_get("data.json")
    print("Fetching seen.json …")
    seen_json, seen_sha = gh_get("seen.json")

    existing_items = (data_json or {}).get("items", [])
    seen_ids = set((seen_json or {}).get("ids", []))

    existing_ids = {i["id"] for i in existing_items}
    truly_new = [i for i in new_items if i.get("id") not in seen_ids and i.get("id") not in existing_ids]
    skipped = len(new_items) - len(truly_new)
    print(f"After dedup: {len(truly_new)} new, {skipped} skipped")

    for item in truly_new:
        item.setdefault("first_seen", today_str)
        item["is_new"] = True
    for item in existing_items:
        item["is_new"] = False

    skip_date_prune = is_stale_branch(existing_items, today_str)
    if skip_date_prune:
        print(f"⚠ 陈旧分支保护触发，跳过按日期剪枝")

    merged = prune(truly_new + existing_items, today_str, skip_date_prune=skip_date_prune)
    merged = sort_items(merged)

    all_candidate_ids = {i["id"] for i in new_items if i.get("id")} | {i["id"] for i, _ in dropped if i.get("id")}
    new_seen_ids = list(seen_ids | all_candidate_ids)
    if len(new_seen_ids) > 1000:
        new_seen_ids = new_seen_ids[-1000:]

    meta = data_json or {}
    new_data = {
        "is_sample": False,
        "updated_at": updated_at,
        "next_runs": meta.get("next_runs", ["08:00", "13:00", "18:00"]),
        "watchlist": meta.get("watchlist", []),
        "positions": [],
        "items": merged,
    }
    new_seen = {
        "updated_at": updated_at,
        "ids": new_seen_ids,
    }

    # Write locally
    out_data = os.path.join(here, "_out_data.json")
    out_seen = os.path.join(here, "_out_seen.json")
    with open(out_data, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    with open(out_seen, "w", encoding="utf-8") as f:
        json.dump(new_seen, f, ensure_ascii=False, indent=2)

    # Also emit SHAs for use in MCP push
    print(f"LOCAL_DATA_SHA={data_sha}")
    print(f"LOCAL_SEEN_SHA={seen_sha}")
    print(f"✓ +{len(truly_new)} new | {len(existing_items)} existing | {len(merged)} total in _out_data.json"
          + (f" | {len(dropped)} dropped by date-validation" if dropped else ""))


if __name__ == "__main__":
    main()
