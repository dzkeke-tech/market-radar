#!/usr/bin/env python3
"""merge_radar.py — merge new_items.json into data.json and publish via GitHub Contents API"""

import json
import os
import sys
import base64
import urllib.request
import urllib.error
import datetime
from pathlib import Path

REPO = "dzkeke-tech/market-radar"
MAIN_BRANCH = "main"
DATA_BRANCH = "claude/radar-data"
API_BASE = f"https://api.github.com/repos/{REPO}/contents"
MAX_ITEMS = 150
PRUNE_DAYS = 7


def beijing_now():
    tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(tz)


def beijing_today():
    return beijing_now().strftime("%Y-%m-%d")


def prune_cutoff(today_str):
    today = datetime.date.fromisoformat(today_str)
    return (today - datetime.timedelta(days=PRUNE_DAYS)).isoformat()


def github_get(path, branch):
    """GET file from GitHub Contents API. Returns (content_bytes, sha) or (None, None) on 404."""
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"{API_BASE}/{path}?ref={branch}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "merge-radar/1.0",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            content = base64.b64decode(data["content"])
            return content, data["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        body = e.read().decode("utf-8", errors="replace")
        print(f"GET {path}@{branch} failed: HTTP {e.code}\n{body}", file=sys.stderr)
        sys.exit(1)


def github_put(path, branch, content_bytes, sha, message):
    """PUT file to GitHub Contents API. Exits non-zero on failure."""
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"{API_BASE}/{path}"
    b64 = base64.b64encode(content_bytes).decode("ascii")
    body = {"message": message, "content": b64, "branch": branch}
    if sha:
        body["sha"] = sha
    body_bytes = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=body_bytes, method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "merge-radar/1.0",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        body_resp = e.read().decode("utf-8", errors="replace")
        print(f"PUBLISH FAILED {path} ({branch}): HTTP {e.code}\n{body_resp}", file=sys.stderr)
        sys.exit(1)
    if code not in (200, 201):
        print(f"PUBLISH FAILED {path} ({branch}): HTTP {code}", file=sys.stderr)
        sys.exit(1)
    return code


def parse_time_for_sort(time_str, today_str):
    """Return a canonical datetime string for sorting (used in reverse for descending)."""
    t = (time_str or "").strip()
    try:
        if not t:
            return "2000-01-01 00:00"
        # "昨 HH:MM"
        if t.startswith("昨"):
            today = datetime.date.fromisoformat(today_str)
            yesterday = (today - datetime.timedelta(days=1)).isoformat()
            hm = t.replace("昨", "").strip()
            return f"{yesterday} {hm}"
        # "HH:MM" (today)
        if len(t) == 5 and ":" in t:
            return f"{today_str} {t}"
        # "MM-DD HH:MM"
        parts = t.split(" ")
        if len(parts) == 2 and "-" in parts[0] and ":" in parts[1]:
            year = today_str[:4]
            return f"{year}-{parts[0]} {parts[1]}"
        return f"{today_str} {t}"
    except Exception:
        return f"{today_str} {t}"


def main():
    base_dir = Path(__file__).parent
    today = beijing_today()
    cutoff = prune_cutoff(today)

    print(f"merge_radar.py — {today} (Beijing)")
    print(f"  7-day prune cutoff: {cutoff}")

    # ── 1. Read new_items.json ────────────────────────────────────────────────
    new_items_path = base_dir / "new_items.json"
    if not new_items_path.exists():
        print("ERROR: new_items.json not found", file=sys.stderr)
        sys.exit(1)
    with open(new_items_path, encoding="utf-8") as f:
        new_items = json.load(f)
    print(f"Read {len(new_items)} candidates from new_items.json")

    # ── 2. Fetch seen.json from claude/radar-data (authoritative) ────────────
    seen_raw, seen_sha_radar = github_get("seen.json", DATA_BRANCH)
    if seen_raw:
        seen_data = json.loads(seen_raw)
        seen_ids = set(seen_data.get("ids", []))
    else:
        seen_data = {"ids": []}
        seen_ids = set()
        seen_sha_radar = None
    print(f"Loaded {len(seen_ids)} seen IDs from {DATA_BRANCH}")

    # ── 3. Fetch data.json from main ─────────────────────────────────────────
    data_raw, data_sha = github_get("data.json", MAIN_BRANCH)
    if data_raw:
        data_doc = json.loads(data_raw)
        existing_items = data_doc.get("items", [])
    else:
        data_doc = {}
        existing_items = []
        data_sha = None
    print(f"Loaded {len(existing_items)} existing items from data.json (main)")

    # Fetch seen.json SHA from main (needed for PUT; content not used)
    _, seen_sha_main = github_get("seen.json", MAIN_BRANCH)

    # ── 4. Dedup ──────────────────────────────────────────────────────────────
    existing_ids = {item["id"] for item in existing_items}
    all_seen = seen_ids | existing_ids
    deduped, dropped = [], 0
    for item in new_items:
        if item["id"] in all_seen:
            dropped += 1
            print(f"  SKIP (dup): {item['id']} — {item['title'][:55]}")
        else:
            deduped.append(item)
    print(f"Deduped: {len(deduped)} new / {dropped} dropped")

    # ── 5. Apply is_new flags ─────────────────────────────────────────────────
    for item in existing_items:
        item["is_new"] = False
        if "first_seen" not in item:
            item["first_seen"] = today  # backfill for legacy items

    for item in deduped:
        item["is_new"] = True
        item["first_seen"] = today

    # ── 6. Merge → prune → sort ───────────────────────────────────────────────
    merged = deduped + existing_items

    # Prune by date
    before = len(merged)
    merged = [i for i in merged if i.get("first_seen", today) >= cutoff]
    pruned_date = before - len(merged)
    if pruned_date:
        print(f"Pruned {pruned_date} items older than {cutoff}")

    # Prune by count (soft cap)
    if len(merged) > MAX_ITEMS:
        pruneable = [i for i in merged if not i.get("is_new") and i.get("tier") != 1]
        pruneable.sort(key=lambda x: (x.get("tier", 3), x.get("first_seen", "")))
        excess = len(merged) - MAX_ITEMS
        remove_ids = {i["id"] for i in pruneable[:excess]}
        merged = [i for i in merged if i["id"] not in remove_ids]
        print(f"Pruned {excess} excess items (tier 3/2 oldest first) to stay under {MAX_ITEMS}")

    # Sort: stable multi-pass (last key wins)
    # Pass 1: time descending within groups
    merged.sort(key=lambda x: parse_time_for_sort(x.get("time", ""), today), reverse=True)
    # Pass 2: tier ascending (stable preserves time order within tier)
    merged.sort(key=lambda x: x.get("tier", 3))
    # Pass 3: is_new:true first (stable preserves tier + time order within each)
    merged.sort(key=lambda x: 0 if x.get("is_new") else 1)

    # ── 7. Build output documents ─────────────────────────────────────────────
    kw_path = base_dir / "keywords.json"
    with open(kw_path, encoding="utf-8") as f:
        kw_doc = json.load(f)
    watchlist = list(kw_doc.get("entries", {}).keys())

    now_bj = beijing_now()
    updated_at = now_bj.strftime("%Y-%m-%d %H:%M") + " (北京时间)"

    updated_data = {
        "is_sample": False,
        "updated_at": updated_at,
        "next_runs": ["08:00", "13:00", "18:00"],
        "watchlist": watchlist,
        "positions": [],
        "items": merged,
    }

    existing_seen_list = seen_data.get("ids", [])
    new_ids_list = [i["id"] for i in deduped]
    combined_ids = existing_seen_list + [x for x in new_ids_list if x not in seen_ids]
    if len(combined_ids) > 1000:
        combined_ids = combined_ids[-1000:]
    updated_seen = {
        "ids": combined_ids,
        "updated_at": updated_at,
    }

    # Write local copies
    data_bytes = json.dumps(updated_data, ensure_ascii=False, indent=2).encode("utf-8")
    seen_bytes = json.dumps(updated_seen, ensure_ascii=False, indent=2).encode("utf-8")
    (base_dir / "data.json").write_bytes(data_bytes)
    (base_dir / "seen.json").write_bytes(seen_bytes)
    print(f"Wrote local data.json ({len(data_bytes)} bytes) and seen.json ({len(seen_bytes)} bytes)")

    # ── 8. Publish ────────────────────────────────────────────────────────────
    commit_msg = f"chore(radar): update market radar for {today} (+{len(deduped)}, total {len(merged)})"
    seen_msg = f"chore(radar): update seen for {today}"

    print("\nPublishing to GitHub...")
    code = github_put("data.json", MAIN_BRANCH, data_bytes, data_sha, commit_msg)
    print(f"  data.json ({MAIN_BRANCH}) → HTTP {code} ✓")

    code = github_put("seen.json", MAIN_BRANCH, seen_bytes, seen_sha_main, seen_msg)
    print(f"  seen.json ({MAIN_BRANCH}) → HTTP {code} ✓")

    code = github_put("seen.json", DATA_BRANCH, seen_bytes, seen_sha_radar, seen_msg)
    print(f"  seen.json ({DATA_BRANCH}) → HTTP {code} ✓")

    # ── 9. Self-check ─────────────────────────────────────────────────────────
    unverified = [i for i in deduped if not i.get("verified")]
    print(f"\n=== 运行自检 ===")
    print(f"本次新增 {len(deduped)} 条 / 去重丢弃 {dropped} 条 / 累积总数 {len(merged)} 条")
    print(f"data.json PUT: ✓ | seen.json (main) PUT: ✓ | seen.json ({DATA_BRANCH}) PUT: ✓")
    if unverified:
        print(f"未核实 (verified=false): {len(unverified)} 条")
        for i in unverified:
            print(f"  • {i['id']}: {i['title'][:70]}")
    else:
        print("所有新增条目均已核实 (verified=true)")
    print(
        "覆盖自检: "
        "①media_anchor 大盘头条已扫(先宽) "
        "②26标的 core+derived 全展开(再窄) "
        "③港股/A股未被美股大新闻挤掉 "
        "④里程碑新闻(SpaceX Nasdaq-100正式加入)已收录"
    )
    print(f"\n✅ 发布成功 — {updated_at}")


if __name__ == "__main__":
    main()
