#!/usr/bin/env python3
"""
merge_radar.py — 合并 new_items.json 到 data.json 并推送到 GitHub main 分支
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

REPO = "dzkeke-tech/market-radar"
DATA_BRANCH = "main"
MAX_ITEMS = 60
MAX_DAYS = 3
BEIJING_TZ = timezone(timedelta(hours=8))


def github_api(method, path, data=None):
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN 未设置")
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        raise RuntimeError(f"GitHub API {e.code}: {detail}") from e


def get_file_sha(path, branch):
    try:
        resp = github_api("GET", f"/repos/{REPO}/contents/{path}?ref={branch}")
        return resp.get("sha")
    except RuntimeError:
        return None


def push_file(path, content_str, message, branch, sha=None):
    payload = {
        "message": message,
        "content": base64.b64encode(content_str.encode()).decode(),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    return github_api("PUT", f"/repos/{REPO}/contents/{path}", payload)


def main():
    now = datetime.now(BEIJING_TZ)
    today_str = now.strftime("%Y-%m-%d")

    # 1. 读取 new_items.json
    try:
        with open("new_items.json", encoding="utf-8") as f:
            new_items = json.load(f)
    except FileNotFoundError:
        print("new_items.json 不存在，退出", file=sys.stderr)
        sys.exit(1)
    print(f"[merge] 候选新增: {len(new_items)} 条")

    # 2. 读取本地 data.json
    try:
        with open("data.json", encoding="utf-8") as f:
            data = json.load(f)
        existing_items = data.get("items", [])
    except Exception:
        data = {}
        existing_items = []

    # 3. 读取本地 seen.json
    try:
        with open("seen.json", encoding="utf-8") as f:
            seen = json.load(f)
        seen_ids: set = set(seen.get("ids", []))
    except Exception:
        seen = {"ids": []}
        seen_ids = set()

    # 4. 去重过滤
    truly_new = [item for item in new_items if item["id"] not in seen_ids]
    skipped = len(new_items) - len(truly_new)
    print(f"[merge] 去重丢弃: {skipped} | 真正新增: {len(truly_new)}")

    # 5. 给新条目打标签
    for item in truly_new:
        item["is_new"] = True
        item.setdefault("first_seen", today_str)

    # 已有条目：上次已入库，清除 is_new 标记
    for item in existing_items:
        item["is_new"] = False

    # 6. 合并、剪枝、排序
    all_items = truly_new + existing_items
    cutoff = (now - timedelta(days=MAX_DAYS)).strftime("%Y-%m-%d")
    all_items = [i for i in all_items if i.get("first_seen", today_str) >= cutoff]
    all_items.sort(key=lambda x: (x.get("tier", 9), 0 if x.get("is_new") else 1))
    all_items = all_items[:MAX_ITEMS]

    # 7. 更新 seen_ids（保留最近 500 条历史）
    new_ids = [item["id"] for item in truly_new]
    updated_ids = list(seen_ids) + new_ids
    updated_ids = updated_ids[-500:]

    # 8. 构建新 data.json
    updated_at = now.strftime("%Y-%m-%d %H:%M") + " (北京时间)"
    new_data = {
        "is_sample": False,
        "updated_at": updated_at,
        "next_runs": data.get("next_runs", []),
        "watchlist": data.get("watchlist", []),
        "positions": data.get("positions", []),
        "items": all_items,
    }
    new_seen = {"ids": updated_ids}

    data_str = json.dumps(new_data, ensure_ascii=False, indent=2)
    seen_str = json.dumps(new_seen, ensure_ascii=False, indent=2)

    # 9. 写本地文件
    with open("data.json", "w", encoding="utf-8") as f:
        f.write(data_str)
    with open("seen.json", "w", encoding="utf-8") as f:
        f.write(seen_str)
    print(f"[merge] 本地写入: data.json ({len(all_items)} 条), seen.json ({len(updated_ids)} IDs)")

    # 10. 推送到 GitHub main 分支
    commit_msg = f"chore(radar): update market radar for {today_str} (第二轮+{len(truly_new)}条)"
    try:
        data_sha = get_file_sha("data.json", DATA_BRANCH)
        seen_sha = get_file_sha("seen.json", DATA_BRANCH)

        push_file("data.json", data_str, commit_msg, DATA_BRANCH, data_sha)
        print(f"[merge] data.json → {DATA_BRANCH} ✓")

        push_file(
            "seen.json",
            seen_str,
            f"chore(radar): update seen for {today_str}",
            DATA_BRANCH,
            seen_sha,
        )
        print(f"[merge] seen.json → {DATA_BRANCH} ✓")

        print(f"[merge] 发布成功 ✓  updated_at={updated_at}")
    except Exception as exc:
        print(f"[merge] GitHub 推送失败: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
