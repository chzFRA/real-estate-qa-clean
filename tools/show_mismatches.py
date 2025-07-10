# tools/show_mismatches.py
"""
把 gt ≠ pred 的题目导出到 csv
用法:
    python tools/show_mismatches.py file.json          # 自动写入 mismatch_csv/
    python tools/show_mismatches.py file.json --stdout # 仍然走 stdout
"""
import json, csv, sys, os, pathlib, argparse

GT_KEY = "correct_answer"

parser = argparse.ArgumentParser()
parser.add_argument("json_file")
parser.add_argument("--stdout", action="store_true",
                    help="仍然把结果写到标准输出")
args = parser.parse_args()

with open(args.json_file, encoding="utf-8") as f:
    data = json.load(f)

rows = []
for idx, itm in enumerate(data):
    gt   = itm[GT_KEY].strip().upper()[0]
    pred = itm.get("pred", "").strip().upper()[0]
    if pred and pred != gt:
        rows.append({
            "idx": idx,
            "gt": gt,
            "pred": pred,
            "question": itm["question"].replace("\n", " / "),
            "fix": ""                     # 方便后面人工填写
        })

if not rows:
    print("✅ 没有发现不一致题目。")
    sys.exit(0)

# ---------- 输出 ----------
if args.stdout:                 # 旧用法
    w = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
else:                           # 新用法：自动保存
    out_dir = "mismatch_csv"
    os.makedirs(out_dir, exist_ok=True)
    base = pathlib.Path(args.json_file).stem
    out_path = os.path.join(out_dir, base + "_mismatch.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"✅ mismatch CSV saved to {out_path} （共 {len(rows)} 条）")
