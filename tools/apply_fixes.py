# tools/apply_fixes.py
"""
根据 mismatch_csv 的 fix 列批量更新 MCQ json 的 answer。
"""
# tools/cache_preds.py
import pathlib, sys, os
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json, csv, sys, shutil

GT_KEY = "correct_answer"          # ← 统一加在文件开头

jfile, csvfile = sys.argv[1:3]
data = json.load(open(jfile, encoding="utf-8"))
fixes = {}
for row in csv.DictReader(open(csvfile, encoding="utf-8")):
    if row.get("fix"):
        fixes[int(row["idx"])] = row["fix"].strip().upper()[0]

changed = False
for idx, new in fixes.items():
    if data[idx][GT_KEY].strip().upper()[0] != new:
        data[idx][GT_KEY] = new
        changed = True

if changed:
    shutil.copy(jfile, jfile + ".orig")
    json.dump(data, open(jfile, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"✅ 已更新 {len(fixes)} 处，并备份 {jfile+'.orig'}")
else:
    print("😃 没有需要更新的条目。")
