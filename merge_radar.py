#!/usr/bin/env python3
"""
merge_radar.py — 合并 new_items.json 到 data.json，更新 seen.json，推送至 GitHub。
"""

import json
import os
import sys
import base64
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

REPO = "dzkeke-tech/market-radar"
RADAR_BRANCH = "claude/radar-data"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
MAX_ITEMS = 100  # 保留条目上限（按 tier 优先剪枝）
WORKDIR = os.path.dirname(os.path.abspath(__file__))

# 北京时间
BJT = timezone(timedelta(hours=8))


def now_bjt():
    return datetime.now(BJT).strftime("%Y-%m-%d %H:%M (北京时间)")


def github_get(path, ref=None):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    if ref:
        url += f"?ref={ref}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def github_put(path, content_str, message, branch, sha=None):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    body = {
        "message": message,
        "content": base64.b64encode(content_str.encode()).decode(),
        "branch": branch,
    }
    if sha:
        body["sha"] = sha
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"  wrote {path}")


def merge(data, new_items, seen_ids):
    """将 new_items 合并入 data['items']，返回实际新增数。"""
    existing_ids = {item["id"] for item in data.get("items", [])}
    added = 0
    timestamp = now_bjt()
    for item in new_items:
        if item["id"] in existing_ids or item["id"] in seen_ids:
            print(f"  skip (dup): {item['id']} {item.get('title','')[:60]}")
            continue
        item["is_new"] = True
        item["first_seen"] = timestamp
        data.setdefault("items", []).append(item)
        existing_ids.add(item["id"])
        seen_ids.add(item["id"])
        added += 1
        print(f"  +added tier{item.get('tier','?')}: {item.get('title','')[:70]}")
    return added


def prune(data):
    """按 tier 优先保留，超出 MAX_ITEMS 则剔除低优先条目。"""
    items = data.get("items", [])
    if len(items) <= MAX_ITEMS:
        return 0
    # 清除旧条目时先清 is_new 标记给低 tier 条目
    items.sort(key=lambda x: (x.get("tier", 9), x.get("first_seen", "")))
    removed = items[: len(items) - MAX_ITEMS]
    data["items"] = items[len(items) - MAX_ITEMS :]
    print(f"  pruned {len(removed)} items to stay under MAX_ITEMS={MAX_ITEMS}")
    return len(removed)


def reset_is_new(data):
    """把上一轮标记为 is_new=True 的条目改为 False（本轮新增除外）。"""
    new_ids = {item["id"] for item in data.get("items", []) if item.get("is_new")}
    for item in data.get("items", []):
        if item.get("is_new") and item["id"] not in new_ids:
            item["is_new"] = False


def main():
    print("=== merge_radar.py start ===")

    new_items_path = os.path.join(WORKDIR, "new_items.json")
    data_path = os.path.join(WORKDIR, "data.json")

    # 1. Load new_items.json
    if not os.path.exists(new_items_path):
        print("ERROR: new_items.json not found", file=sys.stderr)
        sys.exit(1)
    new_items = load_json(new_items_path)
    print(f"  new_items.json: {len(new_items)} candidate items")

    # 2. Load local data.json
    data = load_json(data_path)
    print(f"  data.json: {len(data.get('items', []))} existing items")

    # 3. Load seen.json — use remote radar-data branch as authority
    seen_remote = {}
    remote_file = github_get("seen.json", ref=RADAR_BRANCH)
    if remote_file:
        seen_remote = json.loads(base64.b64decode(remote_file["content"]).decode())
        print(f"  seen.json (remote): {len(seen_remote.get('ids', []))} ids, sha={remote_file['sha'][:8]}")
    else:
        print("  seen.json not found on remote — starting fresh")
    seen_ids = set(seen_remote.get("ids", []))

    # 4. Before merging, clear previous is_new flags
    for item in data.get("items", []):
        item["is_new"] = False

    # 5. Merge
    added = merge(data, new_items, seen_ids)
    print(f"  merged: +{added} new items")

    # 6. Update metadata
    data["updated_at"] = now_bjt()
    data["is_sample"] = False

    # 7. Prune
    prune(data)

    # 8. Save data.json locally
    save_json(data_path, data)

    # 9. Update seen.json — union of remote ids + new ids
    all_ids = sorted(seen_ids)
    seen_remote["ids"] = all_ids
    seen_str = json.dumps(seen_remote, ensure_ascii=False, indent=2)

    # Save locally too
    local_seen_path = os.path.join(WORKDIR, "seen.json")
    with open(local_seen_path, "w", encoding="utf-8") as f:
        f.write(seen_str)
    print(f"  updated local seen.json: {len(all_ids)} ids")

    # 10. Push seen.json to radar-data branch
    if GITHUB_TOKEN:
        try:
            result = github_put(
                "seen.json",
                seen_str,
                f"chore(seen): update seen.json — +{added} ids [{now_bjt()}]",
                RADAR_BRANCH,
                sha=remote_file["sha"] if remote_file else None,
            )
            print(f"  pushed seen.json to {RADAR_BRANCH}: {result['content']['sha'][:8]}")
        except Exception as e:
            print(f"  WARNING: failed to push seen.json to {RADAR_BRANCH}: {e}", file=sys.stderr)
    else:
        print("  WARNING: GITHUB_TOKEN not set, skipping remote seen.json push")

    # 11. Commit and push data.json + seen.json to working branch
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=WORKDIR).decode().strip()
    print(f"  working branch: {branch}")

    subprocess.run(["git", "add", "data.json", "seen.json"], cwd=WORKDIR, check=True)

    # Check if there are changes to commit
    status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=WORKDIR).returncode
    if status != 0:
        commit_msg = f"chore(radar): update market radar {now_bjt()} — +{added} new items"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=WORKDIR, check=True)
        print(f"  committed: {commit_msg}")

        # Push with retry
        for attempt in range(1, 5):
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=WORKDIR,
            )
            if result.returncode == 0:
                print(f"  pushed to origin/{branch}")
                break
            import time
            wait = 2 ** attempt
            print(f"  push failed (attempt {attempt}), retrying in {wait}s...")
            time.sleep(wait)
        else:
            print("ERROR: push failed after 4 attempts", file=sys.stderr)
            sys.exit(1)
    else:
        print("  no changes to commit (all items were duplicates)")

    print(f"=== merge_radar.py done: +{added} new / seen total {len(all_ids)} ===")
    return added


if __name__ == "__main__":
    added = main()
    sys.exit(0)
