#!/usr/bin/env python3
"""
merge_radar.py — 合并 new_items.json 与历史 data.json，推送到 main 分支。
退出码：0=成功，非0=失败。
"""

import json, sys, subprocess, hashlib
from datetime import datetime, timezone, timedelta

# ── 常量 ──────────────────────────────────────────────────────────────────
MAX_ITEMS = 40          # 单次最多保留条目数
MAX_SEEN_IDS = 1000     # seen.json ID 保留上限
PRUNE_HOURS_TIER3 = 24  # tier3 超过此小时数自动剪枝
PRUNE_HOURS_TIER2 = 72  # tier2 超过此小时数自动剪枝（约 3 天）
PRUNE_HOURS_TIER1 = 168 # tier1 保留约 7 天

# ── 北京时间 ──────────────────────────────────────────────────────────────
CST = timezone(timedelta(hours=8))

def now_cst():
    return datetime.now(tz=CST)

def parse_time(t_str):
    """把 data.json 里的 ISO 时间字符串解析成 datetime。"""
    try:
        return datetime.fromisoformat(t_str)
    except Exception:
        return now_cst()

def make_item_time(hhmm: str, base: datetime) -> str:
    """把 new_items 里的 'HH:MM' 转成当天 ISO 时间字符串。"""
    try:
        h, m = map(int, hhmm.split(":"))
        dt = base.replace(hour=h, minute=m, second=0, microsecond=0)
        return dt.isoformat()
    except Exception:
        return base.isoformat()

def make_id(url, title=""):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

