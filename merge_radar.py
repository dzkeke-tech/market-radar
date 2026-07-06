#!/usr/bin/env python3
"""
merge_radar.py — merges new_items.json into data.json and seen.json on the
claude/radar-data GitHub branch.

Usage: python3 merge_radar.py
Requires: GITHUB_TOKEN env var with repo write access.
Exit 0 on success, non-zero on failure.
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
DATA_BRANCH = "claude/radar-data"
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_ITEMS_PATH = os.path.join(WORK_DIR, "new_items.json")

# Keep this many items in data.json (oldest are pruned)
MAX_ITEMS = 120

BJ = timezone(timedelta(hours=8))


def make_id(url: str, title: str = "") -> str:
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def now_bj() -> str:
    return datetime.now(BJ).strftime("%Y-%m-%d %H:%M (北京时间)")


def bj_date() -> str:
    return datetime.now(BJ).strftime("%Y-%m-%d")


def github_get(token: str, path: str, branch: str):
    """Fetch a file from GitHub; returns (content_bytes, sha)."""
    url = f"https://api.github.com/repos/{REPO}/contents/{path}?ref={branch}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
        content = base64.b64decode(body["content"])
        return content, body["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise


def github_put(token: str, path: str, branch: str, content_bytes: bytes,
               sha: str | None, message: str):
    """Create or update a file on GitHub."""
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode(),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def load_json_from_github(token, path, branch):
    raw, sha = github_get(token, path, branch)
    if raw is None:
        return None, None
    return json.loads(raw.decode("utf-8")), sha


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    # ── 1. Load new_items.json ──────────────────────────────────────────────
    if not os.path.exists(NEW_ITEMS_PATH):
        print(f"ERROR: {NEW_ITEMS_PATH} not found", file=sys.stderr)
        sys.exit(1)
    with open(NEW_ITEMS_PATH, encoding="utf-8") as f:
        new_items = json.load(f)
    if not isinstance(new_items, list):
        print("ERROR: new_items.json must be a JSON array", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(new_items)} new item(s) from new_items.json")

    # ── 2. Fetch data.json from claude/radar-data ───────────────────────────
    print(f"Fetching data.json from {DATA_BRANCH}…")
    data_obj, data_sha = load_json_from_github(token, "data.json", DATA_BRANCH)
    if data_obj is None:
        print("WARNING: data.json not found on branch, starting fresh")
        data_obj = {
            "is_sample": False,
            "updated_at": now_bj(),
            "items": [],
        }
        data_sha = None
    existing_items = data_obj.get("items", [])

    # ── 3. Fetch seen.json from claude/radar-data ───────────────────────────
    print(f"Fetching seen.json from {DATA_BRANCH}…")
    seen_obj, seen_sha = load_json_from_github(token, "seen.json", DATA_BRANCH)
    if seen_obj is None:
        seen_obj = {"ids": []}
        seen_sha = None
    seen_ids = set(seen_obj.get("ids", []))
    print(f"  {len(seen_ids)} IDs already in seen.json")

    # Also build existing ID set from data.json items for extra dedup safety
    existing_ids = {item.get("id") for item in existing_items if item.get("id")}

    # ── 4. Process new items ────────────────────────────────────────────────
    added, skipped = [], []
    today = bj_date()
    for item in new_items:
        url = item.get("url", "")
        title = item.get("title", "")
        item_id = item.get("id") or make_id(url, title)
        item["id"] = item_id

        if item_id in seen_ids or item_id in existing_ids:
            skipped.append(item_id)
            continue

        item["is_new"] = True
        if not item.get("first_seen"):
            item["first_seen"] = today
        added.append(item)

    print(f"  {len(added)} item(s) to add, {len(skipped)} already seen/present")

    # ── 5. Mark old is_new items as stale, prepend new ones ────────────────
    for item in existing_items:
        if item.get("is_new"):
            item["is_new"] = False

    merged_items = added + existing_items

    # Prune to MAX_ITEMS
    if len(merged_items) > MAX_ITEMS:
        merged_items = merged_items[:MAX_ITEMS]

    # ── 6. Update data.json ─────────────────────────────────────────────────
    data_obj["updated_at"] = now_bj()
    data_obj["items"] = merged_items

    # Update watchlist/positions arrays if present (keep as-is)
    data_bytes = json.dumps(data_obj, ensure_ascii=False, indent=2).encode("utf-8")

    # ── 7. Update seen.json ─────────────────────────────────────────────────
    new_seen_ids = list(seen_ids) + [item["id"] for item in added]
    # Keep last 512 to prevent unbounded growth
    if len(new_seen_ids) > 512:
        new_seen_ids = new_seen_ids[-512:]
    seen_obj["ids"] = new_seen_ids
    seen_bytes = json.dumps(seen_obj, ensure_ascii=False, indent=2).encode("utf-8")

    if not added:
        print("No new items to push — exiting cleanly.")
        sys.exit(0)

    # ── 8. Push to claude/radar-data ────────────────────────────────────────
    run_ts = now_bj()
    msg = f"radar: +{len(added)} items [{run_ts}]"

    print(f"Pushing data.json to {DATA_BRANCH}…")
    github_put(token, "data.json", DATA_BRANCH, data_bytes, data_sha, msg)

    print(f"Pushing seen.json to {DATA_BRANCH}…")
    github_put(token, "seen.json", DATA_BRANCH, seen_bytes, seen_sha, msg)

    # ── 9. Summary ─────────────────────────────────────────────────────────
    print("\n=== merge_radar.py complete ===")
    print(f"  Added  : {len(added)}")
    print(f"  Skipped: {len(skipped)}")
    print(f"  Total items in data.json: {len(merged_items)}")
    print(f"  seen.json IDs: {len(new_seen_ids)}")
    for item in added:
        flag = "✓ verified" if item.get("verified") else "? unverified"
        print(f"  + [{flag}] {item.get('id')} {item.get('title', '')[:70]}")
    sys.exit(0)


if __name__ == "__main__":
    main()
