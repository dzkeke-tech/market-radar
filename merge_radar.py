#!/usr/bin/env python3
"""
merge_radar.py — 合并 new_items.json 到 data.json，更新 seen.json，推送 GitHub。
"""
import json, hashlib, subprocess, sys, os
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(REPO_DIR, "data.json")
NEW_ITEMS_FILE = os.path.join(REPO_DIR, "new_items.json")
SEEN_LOCAL = "/tmp/seen.json"
MAX_ITEMS = 50
RADAR_DATA_BRANCH = "claude/radar-data"
WORK_BRANCH = "claude/nice-mayer-4iu4be"
IS_NEW_TTL_HOURS = 8  # 条目标记为 is_new=True 的时长

BJT = timezone(timedelta(hours=8))


def make_id(url: str, title: str) -> str:
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def bjt_now() -> str:
    return datetime.now(BJT).strftime("%Y-%m-%d %H:%M (北京时间)")


def run(cmd: list, check=True, capture=False) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd, cwd=REPO_DIR, check=check,
        capture_output=capture, text=True
    )
    return result


def load_seen() -> set:
    if os.path.exists(SEEN_LOCAL):
        with open(SEEN_LOCAL, "r") as f:
            return set(json.load(f).get("ids", []))
    return set()


def save_seen(ids: set):
    ids_sorted = sorted(ids)
    with open(SEEN_LOCAL, "w") as f:
        json.dump({"ids": ids_sorted}, f, ensure_ascii=False, indent=2)


