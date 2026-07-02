#!/usr/bin/env python3
"""merge_radar.py — merge new_items.json into data.json, update seen.json, commit & push."""

import json, os, subprocess, sys, time
from datetime import datetime, timezone, timedelta

KEEP_MAX = 45   # max items kept in data.json
SEEN_MAX = 600  # max IDs kept in seen.json

REPO = os.path.dirname(os.path.abspath(__file__))


def beijing_now():
    bj = timezone(timedelta(hours=8))
    return datetime.now(bj).strftime("%Y-%m-%d %H:%M (北京时间)")


def today_date():
    bj = timezone(timedelta(hours=8))
    return datetime.now(bj).strftime("%Y-%m-%d")


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    if check and result.returncode != 0:
        print(f"ERROR: {cmd}\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def current_branch():
    return run("git branch --show-current")


def main():
    # ── 1. Load new_items.json ────────────────────────────────────────────────
    new_path = os.path.join(REPO, "new_items.json")
    if not os.path.exists(new_path):
        print("ERROR: new_items.json not found.", file=sys.stderr)
        sys.exit(1)
    with open(new_path, encoding="utf-8") as f:
        new_items = json.load(f)
    print(f"[merge] new_items: {len(new_items)}")

    # ── 2. Load data.json ─────────────────────────────────────────────────────
    data_path = os.path.join(REPO, "data.json")
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    old_items = data.get("items", [])
    print(f"[merge] existing items: {len(old_items)}")

    # ── 3. Load seen.json ─────────────────────────────────────────────────────
    seen_path = os.path.join(REPO, "seen.json")
    with open(seen_path, encoding="utf-8") as f:
        seen_data = json.load(f)
    seen_ids = set(seen_data.get("ids", []))

    # ── 4. Annotate new items ─────────────────────────────────────────────────
    today = today_date()
    new_id_set = {item["id"] for item in new_items}
    for item in new_items:
        item["is_new"] = True
        item.setdefault("first_seen", today)

    # ── 5. Mark old items as not new ──────────────────────────────────────────
    for item in old_items:
        item["is_new"] = False

    # ── 6. Merge: new on top, deduplicate by id ───────────────────────────────
    seen_in_merge = set()
    merged = []
    for item in new_items + old_items:
        if item["id"] not in seen_in_merge:
            seen_in_merge.add(item["id"])
            merged.append(item)

    # ── 7. Sort: tier asc, 大盘头条 before 个股 ──────────────────────────────
    def sort_key(item):
        group_order = 0 if item.get("group") == "大盘头条" else 1
        return (item.get("tier", 3), group_order)

    new_sorted = sorted([i for i in merged if i.get("is_new")], key=sort_key)
    old_sorted = sorted([i for i in merged if not i.get("is_new")], key=sort_key)
    final_items = new_sorted + old_sorted

    # ── 8. Prune to KEEP_MAX ──────────────────────────────────────────────────
    if len(final_items) > KEEP_MAX:
        final_items = final_items[:KEEP_MAX]
    print(f"[merge] after merge+prune: {len(final_items)} items")

    # ── 9. Write data.json ────────────────────────────────────────────────────
    data["updated_at"] = beijing_now()
    data["next_runs"] = ["08:00", "13:00", "18:00"]
    data["is_sample"] = False
    data["items"] = final_items
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[merge] data.json written.")

    # ── 10. Update seen.json ──────────────────────────────────────────────────
    all_seen = sorted(seen_ids | new_id_set)
    if len(all_seen) > SEEN_MAX:
        all_seen = all_seen[-SEEN_MAX:]
    seen_data["ids"] = all_seen
    seen_data["updated_at"] = beijing_now()
    with open(seen_path, "w", encoding="utf-8") as f:
        json.dump(seen_data, f, ensure_ascii=False, indent=2)
    print("[merge] seen.json written.")

    # ── 11. Git commit & push ─────────────────────────────────────────────────
    n = len(new_items)
    preview = ", ".join(i["title"][:28] for i in new_items[:4])
    commit_msg = f"chore(radar): update market radar for {today} (+{n}: {preview}...)"

    run("git add data.json seen.json new_items.json")
    run(f'git commit -m "{commit_msg}"')

    branch = current_branch()
    for attempt in range(4):
        result = subprocess.run(
            f"git push -u origin {branch}",
            shell=True, capture_output=True, text=True, cwd=REPO
        )
        if result.returncode == 0:
            print(f"[merge] pushed to origin/{branch}.")
            break
        wait = 2 ** (attempt + 1)
        print(f"[merge] push failed (attempt {attempt+1}), retry in {wait}s...")
        time.sleep(wait)
    else:
        print("[merge] push failed after 4 attempts.", file=sys.stderr)
        sys.exit(1)

    print(f"[merge] done. +{n} new items published.")


if __name__ == "__main__":
    main()
