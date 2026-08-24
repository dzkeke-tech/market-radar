"""
Monkey-patch merge_radar.gh_put to write local files instead of GitHub API.
Run: python3 run_merge_local.py
Outputs: /tmp/out_data.json and /tmp/out_seen.json for manual upload.
"""
import sys, json, base64, types

# Inject a fake gh_put that writes to local files
import merge_radar as mr

_local_outputs = {}

def _fake_gh_put(filename, obj, sha, message):
    out_path = f"/tmp/out_{filename}"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"  LOCAL WRITE {filename} → {out_path}")
    _local_outputs[filename] = out_path

mr.gh_put = _fake_gh_put

# Also patch gh_get to actually fetch from GitHub (it uses urllib which IS allowed for reads)
# (no change needed – reads are allowed through the proxy)

if __name__ == "__main__":
    mr.main()
