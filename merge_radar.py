"""
merge_radar.py — 读取 new_items.json，与 data.json 合并，去除语义重复，写回 data.json，
更新 seen.json（本地），并通过 GitHub API 把两个文件推送到对应分支。
"""
import json, os, sys, base64, hashlib, subprocess, datetime

# ── 配置 ───────────────────────────────────────────────────────────────
OWNER  = "dzkeke-tech"
REPO   = "market-radar"
DATA_BRANCH = "main"          # data.json 所在分支
SEEN_BRANCH = "claude/radar-data"  # seen.json 所在分支
MAX_ITEMS   = 120             # data.json 最多保留条目数（超出按 tier+时间剪枝）
BEIJING_TZ  = "+08:00"

TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN:
    print("ERROR: GITHUB_TOKEN not set", file=sys.stderr)
    sys.exit(1)

# ── 工具 ───────────────────────────────────────────────────────────────
def make_id(url, title):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

def now_beijing():
    # 使用 date 命令获取北京时间
    ts = subprocess.check_output(
        ['python3', '-c',
         'from datetime import datetime, timezone, timedelta; '
         'tz=timezone(timedelta(hours=8)); '
         'print(datetime.now(tz).strftime("%Y-%m-%d %H:%M (北京时间)"))'],
        text=True
    ).strip()
    return ts

def now_iso():
    ts = subprocess.check_output(
        ['python3', '-c',
         'from datetime import datetime, timezone, timedelta; '
         'tz=timezone(timedelta(hours=8)); '
         'print(datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00"))'],
        text=True
    ).strip()
    return ts

def github_get(path, ref=None):
    import urllib.request
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    if ref:
        url += f"?ref={ref}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    })
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

def github_put(path, content_bytes, message, branch, sha=None):
    import urllib.request
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode(),
        "branch": branch
    }
    if sha:
        payload["sha"] = sha
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28"
    })
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return None, f"HTTP {e.code}: {body}"

# ── 主逻辑 ─────────────────────────────────────────────────────────────
def main():
    # 1. 读 new_items.json
    with open("new_items.json", encoding="utf-8") as f:
        new_items = json.load(f)

    # 2. 读本地 data.json
    with open("data.json", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {it["id"] for it in data["items"]}

    # 3. 去除与 data.json 语义重复的条目（ID 级别去重）
    truly_new = [it for it in new_items if it["id"] not in existing_ids]
    skipped   = len(new_items) - len(truly_new)

    print(f"new_items: {len(new_items)}, skipped (ID dup in data.json): {skipped}, adding: {len(truly_new)}")

    if not truly_new:
        print("没有新条目需要合并，退出。")
        # Still update seen.json

    ts_label = now_beijing()
    ts_iso   = now_iso()

    # 4. 标记旧条目 is_new = False
    for it in data["items"]:
        it["is_new"] = False

    # 5. 新条目加 is_new / first_seen / time（转 ISO 格式）
    for it in truly_new:
        it["is_new"]     = True
        it["first_seen"] = ts_label
        # 把 "HH:MM" 格式的 time 转为 ISO（用今日北京日期）
        raw_time = it.get("time", "00:00")
        if len(raw_time) == 5 and ":" in raw_time:
            date_part = ts_label.split()[0]  # "2026-07-03"
            it["time"] = f"{date_part}T{raw_time}:00{BEIJING_TZ}"
        # 其余保留原值

    # 6. 合并（新条目在前）
    merged = truly_new + data["items"]

    # 7. 剪枝：超出 MAX_ITEMS 时，从末尾删除最低 tier 的旧条目
    if len(merged) > MAX_ITEMS:
        merged = merged[:MAX_ITEMS]

    # 8. 更新 data.json 内容
    data["items"]      = merged
    data["updated_at"] = ts_label

    data_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

    # 9. 更新本地 data.json
    with open("data.json", "wb") as f:
        f.write(data_bytes)
    print(f"data.json updated locally ({len(merged)} items).")

    # 10. 推送 data.json 到 main 分支
    remote_data = github_get("data.json", ref=DATA_BRANCH)
    data_sha = remote_data["sha"] if remote_data else None
    commit_msg = f"chore(radar): update market radar for {ts_label} — {len(truly_new)} new items"
    result, err = github_put("data.json", data_bytes, commit_msg, DATA_BRANCH, sha=data_sha)
    if err:
        print(f"ERROR pushing data.json: {err}", file=sys.stderr)
        sys.exit(1)
    print(f"data.json pushed to {DATA_BRANCH}.")

    # 11. 更新 seen.json（追加所有 new item IDs 到 seen）
    seen_remote = github_get("seen.json", ref=SEEN_BRANCH)
    if seen_remote:
        seen_content = base64.b64decode(seen_remote["content"]).decode("utf-8")
        seen_data = json.loads(seen_content)
        seen_sha  = seen_remote["sha"]
    else:
        seen_data = {"ids": []}
        seen_sha  = None

    seen_ids_set = set(seen_data["ids"])
    new_ids = [it["id"] for it in truly_new]
    added_to_seen = 0
    for nid in new_ids:
        if nid not in seen_ids_set:
            seen_ids_set.add(nid)
            seen_data["ids"].append(nid)
            added_to_seen += 1

    seen_bytes = json.dumps(seen_data, ensure_ascii=False, indent=2).encode("utf-8")

    # 保存本地 seen.json
    with open("seen.json", "wb") as f:
        f.write(seen_bytes)

    # 推送 seen.json 到 radar-data 分支
    seen_commit_msg = f"chore(seen): update seen for {ts_label} (+{added_to_seen} ids)"
    result2, err2 = github_put("seen.json", seen_bytes, seen_commit_msg, SEEN_BRANCH, sha=seen_sha)
    if err2:
        print(f"ERROR pushing seen.json: {err2}", file=sys.stderr)
        sys.exit(1)
    print(f"seen.json pushed to {SEEN_BRANCH} (+{added_to_seen} new IDs, total {len(seen_data['ids'])}).")

    print(f"\n✅ 发布完成：新增 {len(truly_new)} 条，跳过重复 {skipped} 条，seen.json +{added_to_seen} IDs")

if __name__ == "__main__":
    main()

