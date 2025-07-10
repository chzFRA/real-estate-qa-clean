"""
清理 MCQ json ⽂件里非法的 pred（去掉 “抱”“这”“对”… 之类）。
- 不带参数：默认处理 mcq_clean 目录下的所有 .json
- 带参数：处理指定的一个或多个 .json / 通配
"""

import json, sys, re, glob, os, pathlib

# ---------- 1. 收集待处理文件 ----------
if len(sys.argv) > 1:
    files = sys.argv[1:]                 # 用户手动指定
else:
    files = glob.glob("mcq_clean/*.json")  # 自动搜
    if not files:
        sys.exit("⚠  mcq_clean 里没找到 json 文件，也没有传入文件参数。")

# ---------- 2. 定义合法选项 ----------
valid_opts = {"A", "B", "C", "D"}

# ---------- 3. 逐文件清理 ----------
for jf in files:
    # 路径检查
    if not os.path.isfile(jf):
        print(f"✘  文件不存在: {jf}")
        continue

    with open(jf, encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for itm in data:
        # 只处理有 pred 字段且非法的情况
        if "pred" in itm and itm["pred"].upper() not in valid_opts:
            itm.pop("pred")
            changed = True

    if changed:
        # 备份 → filename.bak
        bak = jf + ".bak"
        os.replace(jf, bak)

        with open(jf, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✔  已清理非法 pred → {jf}   (备份 {bak})")
    else:
        print(f"—  {jf} 无需清理")
