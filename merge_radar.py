#!/usr/bin/env python3
"""merge_radar.py — merge new_items.json into data.json, update seen.json, push to main."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from itertools import groupby

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(REPO_DIR, "data.json")
SEEN_FILE = os.path.join(REPO_DIR, "seen.json")
NEW_ITEMS_FILE = os.path.join(REPO_DIR, "new_items.json")

MAX_ITEMS = 60
MAX_SEEN_IDS = 1000

BEIJING = timezone(timedelta(hours=8))
NOW_BEIJING = datetime.now(BEIJING).strftime("%Y-%m-%d %H:%M (北京时间)")


def git(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO_DIR)
    if check and r.returncode != 0:
        print(f"git error [{cmd}]:\n{r.stderr}", file=sys.stderr)
        sys.exit(1)
    return r.stdout.strip(), r.returncode


def main():
    # --- 1. Read all files into memory first (before any branch switching) ---
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    with open(SEEN_FILE, encoding="utf-8") as f:
        seen = json.load(f)

    if not os.path.exists(NEW_ITEMS_FILE):
        print("new_items.json not found — nothing to merge.")
        sys.exit(0)

    with open(NEW_ITEMS_FILE, encoding="utf-8") as f:
        new_items = json.load(f)

    # --- 2. Build ID sets ---
    seen_ids = set(seen.get("ids", []))
    existing_ids = {item["id"] for item in data.get("items", [])}

    # --- 3. Deduplicate and merge new items ---
    added = 0
    skipped_seen = 0
    skipped_dupe = 0

    for item in new_items:
        item_id = item["id"]
        if item_id in seen_ids:
            skipped_seen += 1
            continue
        if item_id in existing_ids:
            skipped_dupe += 1
            continue
        item["is_new"] = True
        item["first_seen"] = NOW_BEIJING
        data["items"].append(item)
        seen_ids.add(item_id)
        existing_ids.add(item_id)
        added += 1

    # --- 4. Mark previously-new items as no longer new ---
    new_ids_this_run = {item["id"] for item in new_items}
    for item in data["items"]:
        if item["id"] not in new_ids_this_run:
            item["is_new"] = False

    # --- 5. Sort: tier asc, within tier newest first ---
    def sort_key(item):
        return (item.get("tier", 3), item.get("first_seen", "2000") or "2000")

    items_by_tier = {}
    for item in data["items"]:
        t = item.get("tier", 3)
        items_by_tier.setdefault(t, []).append(item)

    sorted_items = []
    for t in sorted(items_by_tier.keys()):
        group = sorted(items_by_tier[t], key=lambda x: x.get("first_seen", "2000") or "2000", reverse=True)
        sorted_items.extend(group)

    data["items"] = sorted_items

    # --- 6. Prune to MAX_ITEMS (drop oldest tier 3 first, then tier 2) ---
    if len(data["items"]) > MAX_ITEMS:
        tier1 = [i for i in data["items"] if i.get("tier") == 1]
        tier2 = [i for i in data["items"] if i.get("tier") == 2]
        tier3 = [i for i in data["items"] if i.get("tier") == 3]
        data["items"] = (tier1 + tier2 + tier3)[:MAX_ITEMS]

    # --- 7. Update metadata ---
    data["updated_at"] = NOW_BEIJING

    # --- 8. Update seen.json ---
    all_ids = list(seen_ids | {item["id"] for item in data["items"]})
    if len(all_ids) > MAX_SEEN_IDS:
        all_ids = all_ids[-MAX_SEEN_IDS:]
    seen["ids"] = sorted(all_ids)
    seen["updated_at"] = NOW_BEIJING

    # --- 9. Switch to main, write, commit, push ---
    current_branch, _ = git("git rev-parse --abbrev-ref HEAD")

    git("git fetch origin main")

    if current_branch != "main":
        git("git checkout main")
        git("git pull origin main --ff-only")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)

    git("git add data.json seen.json")

    # Check if there are staged changes
    _, rc = git("git diff --cached --quiet", check=False)
    if rc == 0:
        print(f"No file changes detected. added={added}, skipped_seen={skipped_seen}, skipped_dupe={skipped_dupe}")
    else:
        commit_msg = f"radar {NOW_BEIJING}"
        git(f'git commit -m "{commit_msg}"')
        git("git push -u origin main")
        print(f"✓ Pushed to main: added={added}, skipped={skipped_seen+skipped_dupe}, "
              f"total_items={len(data['items'])}, updated_at={NOW_BEIJING}")

    # --- 10. Return to development branch ---
    if current_branch != "main":
        git(f"git checkout {current_branch}")

    print(f"自检: 本次新增 {added} 条 / 去重丢弃 {skipped_seen+skipped_dupe} 条 / "
          f"总条目 {len(data['items'])} / "
          f"verified=false 条目: {sum(1 for i in data['items'] if not i.get('verified', True))}")


if __name__ == "__main__":
    main()
