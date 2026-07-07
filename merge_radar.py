#!/usr/bin/env python3
"""Merge new_items.json into data.json, update seen.json, commit and push."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

REPO = "/home/user/market-radar"
DATA_FILE = os.path.join(REPO, "data.json")
SEEN_FILE = os.path.join(REPO, "seen.json")
NEW_FILE = os.path.join(REPO, "new_items.json")
MAX_ITEMS = 150

BEIJING = timezone(timedelta(hours=8))


def beijing_now():
    return datetime.now(BEIJING)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"  Written: {path}")


def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, **kwargs)
    if result.returncode != 0:
        print(f"  [ERROR] {' '.join(cmd)}\n  stdout: {result.stdout}\n  stderr: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def main():
    now = beijing_now()
    today_str = now.strftime("%Y-%m-%d")
    updated_at = now.strftime("%Y-%m-%d %H:%M") + " (北京时间)"

    print(f"[merge_radar] {updated_at}")

    # Load files
    new_items = load_json(NEW_FILE)
    data = load_json(DATA_FILE)
    seen = load_json(SEEN_FILE)

    seen_ids = set(seen.get("ids", []))
    existing_items = data.get("items", [])

    # Filter truly new items
    fresh = [it for it in new_items if it["id"] not in seen_ids]
    print(f"  New items in file: {len(new_items)}, after dedup: {len(fresh)}")

    if not fresh:
        print("  Nothing new — skipping commit.")
        return

    # Tag new items
    for it in fresh:
        it["is_new"] = True
        it["first_seen"] = today_str

    # Clear is_new on existing items
    for it in existing_items:
        it["is_new"] = False

    # Sort fresh by tier then time
    fresh_sorted = sorted(fresh, key=lambda x: (x.get("tier", 9), x.get("time", "")))

    # Prepend fresh, then existing, prune to MAX_ITEMS
    merged = (fresh_sorted + existing_items)[:MAX_ITEMS]

    # Update data.json
    data["items"] = merged
    data["updated_at"] = updated_at
    save_json(DATA_FILE, data)

    # Update seen.json
    new_ids = [it["id"] for it in fresh]
    seen["ids"] = list(seen_ids) + new_ids
    seen["updated_at"] = updated_at
    save_json(SEEN_FILE, seen)

    # Git operations
    print("  Staging files...")
    run(["git", "add", "data.json", "seen.json"])

    msg = f"radar: 13:00 batch — {len(fresh)} new items ({today_str})"
    print(f"  Committing: {msg}")
    run(["git", "commit", "-m", msg])

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    print(f"  Current branch: {branch}")

    print(f"  Pushing to origin/{branch}...")
    run(["git", "push", "-u", "origin", branch])

    print("  Pushing to origin/main...")
    run(["git", "push", "origin", f"HEAD:main"])

    print(f"[merge_radar] Done. {len(fresh)} items published.")


if __name__ == "__main__":
    main()
