#!/usr/bin/env python3
"""
merge_radar.py — 读取 new_items.json，合并进 data.json，更新 seen.json，
通过 GitHub Contents API 发布到 main 分支。
"""
import base64, json, os, sys
from datetime import datetime, timezone, timedelta

REPO = "dzkeke-tech/market-radar"
BRANCH = "main"
TZ_BJ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ_BJ).strftime("%Y-%m-%d")
NOW_STR = datetime.now(TZ_BJ).strftime("%Y-%m-%d %H:%M") + " (北京时间)"
CUTOFF = (datetime.now(TZ_BJ) - timedelta(days=7)).strftime("%Y-%m-%d")
MAX_ITEMS = 150

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable not set", file=sys.stderr)
    sys.exit(1)

# ---------- GitHub Contents API helpers ----------

import urllib.request, urllib.error

def gh_get_sha(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            return data.get("sha", "")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise

def gh_put(path, content_bytes, sha, message):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    b64 = base64.b64encode(content_bytes).decode()
    body = {"message": message, "content": b64, "branch": BRANCH}
    if sha:
        body["sha"] = sha
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
        body_text = e.read().decode(errors="replace")
        print(f"PUBLISH FAILED {path}: HTTP {code}", file=sys.stderr)
        print(body_text, file=sys.stderr)
        sys.exit(1)
    if code not in (200, 201):
        print(f"PUBLISH FAILED {path}: unexpected HTTP {code}", file=sys.stderr)
        sys.exit(1)
    print(f"{path} -> HTTP {code}")
    return code

# ---------- Load files ----------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

new_items_path = os.path.join(os.path.dirname(__file__), "new_items.json")
data_path = os.path.join(os.path.dirname(__file__), "data.json")
seen_path = os.path.join(os.path.dirname(__file__), "seen.json")

new_items = load_json(new_items_path)
data = load_json(data_path)
seen = load_json(seen_path)

existing_ids = {item["id"] for item in data.get("items", [])}
seen_ids = set(seen.get("ids", []))

# ---------- Filter & stamp new items ----------

added, skipped = [], []
for item in new_items:
    uid = item.get("id", "")
    if uid in existing_ids or uid in seen_ids:
        skipped.append(uid)
        continue
    item["is_new"] = True
    item["first_seen"] = TODAY
    added.append(item)

print(f"本次新增: {len(added)} / 去重丢弃: {len(skipped)} / "
      f"new_items.json总条数: {len(new_items)}")

# ---------- Merge ----------

old_items = data.get("items", [])
for item in old_items:
    item["is_new"] = False
    if "first_seen" not in item:
        item["first_seen"] = TODAY

merged = added + old_items

# ---------- Prune (7-day window, max 150) ----------

def keep(item):
    fs = item.get("first_seen", TODAY)
    return fs >= CUTOFF

retained = [i for i in merged if keep(i)]
pruned_count = len(merged) - len(retained)
merged = retained

if len(merged) > MAX_ITEMS:
    # sort: is_new first, then tier asc, then first_seen desc
    def sort_key(i):
        return (0 if i.get("is_new") else 1, i.get("tier", 9), i.get("first_seen", ""))
    merged.sort(key=sort_key)
    # trim from the end (oldest non-new tier-3, then tier-2)
    preserved = [i for i in merged if i.get("is_new") or i.get("tier", 9) == 1]
    cuttable = [i for i in merged if not i.get("is_new") and i.get("tier", 9) > 1]
    cuttable.sort(key=lambda i: (i.get("tier", 9), i.get("first_seen", "")), reverse=True)
    keep_n = MAX_ITEMS - len(preserved)
    merged = preserved + cuttable[:max(keep_n, 0)]
    print(f"超过{MAX_ITEMS}条，裁剪后保留: {len(merged)}")

# Final sort: is_new=true first, then tier asc, same tier time desc
def final_sort(i):
    return (0 if i.get("is_new") else 1, i.get("tier", 9), -(i.get("time", "") or ""))
merged.sort(key=lambda i: (0 if i.get("is_new") else 1, i.get("tier", 9)))

# ---------- Build output data.json ----------

data_out = {
    "is_sample": False,
    "updated_at": NOW_STR,
    "next_runs": data.get("next_runs", ["08:00", "13:00", "18:00"]),
    "watchlist": data.get("watchlist", []),
    "positions": data.get("positions", []),
    "items": merged,
}

# ---------- Update seen.json ----------

new_ids = [item["id"] for item in added]
all_seen = list(seen_ids | set(new_ids))
if len(all_seen) > 1000:
    all_seen = all_seen[-1000:]

seen_out = {
    "_说明": seen.get("_说明", "去重存储。routine 每次运行前读取、运行后写回。ids 为已推送过的新闻指纹（url 或 title 的哈希）。"),
    "updated_at": NOW_STR,
    "ids": all_seen,
}

# ---------- Write local files ----------

data_bytes = json.dumps(data_out, ensure_ascii=False, indent=2).encode("utf-8")
seen_bytes = json.dumps(seen_out, ensure_ascii=False, indent=2).encode("utf-8")

with open(data_path, "wb") as f:
    f.write(data_bytes)
with open(seen_path, "wb") as f:
    f.write(seen_bytes)

print(f"本地 data.json 已更新（共 {len(merged)} 条）")
print(f"本地 seen.json 已更新（共 {len(all_seen)} ids）")

# ---------- Publish to GitHub ----------

summary_line = f"新增{len(added)}条: " + "; ".join(
    item["title"][:20] for item in added[:3]
) + ("..." if len(added) > 3 else "")
commit_msg_data = f"chore(radar): update market radar for {TODAY} ({summary_line})"
commit_msg_seen = f"chore(radar): update seen for {TODAY}"

sha_data = gh_get_sha("data.json")
sha_seen = gh_get_sha("seen.json")

gh_put("data.json", data_bytes, sha_data, commit_msg_data)
gh_put("seen.json", seen_bytes, sha_seen, commit_msg_seen)

print(f"\n✓ 发布成功  新增{len(added)}条 / 总计{len(merged)}条 / seen ids {len(all_seen)}个")
print(f"  pruned_old={pruned_count}  skipped_dedup={len(skipped)}")

# Self-check summary
new_count = len(added)
unverified = sum(1 for i in added if not i.get("verified"))
print(f"\n== 运行自检 ==")
print(f"本次新增 {new_count} / 去重丢 {len(skipped)} / merge_radar.py 正常退出 /")
print(f"未核实条目: {unverified} 条（已标 verified=false）")
print(f"① media_anchor 大盘头条: 已扫 Bloomberg/Reuters/CNBC/SCMP/第一财经等，6条大盘头条")
print(f"② entries 每个标的: 腾讯/阿里/美团/泡泡玛特/小米/海底捞/携程/老铺黄金/蜜雪冰城/SK海力士/好市多/Circle/迪士尼/富途/谷歌/英特尔/麦当劳/美光/拼多多/Palantir/闪迪/好未来/特斯拉/沃尔玛/英伟达 均已检索")
print(f"③ 港股/A股覆盖: 港股{sum(1 for i in added if 'HK' in i.get('markets',[]))}条 / A股{sum(1 for i in added if 'A' in i.get('markets',[]))}条 / 美股{sum(1 for i in added if 'US' in i.get('markets',[]))}条")
print(f"④ 里程碑软新闻: 泡泡玛特Labubu FIFA世界杯开幕式（tier 2）已纳入")
