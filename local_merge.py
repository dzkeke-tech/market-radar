"""Local merge script - simulates merge_radar.py but writes locally instead of via API."""
import json, hashlib, sys
from datetime import datetime, timezone, timedelta as td

TZ_BJ = timezone(td(hours=8))
now_bj = datetime.now(TZ_BJ)
today_str = now_bj.strftime("%Y-%m-%d")
updated_at = now_bj.strftime("%Y-%m-%d %H:%M") + " (北京时间)"

KEEP_DAYS = 7
MAX_ITEMS = 200

# Load files
with open("new_items.json", encoding="utf-8") as f:
    new_items = json.load(f)

with open("data.json", encoding="utf-8") as f:
    data_json = json.load(f)

with open("seen.json", encoding="utf-8") as f:
    seen_json = json.load(f)

existing_items = data_json.get("items", [])
seen_ids = set(seen_json.get("ids", []))

print(f"Loaded {len(new_items)} candidate new items")
print(f"Existing items: {len(existing_items)}, seen IDs: {len(seen_ids)}")

# Date filter (from merge_radar.py validate_new_items logic)
from datetime import date, timedelta

today_date = date.fromisoformat(today_str)

def check_date(item):
    pd = item.get("published_date", "")
    if not pd:
        return None, "missing published_date"
    try:
        pub_date = date.fromisoformat(pd)
    except ValueError:
        return None, f"invalid published_date: {pd}"
    age = (today_date - pub_date).days
    if age > 5:
        return None, f"published_date {pd} is {age} days old (>5)"
    return age, None

validated = []
dropped = []
for item in new_items:
    age, err = check_date(item)
    if err:
        dropped.append((item, err))
    else:
        validated.append(item)

if dropped:
    print(f"Date validation dropped {len(dropped)}:")
    for it, reason in dropped:
        print(f"  ✗ {it.get('title','')[:50]} → {reason}")

# ID dedup
existing_ids = {i["id"] for i in existing_items}
truly_new = [i for i in validated if i.get("id") not in seen_ids and i.get("id") not in existing_ids]
skipped = len(validated) - len(truly_new)
print(f"After id-dedup: {len(truly_new)} new, {skipped} skipped")

# Simple topic dedup: check if title similarity suggests same event
# Use keywords overlap to detect same event
def topics_overlap(a, b):
    """Check if two items likely cover the same event."""
    ka = set(k.lower() for k in a.get("keywords", []))
    kb = set(k.lower() for k in b.get("keywords", []))
    overlap = ka & kb
    if len(overlap) >= 3:
        return True
    # Also check title word overlap
    ta = set(a.get("title","").lower().split())
    tb = set(b.get("title","").lower().split())
    stop = {"the","a","an","as","in","of","on","at","to","for","and","or","is","are","was","were",
            "has","have","after","by","with","from","that","this","its"}
    ta -= stop; tb -= stop
    common = ta & tb
    if len(common) >= 4:
        return True
    return False

topic_dupes = []
truly_new_final = []
for item in truly_new:
    is_dup = False
    for ex in existing_items:
        if topics_overlap(item, ex):
            topic_dupes.append((item, ex))
            is_dup = True
            break
    if not is_dup:
        truly_new_final.append(item)

if topic_dupes:
    print(f"Topic-level dedup dropped {len(topic_dupes)}:")
    for it, matched in topic_dupes:
        print(f"  ⚠ {it.get('title','')[:40]} ≈ {matched.get('title','')[:40]}")
print(f"After topic-dedup: {len(truly_new_final)} truly new")

# Stamp new items
for item in truly_new_final:
    item.setdefault("first_seen", today_str)
    item["is_new"] = True

for item in existing_items:
    item["is_new"] = False

# Prune by date
merged = truly_new_final + existing_items
cutoff = today_date - timedelta(days=KEEP_DAYS)

# Check stale branch
if existing_items:
    def try_parse_date(s):
        try:
            return date.fromisoformat(str(s)[:10])
        except Exception:
            return date.min
    most_recent_seen = max(
        (try_parse_date(i["first_seen"]) for i in existing_items if i.get("first_seen")),
        default=date.min
    )
    stale = (today_date - most_recent_seen).days > KEEP_DAYS
else:
    stale = False

if stale:
    print(f"⚠ Stale branch detected, skipping date prune")
    pruned = merged
else:
    pruned = []
    for item in merged:
        pd_str = item.get("published_date") or item.get("first_seen", "")
        try:
            pd = date.fromisoformat(pd_str)
        except ValueError:
            pruned.append(item)
            continue
        if pd >= cutoff:
            pruned.append(item)

# Sort: new first, then by tier, then by published_date desc
pruned.sort(key=lambda i: (
    0 if i.get("is_new") else 1,
    i.get("tier", 9),
    i.get("published_date", ""),
), reverse=False)
# actually sort by is_new desc, tier asc, date desc
pruned.sort(key=lambda i: (
    not i.get("is_new"),
    i.get("tier", 9),
    -(date.fromisoformat(i["published_date"]).toordinal() if i.get("published_date") else 0)
))

# Trim
if len(pruned) > MAX_ITEMS:
    pruned = pruned[:MAX_ITEMS]

# Update seen IDs
all_candidate_ids = set()
for items_list in [new_items, [i for i,_ in dropped], [i for i,_ in topic_dupes]]:
    for it in items_list:
        if it.get("id"):
            all_candidate_ids.add(it["id"])

new_seen_ids = list(seen_ids | all_candidate_ids)
if len(new_seen_ids) > 1000:
    new_seen_ids = new_seen_ids[-1000:]

# Build output
meta = data_json
new_data = {
    "is_sample": False,
    "updated_at": updated_at,
    "next_runs": meta.get("next_runs", ["08:00", "13:00", "18:00"]),
    "watchlist": meta.get("watchlist", []),
    "positions": [],
    "last_run": {
        "at": updated_at,
        "new_count": len(truly_new_final),
        "degraded": 0,
        "input_missing": False,
    },
    "items": pruned,
}
new_seen = {
    "updated_at": updated_at,
    "ids": new_seen_ids,
}

# Write locally
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

with open("seen.json", "w", encoding="utf-8") as f:
    json.dump(new_seen, f, ensure_ascii=False, indent=2)

print(f"\n✓ Written: +{len(truly_new_final)} new | {len(existing_items)} existing | {len(pruned)} total")
print(f"  seen.json: {len(new_seen_ids)} IDs")
