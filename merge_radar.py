#!/usr/bin/env python3
"""
merge_radar.py — merge new_items.json into data.json, update seen.json, push to GitHub.

Usage:  python3 merge_radar.py
Exit 0 = success, non-zero = failure.
"""

import json
import os
import sys
import subprocess
import hashlib
from datetime import datetime, timezone, timedelta


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(REPO_ROOT, "data.json")
SEEN_FILE = os.path.join(REPO_ROOT, "seen.json")
NEW_FILE  = os.path.join(REPO_ROOT, "new_items.json")

MAX_ITEMS = 60      # keep latest N items in data.json
BEIJING   = timezone(timedelta(hours=8))


def now_beijing() -> str:
    return datetime.now(BEIJING).strftime("%Y-%m-%d %H:%M (北京时间)")


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"  wrote {path}")


def make_id(url_or_title: str) -> str:
    return hashlib.sha1((url_or_title or "").strip().encode()).hexdigest()[:16]


def run_git(*args) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", REPO_ROOT] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  git {' '.join(args)} FAILED:\n{result.stderr}", file=sys.stderr)
    return result


def push_to_github(branch: str = "main") -> bool:
    """Commit data.json + seen.json and push to origin/<branch>."""
    ts = now_beijing()

    run_git("config", "user.email", "radar-bot@market-radar.local")
    run_git("config", "user.name",  "Market Radar Bot")

    # Make sure we're on the right branch
    current = run_git("rev-parse", "--abbrev-ref", "HEAD")
    current_branch = current.stdout.strip()

    if current_branch != branch:
        print(f"  current branch: {current_branch}, switching to {branch}")
        r = run_git("checkout", branch)
        if r.returncode != 0:
            # Try fetching and checking out
            run_git("fetch", "origin", branch)
            r = run_git("checkout", "-B", branch, f"origin/{branch}")
            if r.returncode != 0:
                print(f"  could not checkout {branch}", file=sys.stderr)
                return False

    run_git("add", DATA_FILE, SEEN_FILE)

    status = run_git("status", "--porcelain")
    if not status.stdout.strip():
        print("  nothing to commit — data unchanged")
        return True

    msg = f"radar {ts}"
    r = run_git("commit", "-m", msg)
    if r.returncode != 0:
        print(f"  commit failed: {r.stderr}", file=sys.stderr)
        return False

    # Push with retry (exponential back-off)
    import time
    delays = [2, 4, 8, 16]
    for attempt, delay in enumerate(delays, 1):
        r = run_git("push", "-u", "origin", branch)
        if r.returncode == 0:
            print(f"  pushed to origin/{branch}")
            return True
        print(f"  push attempt {attempt} failed, retrying in {delay}s…")
        time.sleep(delay)

    print("  all push attempts failed", file=sys.stderr)
    return False


def main() -> int:
    # ── 1. Load existing data ──────────────────────────────────────────────
    data = load_json(DATA_FILE)
    seen = load_json(SEEN_FILE)

    existing_ids: set = {item["id"] for item in data.get("items", [])}
    seen_ids: set     = set(seen.get("ids", []))

    # ── 2. Load new items ──────────────────────────────────────────────────
    if not os.path.exists(NEW_FILE):
        print(f"ERROR: {NEW_FILE} not found", file=sys.stderr)
        return 1

    new_items = load_json(NEW_FILE)
    if not isinstance(new_items, list):
        print("ERROR: new_items.json must be a JSON array", file=sys.stderr)
        return 1

    # ── 3. Deduplicate & merge ─────────────────────────────────────────────
    added = []
    skipped_dup = 0

    for item in new_items:
        # Ensure id is set
        if not item.get("id"):
            item["id"] = make_id(item.get("url") or item.get("title") or "")

        uid = item["id"]
        if uid in existing_ids:
            skipped_dup += 1
            print(f"  skip (in data)  {uid}  {item.get('title', '')[:50]}")
            continue

        # Allow items in seen.json that are NOT in data.json (previous failed runs)
        existing_ids.add(uid)
        seen_ids.add(uid)
        added.append(item)
        print(f"  add             {uid}  {item.get('title', '')[:50]}")

    # ── 4. Mark previous is_new items as old ──────────────────────────────
    for item in data["items"]:
        item["is_new"] = False

    # ── 5. Prepend new items ───────────────────────────────────────────────
    data["items"] = added + data["items"]

    # ── 6. Prune to MAX_ITEMS ──────────────────────────────────────────────
    if len(data["items"]) > MAX_ITEMS:
        pruned = data["items"][MAX_ITEMS:]
        data["items"] = data["items"][:MAX_ITEMS]
        for p in pruned:
            seen_ids.discard(p["id"])
        print(f"  pruned {len(pruned)} oldest items")

    # ── 7. Update timestamps ───────────────────────────────────────────────
    ts = now_beijing()
    data["updated_at"] = ts
    seen["updated_at"] = ts
    seen["ids"] = sorted(seen_ids)

    # ── 8. Save locally ────────────────────────────────────────────────────
    save_json(DATA_FILE, data)
    save_json(SEEN_FILE, seen)

    print(f"\n  merged: +{len(added)} new, {skipped_dup} skipped (dup), {len(data['items'])} total")

    # ── 9. Push to GitHub ──────────────────────────────────────────────────
    ok = push_to_github(branch="main")
    if not ok:
        print("ERROR: push failed", file=sys.stderr)
        return 1

    print(f"\n✓ done — {len(added)} items published, updated_at={ts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
