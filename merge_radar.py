#!/usr/bin/env python3
"""
merge_radar.py — 合并新闻条目、去重、剪枝，写回 GitHub main 分支并提交本地分支。

流程：
  1. 读取 new_items.json（本轮新增候选）
  2. 读取本地 seen.json（全量去重集合）
  3. 按 SHA1[:12](url|title) 去重，过滤掉已见条目
  4. 读取本地 data.json（当前分支历史条目）+ 从 main 分支拉取 data.json（Pages 版本）
  5. 合并：新条目 + 本地分支条目 + main 条目，按 ID 去重
  6. 排序：is_new=True 在前，再按 tier↑
  7. 剪枝：保留最新 MAX_ITEMS 条
  8. 写回 main 分支（GitHub API）
  9. 更新本地 data.json 和 seen.json
 10. git add / commit / push 本地分支
"""

import json, hashlib, os, sys, base64, subprocess
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

# ── 配置 ────────────────────────────────────────────────────────────────────
REPO        = "dzkeke-tech/market-radar"
TOKEN       = os.environ.get("GITHUB_TOKEN", "")
BRANCH_DATA = "main"          # GitHub Pages 读取的分支
MAX_ITEMS   = 70              # 保留最多条目数
RUN_LABEL   = "第三轮"


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def make_id(url: str, title: str = "") -> str:
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def _api_request(method: str, path: str, payload: dict | None = None):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept":        "application/vnd.github.v3+json",
        "Content-Type":  "application/json",
    })
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, e


def github_get(path: str, ref: str = BRANCH_DATA):
    resp, err = _api_request("GET", path + f"?ref={ref}")
    if err:
        if err.code == 404:
            return None, None
        raise RuntimeError(f"GET {path} failed: {err.code} {err.reason}")
    content = base64.b64decode(resp["content"]).decode()
    return content, resp["sha"]


def github_put(path: str, content: str, sha: str | None, message: str):
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch":  BRANCH_DATA,
    }
    if sha:
        payload["sha"] = sha
    resp, err = _api_request("PUT", path, payload)
    if err:
        raise RuntimeError(f"PUT {path} failed: {err.code} {err.read().decode()[:300]}")
    return resp


def git_run(*args, **kwargs):
    result = subprocess.run(["git"] + list(args), capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def beijing_now() -> str:
    utc_now = datetime.now(timezone.utc)
    bj = utc_now + timedelta(hours=8)
    return bj.strftime("%Y-%m-%d %H:%M (北京时间)")


# ── 主流程 ────────────────────────────────────────────────────────────────────
def main() -> int:
    today_str = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d")

    # 1. 读 new_items.json
    try:
        with open("new_items.json", "r", encoding="utf-8") as f:
            new_items: list[dict] = json.load(f)
    except FileNotFoundError:
        print("❌ new_items.json 不存在，请先生成。")
        return 1

    # 2. 读本地 seen.json
    with open("seen.json", "r", encoding="utf-8") as f:
        seen_data = json.load(f)
    local_seen_ids: set[str] = set(seen_data.get("ids", []))

    # 3. 去重并重算 ID
    fresh: list[dict] = []
    dup_count = 0
    for item in new_items:
        item_id = make_id(item.get("url", ""), item.get("title", ""))
        item["id"] = item_id
        if item_id in local_seen_ids:
            dup_count += 1
        else:
            fresh.append(item)

    print(f"候选: {len(new_items)} | 去重丢弃: {dup_count} | 净新增: {len(fresh)}")

    # 4a. 读本地 data.json（当前分支）
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            local_data = json.load(f)
        local_items: list[dict] = local_data.get("items", [])
    except (FileNotFoundError, json.JSONDecodeError):
        local_data = {}
        local_items = []

    # 4b. 从 main 拉取 data.json（GitHub Pages 版）
    main_raw, main_data_sha = github_get("data.json")
    if main_raw:
        main_data = json.loads(main_raw)
        main_items: list[dict] = main_data.get("items", [])
        print(f"main data.json: {len(main_items)} 条历史条目")
    else:
        main_data = {}
        main_items = []
        main_data_sha = None
        print("main data.json: 不存在，将新建")

    # 5. 合并去重
    now_iso = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    seen_in_merge: set[str] = set()
    merged: list[dict] = []

    # 先放新条目（is_new=True）
    for item in fresh:
        if item["id"] not in seen_in_merge:
            item["is_new"]     = True
            item["first_seen"] = today_str
            merged.append(item)
            seen_in_merge.add(item["id"])

    # 再放本地分支条目（今日先前各轮）
    for item in local_items:
        if item["id"] not in seen_in_merge:
            merged.append(item)
            seen_in_merge.add(item["id"])

    # 最后补 main 历史条目（降 is_new）
    for item in main_items:
        if item["id"] not in seen_in_merge:
            item["is_new"] = False
            merged.append(item)
            seen_in_merge.add(item["id"])

    # 6. 排序：is_new=True 在前，再按 tier 升序
    merged.sort(key=lambda x: (0 if x.get("is_new") else 1, x.get("tier", 9)))

    # 7. 剪枝
    if len(merged) > MAX_ITEMS:
        merged = merged[:MAX_ITEMS]
    print(f"合并后: {len(merged)} 条（MAX_ITEMS={MAX_ITEMS}）")

    # 8. 构建最终 data.json
    watchlist = local_data.get("watchlist") or main_data.get("watchlist") or []
    positions = local_data.get("positions") or main_data.get("positions") or []
    out_data = {
        "is_sample":  False,
        "updated_at": beijing_now(),
        "next_runs":  ["08:00", "13:00", "18:00"],
        "watchlist":  watchlist,
        "positions":  positions,
        "items":      merged,
    }
    out_json = json.dumps(out_data, ensure_ascii=False, indent=2)

    # 8a. 写到 main 分支
    new_count = len(fresh)
    titles    = "/".join(i["title"][:15] for i in fresh[:3])
    msg_data  = f"chore(radar): update market radar for {today_str} ({RUN_LABEL}+{new_count}条：{titles})"
    github_put("data.json", out_json, main_data_sha, msg_data)
    print(f"✅ data.json → main ({len(merged)} 条)")

    # 9. 更新 seen.json（合并 local + main 已知 ID + 新增）
    main_seen_raw, main_seen_sha = github_get("seen.json")
    if main_seen_raw:
        main_seen_ids: set[str] = set(json.loads(main_seen_raw).get("ids", []))
    else:
        main_seen_ids = set()
        main_seen_sha = None

    all_seen_ids = sorted(local_seen_ids | main_seen_ids | {i["id"] for i in fresh})
    seen_out = json.dumps({"ids": all_seen_ids}, ensure_ascii=False, indent=2)

    github_put("seen.json", seen_out, main_seen_sha,
               f"chore(radar): update seen for {today_str}")
    print(f"✅ seen.json → main ({len(all_seen_ids)} IDs)")

    # 9b. 同步更新本地文件
    with open("data.json", "w", encoding="utf-8") as f:
        f.write(out_json)
    with open("seen.json", "w", encoding="utf-8") as f:
        f.write(seen_out)

    # 10. 提交本地分支
    git_run("add", "data.json", "seen.json", "new_items.json")
    git_run("commit", "-m", msg_data)
    git_run("push", "-u", "origin", "claude/nice-mayer-63iyy0")
    print(f"✅ git commit + push → claude/nice-mayer-63iyy0")

    return 0


if __name__ == "__main__":
    sys.exit(main())