# ── 读取文件 ──────────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# ── 主逻辑 ────────────────────────────────────────────────────────────────
def main():
    now = now_cst()
    today_str = now.strftime("%Y-%m-%d")

    # 1. 读取
    new_raw   = load_json("new_items.json", [])
    data      = load_json("data.json", {"items": [], "watchlist": [], "positions": []})
    seen_data = load_json("seen.json", {"ids": []})
    seen_ids  = set(seen_data.get("ids", []))

    existing_items = data.get("items", [])

    # 2. 处理新条目
    new_items = []
    for item in new_raw:
        # 确保有 id
        if "id" not in item:
            item["id"] = make_id(item.get("url", ""), item.get("title", ""))
        # 跳过已在 seen 里的（双重保障）
        if item["id"] in seen_ids:
            continue
        # 补充字段
        item["is_new"] = True
        item["first_seen"] = today_str
        # 转换 time 字段：HH:MM → ISO datetime
        raw_time = item.get("time", "00:00")
        item["time"] = make_item_time(raw_time, now)
        new_items.append(item)

    print(f"New items after dedup: {len(new_items)}")

    # 3. 清除旧条目的 is_new 标记
    for item in existing_items:
        item["is_new"] = False

    # 4. 合并（新在前）
    id_seen_in_merge = {item["id"] for item in existing_items}
    deduped_new = []
    for item in new_items:
        if item["id"] not in id_seen_in_merge:
            deduped_new.append(item)
            id_seen_in_merge.add(item["id"])

    merged = deduped_new + existing_items

    # 5. 剪枝
    def age_hours(item):
        try:
            dt = parse_time(item.get("time", ""))
            delta = now - dt.astimezone(CST)
            return delta.total_seconds() / 3600
        except Exception:
            return 9999

    def keep(item):
        tier = item.get("tier", 3)
        age  = age_hours(item)
        if tier == 1:
            return age <= PRUNE_HOURS_TIER1
        elif tier == 2:
            return age <= PRUNE_HOURS_TIER2
        else:
            return age <= PRUNE_HOURS_TIER3

    pruned = [i for i in merged if keep(i)]

    # 排序：tier asc，时间 desc
    def sort_key(item):
        try:
            dt = parse_time(item.get("time", ""))
            ts = dt.timestamp()
        except Exception:
            ts = 0
        return (item.get("tier", 3), -ts)

    pruned.sort(key=sort_key)

    # 超出上限时优先保留 tier 1/2
    if len(pruned) > MAX_ITEMS:
        tier12 = [i for i in pruned if i.get("tier", 3) <= 2]
        tier3  = [i for i in pruned if i.get("tier", 3) >= 3]
        # tier3 只保留最新的，补到 MAX_ITEMS
        slots_for_tier3 = max(0, MAX_ITEMS - len(tier12))
        final = tier12 + tier3[:slots_for_tier3]
        final.sort(key=sort_key)
        pruned = final

    print(f"Items after pruning: {len(pruned)}")

    # 6. 读取 keywords.json 取 watchlist
    kw = load_json("keywords.json", {})
    watchlist = list(kw.get("entries", {}).keys())

    # 7. 构建 data.json
    data_out = {
        "is_sample": False,
        "updated_at": now.strftime("%Y-%m-%d %H:%M (北京时间)"),
        "next_runs": ["08:00", "13:00", "18:00"],
        "watchlist": watchlist,
        "positions": data.get("positions", []),
        "items": pruned
    }
    save_json("data.json", data_out)
    print("data.json written.")

    # 8. 更新 seen.json（合并新 ID）
    new_ids_list = [item["id"] for item in deduped_new]
    updated_ids = list(seen_ids | set(new_ids_list))
    # 保留最近 MAX_SEEN_IDS 条（近似，按列表末尾为新）
    if len(updated_ids) > MAX_SEEN_IDS:
        updated_ids = updated_ids[-MAX_SEEN_IDS:]
    seen_out = {
        "updated_at": now.strftime("%Y-%m-%d %H:%M (北京时间)"),
        "ids": updated_ids
    }
    save_json("seen.json", seen_out)
    print("seen.json written.")

    # 9. git commit & push to main
    n_new = len(deduped_new)
    keywords_preview = "/".join(
        item.get("title", "")[:12].replace("\n", " ")
        for item in deduped_new[:5]
    )
    commit_msg = (
        f"chore(radar): update market radar {now.strftime('%Y-%m-%d %H:%M')} (北京时间)"
        f" — {n_new} new"
        + (f" ({keywords_preview})" if keywords_preview else "")
    )

    def run(cmd, **kw):
        result = subprocess.run(cmd, capture_output=True, text=True, **kw)
        if result.returncode != 0:
            print(f"CMD FAILED: {' '.join(cmd)}")
            print("STDOUT:", result.stdout[-500:] if result.stdout else "")
            print("STDERR:", result.stderr[-500:] if result.stderr else "")
        return result

    # Stage the two data files
    run(["git", "add", "data.json", "seen.json"])

    # Check if there's anything staged
    status = run(["git", "diff", "--cached", "--stat"])
    if not status.stdout.strip():
        print("Nothing to commit — data unchanged.")
        return 0

    # Commit on current branch
    run(["git", "commit", "-m", commit_msg])

    # Push current branch
    current_branch_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    current_branch = current_branch_result.stdout.strip()
    run(["git", "push", "-u", "origin", current_branch])

    # Push to main (fast-forward, since current branch is ahead of main)
    push_main = run(["git", "push", "origin", f"HEAD:main"])
    if push_main.returncode != 0:
        # Try force push if main has diverged
        print("Fast-forward to main failed, trying force-with-lease...")
        push_main2 = run(["git", "push", "--force-with-lease", "origin", "HEAD:main"])
        if push_main2.returncode != 0:
            print("ERROR: Failed to push to main.")
            return 1

    print(f"Pushed {n_new} new items to origin/{current_branch} and origin/main.")

    # 10. 自检摘要
    unverified = [i for i in deduped_new if not i.get("verified", False)]
    print(
        f"\n[自检] 本次新增 {n_new} 条 / "
        f"去重丢弃 {len(new_raw) - len(deduped_new)} 条 / "
        f"data.json 共 {len(pruned)} 条 / "
        f"未核实 {len(unverified)} 条"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
