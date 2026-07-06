#!/usr/bin/env python3
"""
merge_radar.py — merges new_items.json → data.json (main) + seen.json (claude/radar-data).

Usage:  python3 merge_radar.py
Reads : new_items.json (local, written by gen_items.py)
Writes: data.json (local + push to main), seen.json (local + push to claude/radar-data)
"""

import base64
import json
import os
import sys
from urllib import request as urllib_request

OWNER       = "dzkeke-tech"
REPO        = "market-radar"
DATA_BRANCH = "main"
SEEN_BRANCH = "claude/radar-data"
DATA_PATH   = "data.json"
SEEN_PATH   = "seen.json"
TODAY       = "2026-07-06"
NOW_STR     = "2026-07-06 13:00 (北京时间)"
PRUNE_KEEP  = 100   # rolling window; keeps ~5-6 days of 3x-daily runs


# ── GitHub helpers ─────────────────────────────────────────────────────────────

def _gh_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }


def gh_get_file(token, path, branch):
    """Fetch a JSON file from GitHub; return (parsed_obj, sha)."""
    url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
        f"?ref={branch}"
    )
    req = urllib_request.Request(url, headers=_gh_headers(token))
    with urllib_request.urlopen(req) as resp:
        meta = json.loads(resp.read())
    content = base64.b64decode(meta["content"]).decode("utf-8")
    return json.loads(content), meta["sha"]


def gh_push_file(token, path, branch, content_str, sha, message):
    """Update a file on GitHub."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    payload = json.dumps({
        "message": message,
        "content": base64.b64encode(content_str.encode("utf-8")).decode(),
        "sha": sha,
        "branch": branch,
    }).encode("utf-8")
    req = urllib_request.Request(
        url, data=payload, method="PUT", headers=_gh_headers(token)
    )
    with urllib_request.urlopen(req) as resp:
        return json.loads(resp.read())


# ── Time normalisation ─────────────────────────────────────────────────────────

def normalise_time(t):
    """Convert bare 'HH:MM' to full ISO-8601+08:00; pass through if already ISO."""
    if t and "T" in str(t):
        return t
    hhmm = str(t).strip() if t else "00:00"
    if len(hhmm) == 5 and hhmm[2] == ":":
        return f"{TODAY}T{hhmm}:00+08:00"
    return hhmm  # unknown format — keep as-is


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("ERROR: GITHUB_TOKEN not set.", file=sys.stderr)
        sys.exit(1)

    # 1. Load new items
    with open("new_items.json", encoding="utf-8") as f:
        new_items = json.load(f)

    if not new_items:
        print("No new items — nothing to merge.")
        return

    print(f"New items to merge: {len(new_items)}")

    # 2. Fetch authoritative copies from GitHub (also gets SHAs for update)
    print(f"Fetching {DATA_PATH} from {DATA_BRANCH}...")
    data_obj, data_sha = gh_get_file(token, DATA_PATH, DATA_BRANCH)

    print(f"Fetching {SEEN_PATH} from {SEEN_BRANCH}...")
    seen_obj, seen_sha = gh_get_file(token, SEEN_PATH, SEEN_BRANCH)

    # 3. Mark existing items as not-new
    for item in data_obj.get("items", []):
        item["is_new"] = False

    # 4. Annotate and normalise new items
    existing_seen = set(seen_obj.get("ids", []))
    prepared = []
    for item in new_items:
        item["is_new"] = True
        item["first_seen"] = TODAY
        item["time"] = normalise_time(item.get("time"))
        prepared.append(item)

    # 5. Merge: new items first, then existing history
    data_obj["items"] = prepared + data_obj.get("items", [])

    # 6. Prune to rolling window
    data_obj["items"] = data_obj["items"][:PRUNE_KEEP]

    # 7. Update data.json metadata
    data_obj["updated_at"] = NOW_STR

    # 8. Update seen.json — append only truly new IDs
    added_ids = [it["id"] for it in prepared if it["id"] not in existing_seen]
    seen_obj["ids"] = seen_obj.get("ids", []) + added_ids
    seen_obj["updated_at"] = NOW_STR

    # 9. Serialise
    data_str = json.dumps(data_obj, ensure_ascii=False, indent=2)
    seen_str = json.dumps(seen_obj, ensure_ascii=False, indent=2)

    # 10. Write locally
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(data_str)
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        f.write(seen_str)
    print("Local files updated.")

    # 11. Build commit messages
    titles_preview = "/".join(it["title"][:25] for it in prepared[:3])
    msg_data = (
        f"chore(radar): update market radar {NOW_STR}"
        f" — {len(prepared)} new ({titles_preview})"
    )
    msg_seen = f"chore(radar): update seen.json {NOW_STR} — {len(added_ids)} new IDs"

    # 12. Push data.json → main
    print(f"Pushing {DATA_PATH} → {DATA_BRANCH}...")
    gh_push_file(token, DATA_PATH, DATA_BRANCH, data_str, data_sha, msg_data)
    print(f"  {DATA_PATH} pushed.")

    # 13. Push seen.json → claude/radar-data
    print(f"Pushing {SEEN_PATH} → {SEEN_BRANCH}...")
    gh_push_file(token, SEEN_PATH, SEEN_BRANCH, seen_str, seen_sha, msg_seen)
    print(f"  {SEEN_PATH} pushed.")

    # 14. Summary
    print(f"\nMerge complete — {len(prepared)} added, {len(data_obj['items'])} total items.")
    for it in prepared:
        print(f"  + {it['id']} | T{it['tier']} | {it['title'][:65]}")


if __name__ == "__main__":
    main()
