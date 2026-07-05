#!/usr/bin/env python3
"""
merge_radar.py — merges new_items.json into data.json and pushes to GitHub.
Usage: python3 merge_radar.py
Exit 0 on success, non-zero on failure.
"""

import json
import os
import sys
import subprocess
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

REPO = "dzkeke-tech/market-radar"
DATA_BRANCH = "claude/radar-data"
WORK_BRANCH = "claude/nice-mayer-blaefj"
DATA_FILE = "data.json"
SEEN_FILE = "seen.json"
NEW_ITEMS_FILE = "new_items.json"
PRUNE_DAYS = 7

TZ_BJ = timezone(timedelta(hours=8))

def github_api(path, method="GET", body=None):
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp), resp.status
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode()
        print(f"[github_api] HTTP {e.code} {method} {path}: {body_txt[:300]}", file=sys.stderr)
        return None, e.code

def get_file_from_branch(path, branch):
    resp, status = github_api(f"/repos/{REPO}/contents/{path}?ref={branch}")
    if status != 200 or not resp:
        return None, None
    content = base64.b64decode(resp["content"]).decode("utf-8")
    return content, resp.get("sha")

def put_file_to_branch(path, branch, content_str, sha, message):
    encoded = base64.b64encode(content_str.encode("utf-8")).decode()
    body = {"message": message, "content": encoded, "branch": branch}
    if sha:
        body["sha"] = sha
    resp, status = github_api(f"/repos/{REPO}/contents/{path}", method="PUT", body=body)
    return status in (200, 201)

def now_bj():
    return datetime.now(TZ_BJ)

def date_str():
    return now_bj().strftime("%Y-%m-%d")

def time_to_iso(time_str):
    """Convert HH:MM to full ISO 8601 Beijing time string."""
    now = now_bj()
    try:
        h, m = map(int, time_str.split(":"))
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
    except Exception:
        dt = now
    return dt.isoformat()

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_file(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def prune_items(items, days=PRUNE_DAYS):
    cutoff = now_bj() - timedelta(days=days)
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    kept = []
    for item in items:
        fs = item.get("first_seen", "")
        # Keep if first_seen is within window (compare as strings, ISO format sorts correctly)
        if fs >= cutoff_str:
            kept.append(item)
    return kept

def main():
    # 1. Load new items
    if not os.path.exists(NEW_ITEMS_FILE):
        print(f"[merge] {NEW_ITEMS_FILE} not found — nothing to merge.", file=sys.stderr)
        sys.exit(1)

    new_items = load_json_file(NEW_ITEMS_FILE)
    if not isinstance(new_items, list):
        print("[merge] new_items.json must be a list.", file=sys.stderr)
        sys.exit(1)

    print(f"[merge] Loaded {len(new_items)} new items from {NEW_ITEMS_FILE}")

    # 2. Load existing data.json
    data = load_json_file(DATA_FILE)
    existing_items = data.get("items", [])
    existing_ids = {item["id"] for item in existing_items}

    # 3. Load seen IDs from /tmp/seen.json (already fetched by the caller)
    seen_path = "/tmp/seen.json"
    if os.path.exists(seen_path):
        seen_data = load_json_file(seen_path)
    else:
        seen_data = {"ids": []}
    seen_ids = set(seen_data.get("ids", []))

    # 4. Validate and enrich new items
    today = date_str()
    accepted = []
    skipped_dup = 0
    for item in new_items:
        iid = item.get("id", "")
        if not iid:
            continue
        if iid in seen_ids or iid in existing_ids:
            skipped_dup += 1
            continue
        # Enrich
        item["is_new"] = True
        item["first_seen"] = today
        # Convert time HH:MM -> ISO if needed
        raw_time = item.get("time", "")
        if raw_time and len(raw_time) <= 5 and ":" in raw_time:
            item["time"] = time_to_iso(raw_time)
        elif not raw_time:
            item["time"] = now_bj().isoformat()
        accepted.append(item)

    print(f"[merge] Accepted {len(accepted)}, skipped {skipped_dup} duplicates")

    # 5. Reset is_new on all old items
    for item in existing_items:
        item["is_new"] = False

    # 6. Merge: new items first, then existing
    merged = accepted + existing_items

    # 7. Prune
    before_prune = len(merged)
    merged = prune_items(merged)
    print(f"[merge] Pruned {before_prune - len(merged)} old items; {len(merged)} remaining")

    # 8. Update data
    now_str = now_bj().strftime("%Y-%m-%d %H:%M") + " (北京时间)"
    data["items"] = merged
    data["updated_at"] = now_str
    data["is_sample"] = False

    # 9. Write data.json locally
    save_json_file(DATA_FILE, data)
    print(f"[merge] Wrote {DATA_FILE} locally")

    # 10. Update seen.json on GitHub (claude/radar-data branch)
    _, seen_sha = get_file_from_branch(SEEN_FILE, DATA_BRANCH)
    all_new_ids = [item["id"] for item in accepted]
    updated_seen_ids = list(seen_ids | set(all_new_ids))
    # Keep seen list bounded to last 2000 IDs
    if len(updated_seen_ids) > 2000:
        updated_seen_ids = updated_seen_ids[-2000:]
    new_seen = {"ids": updated_seen_ids}
    seen_ok = put_file_to_branch(
        SEEN_FILE, DATA_BRANCH,
        json.dumps(new_seen, ensure_ascii=False, indent=2),
        seen_sha,
        f"chore(seen): add {len(all_new_ids)} new IDs [{today}]"
    )
    if seen_ok:
        print(f"[merge] Updated {SEEN_FILE} on {DATA_BRANCH} (+{len(all_new_ids)} IDs)")
    else:
        print(f"[merge] WARNING: failed to update {SEEN_FILE} on {DATA_BRANCH}", file=sys.stderr)

    # 11. Commit and push data.json on working branch
    n = len(accepted)
    headlines = [i["title"][:20] for i in accepted[:5]]
    short_list = "/".join(headlines)
    commit_msg = f"chore(radar): update market radar {now_str} (+{n} new: {short_list})"

    def run(cmd, check=True):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"[git] ERROR: {cmd}\n{result.stderr}", file=sys.stderr)
            sys.exit(result.returncode)
        return result

    run("git add data.json")
    run(f'git commit -m "{commit_msg}"')

    # Push with retry
    for attempt, wait in enumerate([0, 2, 4, 8, 16]):
        if wait:
            import time
            time.sleep(wait)
        result = run(f"git push -u origin {WORK_BRANCH}", check=False)
        if result.returncode == 0:
            print(f"[merge] Pushed to {WORK_BRANCH}")
            break
        if attempt == 4:
            print(f"[merge] Push failed after retries:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)

    print(f"[merge] Done. {n} new items published. seen total: {len(updated_seen_ids)}")
    sys.exit(0)

if __name__ == "__main__":
    main()
