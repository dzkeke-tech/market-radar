#!/usr/bin/env python3
"""
merge_radar.py — 合并 new_items.json 到 data.json，更新 seen.json，
并通过 GitHub Contents API 发布到 main 分支。
"""
import json, os, sys, base64, subprocess
from datetime import datetime, timezone, timedelta

REPO = "dzkeke-tech/market-radar"
BRANCH = "main"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 北京时间
BJT = timezone(timedelta(hours=8))

def now_bj():
    return datetime.now(BJT)

def today_bj():
    return now_bj().strftime("%Y-%m-%d")

def now_str():
    return now_bj().strftime("%Y-%m-%d %H:%M (北京时间)")

# ── 读本地文件 ────────────────────────────────────────────────
def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# ── GitHub Contents API ──────────────────────────────────────
def api_get_sha(filepath):
    import urllib.request, urllib.error
    url = f"https://api.github.com/repos/{REPO}/contents/{filepath}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
            return data.get("sha", "")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise

def api_put(filepath, content_bytes, message, sha):
    import urllib.request, urllib.error
    url = f"https://api.github.com/repos/{REPO}/contents/{filepath}"
    body = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode(),
        "branch": BRANCH,
    }
    if sha:
        body["sha"] = sha
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as r:
            code = r.status
            return code, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def publish(filepath, local_path, message):
    print(f"  Publishing {filepath} …", end=" ", flush=True)
    sha = api_get_sha(filepath)
    content_bytes = open(local_path, "rb").read()
    code, body = api_put(filepath, content_bytes, message, sha)
    print(f"HTTP {code}")
    if code not in (200, 201):
        print(f"  PUBLISH FAILED for {filepath}:", file=sys.stderr)
        print(body.decode(errors="replace"), file=sys.stderr)
        sys.exit(1)

# ── 主逻辑 ───────────────────────────────────────────────────
def main():
    today = today_bj()
    cutoff = (now_bj() - timedelta(days=7)).strftime("%Y-%m-%d")

    # 1. 读现有 data.json
    data = read_json("data.json")
    existing = data.get("items", [])

    # 2. 读新增条目
    new_items = read_json("new_items.json")
    print(f"New items to add: {len(new_items)}")

    # 3. 读 seen.json（本地版本，已含本轮前的 ids）
    seen_data = read_json("seen.json")
    seen_ids = set(seen_data.get("ids", []))

    # 4. 去重：跳过已在 data.json items 中的 id
    existing_ids = {it.get("id") for it in existing}
    filtered_new = []
    for item in new_items:
        iid = item.get("id", "")
        if iid in existing_ids or iid in seen_ids:
            print(f"  SKIP dup: {iid} — {item.get('title','')[:40]}")
        else:
            filtered_new.append(item)
    print(f"After dedup: {len(filtered_new)} truly new items")

    # 5. 标记旧条目 is_new=false
    for it in existing:
        it["is_new"] = False
        if "first_seen" not in it:
            it["first_seen"] = today  # 补缺

    # 6. 标记新条目 is_new=true，补 first_seen
    for it in filtered_new:
        it["is_new"] = True
        it["first_seen"] = today

    # 7. 合并
    merged = filtered_new + existing

    # 8. 剪枝：丢 first_seen < cutoff
    before_prune = len(merged)
    merged = [it for it in merged if it.get("first_seen", today) >= cutoff]
    pruned_age = before_prune - len(merged)

    # 若超 150 条，继续裁
    pruned_extra = 0
    if len(merged) > 150:
        # 保护：is_new=true、tier=1 一律保留
        keep = [it for it in merged if it.get("is_new") or it.get("tier") == 1]
        cands = [it for it in merged if not it.get("is_new") and it.get("tier") != 1]
        # 按 tier 降序、first_seen 升序（先裁 tier=3 最旧）
        cands.sort(key=lambda x: (-x.get("tier", 3), x.get("first_seen", "")))
        trim = len(merged) - 150
        pruned_extra = min(trim, len(cands))
        merged = keep + cands[pruned_extra:]

    # 9. 排序：is_new true 先、tier 升序、time 倒序
    def sort_key(it):
        return (0 if it.get("is_new") else 1, it.get("tier", 3), it.get("time", ""))
    merged.sort(key=sort_key)

    # 10. 读 keywords.json 的 entries 作为 watchlist
    kw = read_json("keywords.json")
    watchlist = list(kw.get("entries", {}).keys())

    # 11. 写 data.json
    data_out = {
        "is_sample": False,
        "updated_at": now_str(),
        "next_runs": ["08:00", "13:00", "18:00"],
        "watchlist": watchlist,
        "positions": data.get("positions", []),
        "items": merged,
    }
    write_json("data.json", data_out)
    print(f"data.json written: {len(merged)} items total "
          f"({len(filtered_new)} new, {pruned_age} pruned by age, {pruned_extra} pruned by count)")

    # 12. 更新 seen.json
    new_ids = [it["id"] for it in filtered_new if "id" in it]
    all_seen = list(seen_ids | set(new_ids))
    if len(all_seen) > 1000:
        all_seen = all_seen[-1000:]
    seen_out = {"ids": all_seen, "updated_at": now_str()}
    write_json("seen.json", seen_out)
    print(f"seen.json updated: {len(all_seen)} total ids")

    # 13. 发布
    if not TOKEN:
        print("WARNING: GITHUB_TOKEN not set — skipping publish", file=sys.stderr)
        sys.exit(1)

    commit_msg = (
        f"chore(radar): update market radar for {today} "
        f"— {len(filtered_new)} new items"
    )
    print("Publishing to GitHub …")
    publish("data.json", "data.json", commit_msg)
    publish("seen.json", "seen.json", f"chore(radar): update seen for {today}")

    print(f"\n✓ Done. {len(filtered_new)} new / {len(merged)} total / "
          f"pruned {pruned_age+pruned_extra}")

if __name__ == "__main__":
    main()
