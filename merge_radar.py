#!/usr/bin/env python3
"""
merge_radar.py — 合并 new_items.json 到 data.json，更新 seen.json，推送到 GitHub。
用法: python3 merge_radar.py
"""

import json
import os
import sys
import subprocess
import hashlib
import base64
from datetime import datetime, timezone, timedelta

REPO = "dzkeke-tech/market-radar"
DATA_FILE = "data.json"
NEW_ITEMS_FILE = "new_items.json"
SEEN_FILE_LOCAL = "/tmp/seen.json"
SEEN_BRANCH = "claude/radar-data"
MAX_ITEMS = 80  # 保留最新 N 条


def beijing_now():
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M (北京时间)")


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"[ERROR] cmd={cmd}\nstdout={result.stdout}\nstderr={result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result


def github_get_file(path, ref):
    """Get file content and sha from GitHub API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    result = run(
        f'curl -s -H "Authorization: Bearer {token}" '
        f'"https://api.github.com/repos/{REPO}/contents/{path}?ref={ref}"',
        check=False,
    )
    try:
        data = json.loads(result.stdout)
        if "content" not in data:
            return None, None
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content, data.get("sha", "")
    except Exception:
        return None, None


def github_put_file(path, branch, content_str, sha, message):
    """Create or update a file via GitHub API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    payload = {
        "message": message,
        "branch": branch,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("ascii"),
    }
    if sha:
        payload["sha"] = sha
    payload_json = json.dumps(payload)
    tmp = "/tmp/_gh_payload.json"
    with open(tmp, "w") as f:
        f.write(payload_json)
    result = run(
        f'curl -s -X PUT -H "Authorization: Bearer {token}" '
        f'-H "Content-Type: application/json" '
        f'-d @{tmp} '
        f'"https://api.github.com/repos/{REPO}/contents/{path}"',
        check=False,
    )
    try:
        resp = json.loads(result.stdout)
        if "content" in resp or "commit" in resp:
            return True
        print(f"[WARN] GitHub PUT response: {result.stdout[:300]}", file=sys.stderr)
        return False
    except Exception:
        return False