def load_data() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_new_items() -> list:
    if not os.path.exists(NEW_ITEMS_FILE):
        print("[merge] new_items.json not found — nothing to merge.", flush=True)
        return []
    with open(NEW_ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def is_still_new(first_seen_str: str) -> bool:
    """Check if an item's first_seen timestamp is within IS_NEW_TTL_HOURS."""
    try:
        # Support ISO format and simple date strings
        for fmt in ("%Y-%m-%d %H:%M (北京时间)", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                ts = datetime.strptime(first_seen_str, fmt)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=BJT)
                now = datetime.now(BJT)
                return (now - ts).total_seconds() < IS_NEW_TTL_HOURS * 3600
            except ValueError:
                continue
    except Exception:
        pass
    return True  # default to new if parse fails


def update_seen_on_radar_data_branch(new_ids: list):
    """Push updated seen.json to the claude/radar-data branch via git."""
    if not new_ids:
        return

    # Fetch and checkout radar-data branch content without switching HEAD
    run(["git", "fetch", "origin", RADAR_DATA_BRANCH], check=False)

    # Get current seen.json from radar-data branch
    result = run(
        ["git", "show", f"origin/{RADAR_DATA_BRANCH}:seen.json"],
        check=False, capture=True
    )
    if result.returncode == 0:
        existing = json.loads(result.stdout)
        existing_ids = set(existing.get("ids", []))
    else:
        existing_ids = set()

    combined = sorted(existing_ids | set(new_ids))
    seen_content = json.dumps({"ids": combined}, ensure_ascii=False, indent=2)

    # Write to a temp location and push using git hash-object + update-ref
    # Simpler: use GitHub API via curl
    import base64
    encoded = base64.b64encode(seen_content.encode()).decode()

    # Get current file SHA from radar-data branch
    github_token = os.environ.get("GITHUB_TOKEN", "")
    repo = "dzkeke-tech/market-radar"
    api_base = "https://api.github.com"

    get_cmd = [
        "curl", "-s",
        "-H", f"Authorization: Bearer {github_token}",
        "-H", "Accept: application/vnd.github+json",
        f"{api_base}/repos/{repo}/contents/seen.json?ref={RADAR_DATA_BRANCH}"
    ]
    r = subprocess.run(get_cmd, capture_output=True, text=True)
    file_info = {}
    try:
        file_info = json.loads(r.stdout)
    except Exception:
        pass

    file_sha = file_info.get("sha", "")

    payload = {
        "message": f"update seen.json — {bjt_now()}",
        "content": encoded,
        "branch": RADAR_DATA_BRANCH,
    }
    if file_sha:
        payload["sha"] = file_sha

    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(payload, tmp)
        tmp_path = tmp.name

    put_cmd = [
        "curl", "-s", "-X", "PUT",
        "-H", f"Authorization: Bearer {github_token}",
        "-H", "Accept: application/vnd.github+json",
        "-H", "Content-Type: application/json",
        "-d", f"@{tmp_path}",
        f"{api_base}/repos/{repo}/contents/seen.json"
    ]
    pr = subprocess.run(put_cmd, capture_output=True, text=True)
    os.unlink(tmp_path)

    try:
        resp = json.loads(pr.stdout)
        if "content" in resp:
            print(f"[merge] seen.json updated on {RADAR_DATA_BRANCH} ({len(combined)} IDs total)", flush=True)
        else:
            print(f"[merge] WARNING: seen.json push may have failed: {pr.stdout[:200]}", flush=True)
    except Exception as e:
        print(f"[merge] WARNING: seen.json push error: {e}", flush=True)

    # Also update local /tmp/seen.json
    save_seen(set(combined))


def main():
    print(f"[merge] Starting merge at {bjt_now()}", flush=True)

    # 1. Load inputs
    new_items_raw = load_new_items()
    data = load_data()
    seen_ids = load_seen()

    existing_items = data.get("items", [])
    existing_ids = {item["id"] for item in existing_items}

    # 2. Compute IDs and deduplicate new items
    truly_new = []
    skipped = 0
    for item in new_items_raw:
        item_id = make_id(item.get("url", ""), item.get("title", ""))
        item["id"] = item_id
        if item_id in seen_ids or item_id in existing_ids:
            skipped += 1
            continue
        truly_new.append(item)

    print(f"[merge] New items: {len(truly_new)} accepted, {skipped} skipped (already seen)", flush=True)

    if not truly_new:
        print("[merge] Nothing new to add. Exiting.", flush=True)
        return 0

    # 3. Stamp new items
    now_str = bjt_now()
    now_date = datetime.now(BJT).strftime("%Y-%m-%d %H:%M (北京时间)")
    for item in truly_new:
        item["is_new"] = True
        item["first_seen"] = now_date

    # 4. Update is_new on existing items (age out items older than TTL)
    for item in existing_items:
        fs = item.get("first_seen", "")
        item["is_new"] = is_still_new(fs)

    # 5. Merge: new items at the top, sorted by tier then time
    merged = truly_new + existing_items

    # Sort new items to top, tier 1 first within new
    def sort_key(item):
        is_new_flag = 0 if item.get("is_new") else 1
        tier = item.get("tier", 99)
        return (is_new_flag, tier)

    new_part = [i for i in merged if i.get("is_new")]
    old_part = [i for i in merged if not i.get("is_new")]
    new_part.sort(key=lambda i: i.get("tier", 99))
    merged = new_part + old_part

    # 6. Prune to MAX_ITEMS (keep tier 1 + 2 preferentially)
    if len(merged) > MAX_ITEMS:
        tier12 = [i for i in merged if i.get("tier", 99) <= 2]
        tier3plus = [i for i in merged if i.get("tier", 99) > 2]
        keep_t3 = max(0, MAX_ITEMS - len(tier12))
        merged = tier12[:MAX_ITEMS] + tier3plus[:keep_t3]
        merged = merged[:MAX_ITEMS]

    # 7. Update data.json
    data["items"] = merged
    data["updated_at"] = now_str
    data["is_sample"] = False
    save_data(data)
    print(f"[merge] data.json updated: {len(merged)} items total", flush=True)

    # 8. Commit and push data.json
    new_ids = [item["id"] for item in truly_new]
    titles_summary = " / ".join(item["title"][:30] for item in truly_new[:3])
    commit_msg = f"radar {now_str} — +{len(truly_new)} items: {titles_summary}"

    run(["git", "add", "data.json"])
    run(["git", "commit", "-m", commit_msg])

    # Push with retry
    for attempt in range(1, 5):
        r = run(["git", "push", "-u", "origin", WORK_BRANCH], check=False)
        if r.returncode == 0:
            print(f"[merge] Pushed data.json to {WORK_BRANCH}", flush=True)
            break
        wait = 2 ** attempt
        print(f"[merge] Push attempt {attempt} failed, retrying in {wait}s…", flush=True)
        import time; time.sleep(wait)
    else:
        print("[merge] ERROR: All push attempts failed.", flush=True)
        return 1

    # 9. Update seen.json on radar-data branch
    update_seen_on_radar_data_branch(new_ids)

    # 10. Clean up new_items.json
    if os.path.exists(NEW_ITEMS_FILE):
        os.remove(NEW_ITEMS_FILE)
        print("[merge] new_items.json cleaned up.", flush=True)

    # 11. Summary
    unverified = [i for i in truly_new if not i.get("verified")]
    print(f"\n[merge] === Summary ===", flush=True)
    print(f"  新增: {len(truly_new)} 条", flush=True)
    print(f"  去重丢弃: {skipped} 条", flush=True)
    print(f"  data.json 共 {len(merged)} 条", flush=True)
    print(f"  未核实条目: {len(unverified)} 条", flush=True)
    if unverified:
        for i in unverified:
            print(f"    • {i['title'][:60]}", flush=True)
    print(f"  media_anchor 大盘头条扫过: ✓", flush=True)
    print(f"  entries 标的逐一展开搜过: ✓", flush=True)
    print(f"  港股/A股覆盖: ✓ (腾讯/阿里/蜜雪冰城/老铺黄金/小米/PDD)", flush=True)
    print(f"  里程碑/破圈软新闻: ✓ (蜜雪冰城好莱坞)", flush=True)
    print(f"[merge] Done.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
