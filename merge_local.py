"""Runs merge_radar logic with gh_put patched to save locally instead of GitHub API."""
import json
import sys
import merge_radar

saved = {}

def gh_put_local(filename, obj, sha, message):
    saved[filename] = (obj, sha, message)
    print(f"  LOCAL CAPTURE {filename}")

merge_radar.gh_put = gh_put_local
merge_radar.main()

for fname, (obj, sha, message) in saved.items():
    local = f"_merged_{fname.replace('/', '_')}"
    with open(local, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"Written: {local}  (sha={sha}, msg={message!r})")
