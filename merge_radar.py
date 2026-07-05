#!/usr/bin/env python3
"""
merge_radar.py — merge new_items.json into GitHub main data.json + seen.json
via GitHub Contents API (git push is blocked in this environment).
"""

import base64
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

REPO = "dzkeke-tech/market-radar"
BRANCH = "main"
API_BASE = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TZ_BJ = timezone(timedelta(hours=8))


def bj_now() -> str:
    return datetime.now(TZ_BJ).strftime("%Y-%m-%d %H:%M (北京时间)")


def bj_today() -> str:
    return datetime.now(TZ_BJ).strftime("%Y-%m-%d")


def gh_get(path: str):
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return json.loads(body) if body else {}, e.code


def gh_put(path: str, payload: dict) -> tuple:
    url = f"{API_BASE}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return json.loads(body) if body else {}, e.code


def fetch_file(filename: str):
    """Fetch file from GitHub main branch. Returns (content_str, sha)."""
    data, status = gh_get(f"/repos/{REPO}/contents/{filename}?ref={BRANCH}")
    if status == 404:
        return None, None
    if status != 200:
        raise RuntimeError(f"GET {filename} -> HTTP {status}: {data}")
    content = base64.b64decode(data["content"]).decode("utf-8")
    return content, data["sha"]