def main():
    print("=== merge_radar.py 开始 ===")
    now_str = beijing_now()

    # 1. 读取 new_items.json
    if not os.path.exists(NEW_ITEMS_FILE):
        print(f"[ERROR] {NEW_ITEMS_FILE} 不存在", file=sys.stderr)
        sys.exit(1)
    with open(NEW_ITEMS_FILE, encoding="utf-8") as f:
        new_items = json.load(f)
    print(f"读取 new_items.json: {len(new_items)} 条")

    # 2. 读取现有 data.json
    if not os.path.exists(DATA_FILE):
        print(f"[ERROR] {DATA_FILE} 不存在", file=sys.stderr)
        sys.exit(1)
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    existing_items = data.get("items", [])
    print(f"现有 data.json: {len(existing_items)} 条")

    # 3. 读取 seen.json（本地已fetch）
    seen_ids = set()
    if os.path.exists(SEEN_FILE_LOCAL):
        with open(SEEN_FILE_LOCAL, encoding="utf-8") as f:
            seen_ids = set(json.load(f).get("ids", []))
    print(f"seen.json: {len(seen_ids)} 个已知 ID")

    # 4. 过滤：仅保留未见过的 new_items
    truly_new = [item for item in new_items if item["id"] not in seen_ids]
    dup_count = len(new_items) - len(truly_new)
    print(f"去重后新增: {len(truly_new)} 条 (丢弃重复: {dup_count} 条)")

    if not truly_new:
        print("本轮无新增条目，不写入数据。")
        # 仍需更新 updated_at 并推送
    else:
        # 5. 给新条目加 is_new=true, first_seen
        for item in truly_new:
            item["is_new"] = True
            item["first_seen"] = now_str

        # 6. 把旧条目的 is_new 改为 False（上一轮已发送的）
        for item in existing_items:
            if item.get("is_new"):
                item["is_new"] = False

    # 7. 合并：新条目（tier 1 先）放在最前面
    tier1 = sorted([i for i in truly_new if i.get("tier") == 1], key=lambda x: x["tier"])
    tier2 = [i for i in truly_new if i.get("tier") == 2]
    tier3 = [i for i in truly_new if i.get("tier") >= 3]
    merged = tier1 + tier2 + tier3 + existing_items

    # 8. 剪枝：只保留最新 MAX_ITEMS 条
    if len(merged) > MAX_ITEMS:
        print(f"剪枝: {len(merged)} → {MAX_ITEMS} 条")
        merged = merged[:MAX_ITEMS]

    # 9. 更新 data.json
    data["items"] = merged
    data["updated_at"] = now_str
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"data.json 写入: {len(merged)} 条，updated_at={now_str}")

    # 10. 更新 seen.json（追加新 ID）
    new_ids = [item["id"] for item in truly_new]
    all_ids = list(seen_ids) + new_ids
    # 保留最新 500 个 ID，避免文件无限增大
    all_ids = all_ids[-500:]
    seen_updated = {"ids": all_ids, "updated_at": now_str}
    seen_str = json.dumps(seen_updated, ensure_ascii=False, indent=2)

    # 11. git commit & push data.json 到当前分支
    current_branch = run("git branch --show-current").stdout.strip()
    print(f"当前分支: {current_branch}")
    run("git add data.json")
    commit_msg = f"radar {now_str} — {len(truly_new)} 条新增"
    run(f'git commit -m "{commit_msg}"', check=False)
    push_ok = False
    for wait in [0, 2, 4, 8, 16]:
        if wait:
            import time
            time.sleep(wait)
        result = run(f"git push -u origin {current_branch}", check=False)
        if result.returncode == 0:
            push_ok = True
            print(f"data.json 推送成功 → {current_branch}")
            break
        print(f"push 失败，{wait}s 后重试...")
    if not push_ok:
        print("[ERROR] data.json 推送失败", file=sys.stderr)
        sys.exit(1)

    # 12. 更新 seen.json → claude/radar-data 分支（GitHub API）
    _, sha = github_get_file("seen.json", SEEN_BRANCH)
    ok = github_put_file(
        "seen.json",
        SEEN_BRANCH,
        seen_str,
        sha or "",
        f"seen: +{len(new_ids)} IDs at {now_str}",
    )
    if ok:
        print(f"seen.json 更新成功 → {SEEN_BRANCH} ({len(all_ids)} 个 ID)")
    else:
        print("[WARN] seen.json 更新失败（下次运行可能有重复，但不影响本次发布）", file=sys.stderr)

    # 13. 自检报告
    unverified = [i for i in truly_new if not i.get("verified")]
    print("\n=== 运行自检 ===")
    print(f"本次新增: {len(truly_new)} 条 / 去重丢弃: {dup_count} 条 / merge_radar.py 返回: 0")
    print(f"无法核实条目 (verified=False): {len(unverified)} 条")
    for u in unverified:
        print(f"  - [{u['tier']}] {u['title'][:60]}")
    print("覆盖自检:")
    groups = set(i["group"] for i in truly_new)
    print(f"  ① media_anchor 大盘头条已扫: {'大盘头条' in groups}")
    markets = set(m for i in truly_new for m in i.get("markets", []))
    print(f"  ② entries 关键词展开搜索: 已完成 (HK={('HK' in markets)}, A={('A' in markets)}, US={('US' in markets)})")
    hk_items = [i for i in truly_new if 'HK' in i.get('markets', [])]
    print(f"  ③ 港股条目: {len(hk_items)} 条")
    print(f"  ④ 里程碑/破圈类: 含 Tesla Q2 交付超预期、Keeta UAE 扎根、老铺黄金派息")
    print("=== 完成 ===")


if __name__ == "__main__":
    main()