def publish_file(filename: str, content: str, sha: str | None, message: str):
    """PUT file to GitHub main branch."""
    b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    payload = {"message": message, "content": b64, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    result, status = gh_put(f"/repos/{REPO}/contents/{filename}", payload)
    print(f"  {filename} -> HTTP {status}")
    if status not in (200, 201):
        print(f"  PUBLISH FAILED {filename}:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)


def make_id(url: str, title: str) -> str:
    s = url.strip() if url and url.strip() else title.strip()
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def parse_time_key(item: dict) -> str:
    """Return sortable string for time field."""
    return str(item.get("time", item.get("first_seen", "")))


def main():
    if not TOKEN:
        print("ERROR: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    # ── 1. Load new items ──────────────────────────────────────────────────
    new_items_path = os.path.join(os.path.dirname(__file__), "new_items.json")
    with open(new_items_path, encoding="utf-8") as f:
        new_items: list = json.load(f)
    print(f"Loaded {len(new_items)} new items from new_items.json")

    # ── 2. Load keywords.json for watchlist ────────────────────────────────
    kw_path = os.path.join(os.path.dirname(__file__), "keywords.json")
    with open(kw_path, encoding="utf-8") as f:
        keywords = json.load(f)
    watchlist = list(keywords.get("entries", {}).keys())

    # ── 3. Fetch current data.json from GitHub main ────────────────────────
    print("Fetching data.json from GitHub main …")
    data_str, data_sha = fetch_file("data.json")
    if data_str:
        existing_data = json.loads(data_str)
        existing_items: list = existing_data.get("items", [])
    else:
        existing_data = {}
        existing_items = []
    print(f"  Found {len(existing_items)} existing items")

    # ── 4. Fetch seen.json from GitHub main ───────────────────────────────
    print("Fetching seen.json from GitHub main …")
    seen_str, seen_sha = fetch_file("seen.json")
    if seen_str:
        seen_data = json.loads(seen_str)
        seen_ids: set = set(seen_data.get("ids", []))
    else:
        seen_data = {}
        seen_ids = set()
    print(f"  Found {len(seen_ids)} seen IDs")

    # ── 5. Build existing ID set ───────────────────────────────────────────
    existing_ids = {item["id"] for item in existing_items if "id" in item}

    # ── 6. Deduplicate new items ───────────────────────────────────────────
    accepted = []
    skipped = 0
    for item in new_items:
        item_id = item.get("id") or make_id(item.get("url", ""), item.get("title", ""))
        item["id"] = item_id
        if item_id in seen_ids or item_id in existing_ids:
            skipped += 1
            continue
        accepted.append(item)
    print(f"  Accepted {len(accepted)} truly new items; skipped {skipped} duplicates")

    # ── 7. Mark old items is_new=false; stamp new items ───────────────────
    today = bj_today()
    for item in existing_items:
        item["is_new"] = False
        if "first_seen" not in item:
            item["first_seen"] = today

    for item in accepted:
        item["is_new"] = True
        item["first_seen"] = today

    # ── 8. Merge ───────────────────────────────────────────────────────────
    merged = accepted + existing_items

    # ── 9. Prune: drop items older than 7 days ────────────────────────────
    cutoff = (datetime.now(TZ_BJ) - timedelta(days=7)).strftime("%Y-%m-%d")
    before_prune = len(merged)
    merged = [
        item for item in merged
        if item.get("first_seen", today) >= cutoff
    ]
    print(f"  Pruned {before_prune - len(merged)} items older than 7 days; {len(merged)} remain")

    # ── 10. Storage prune if >150 ─────────────────────────────────────────
    MAX_ITEMS = 150
    if len(merged) > MAX_ITEMS:
        old_t3 = [i for i in merged if not i.get("is_new") and i.get("tier") == 3]
        old_t3.sort(key=parse_time_key)
        need_drop = len(merged) - MAX_ITEMS
        drop_ids = {i["id"] for i in old_t3[:need_drop]}
        if len(drop_ids) < need_drop:
            old_t2 = [i for i in merged if not i.get("is_new") and i.get("tier") == 2 and i["id"] not in drop_ids]
            old_t2.sort(key=parse_time_key)
            still_need = need_drop - len(drop_ids)
            drop_ids |= {i["id"] for i in old_t2[:still_need]}
        merged = [i for i in merged if i["id"] not in drop_ids]
        print(f"  Storage prune: dropped {need_drop} old tier-2/3 items; {len(merged)} remain")

    # ── 11. Sort ──────────────────────────────────────────────────────────
    def sort_key(item):
        is_new = 0 if item.get("is_new") else 1
        tier = item.get("tier", 9)
        time_str = parse_time_key(item)
        return (is_new, tier, "~" + time_str)  # "~" flips to descending

    merged.sort(key=sort_key)

    # ── 12. Build new data.json ────────────────────────────────────────────
    new_data = {
        "is_sample": False,
        "updated_at": bj_now(),
        "next_runs": ["08:00", "13:00", "18:00"],
        "watchlist": watchlist,
        "positions": [],
        "items": merged,
    }

    # ── 13. Update seen.json ───────────────────────────────────────────────
    new_ids_set = {item["id"] for item in accepted}
    all_seen = list(seen_ids | new_ids_set)
    if len(all_seen) > 1000:
        all_seen = all_seen[-1000:]
    new_seen = {
        "updated_at": bj_now(),
        "ids": all_seen,
    }

    # ── 14. Publish ────────────────────────────────────────────────────────
    date_str = today
    print("Publishing data.json …")
    publish_file(
        "data.json",
        json.dumps(new_data, ensure_ascii=False, indent=2),
        data_sha,
        f"chore(radar): update market radar for {date_str} (+{len(accepted)} new)",
    )
    print("Publishing seen.json …")
    publish_file(
        "seen.json",
        json.dumps(new_seen, ensure_ascii=False, indent=2),
        seen_sha,
        f"chore(radar): update seen for {date_str}",
    )

    # ── 15. Summary ────────────────────────────────────────────────────────
    print(
        f"\n运行自检 ✓\n"
        f"  本次新增：{len(accepted)} 条\n"
        f"  去重丢弃：{skipped} 条\n"
        f"  累积总数：{len(merged)} 条\n"
        f"  data.json + seen.json 两个 PUT 均 200/201\n"
        f"  无法核实条目：{sum(1 for i in accepted if not i.get('verified'))} 条（verified=false）\n"
    )


if __name__ == "__main__":
    main()
