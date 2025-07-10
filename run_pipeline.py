# run_pipeline.py
"""
整体流水线：
1.  缓存各个 MCQ 文件的 LLM 预测
2.  评估准确率
3.  其它自定义步骤……
"""

import subprocess, sys, pathlib, argparse, json, os, pandas as pd

MCQ_DIR   = pathlib.Path("mcq_clean")
MODEL     = "gpt4"
TEMP      = 0.0                     # 现在仅供其他地方使用，cache_preds 不再需要

def run(cmd, stdout=None):
    """薄包装，方便打印调试"""
    print(" ".join(map(str, cmd)))
    subprocess.run([sys.executable, *cmd], check=True, stdout=stdout)

# ---------- Step-1 缓存预测 ----------
def step_cache():
    print("🔮 Step-1 缓存模型预测 …")
    for jf in MCQ_DIR.glob("*.json"):
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        run(["tools/cache_preds.py", str(jf), "--model", MODEL])   # ← 删除 --temp
        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
        
# ---------- Step-2 汇总为 CSV ----------
def step_write_csv(out_file="preds.csv"):
    print("📝 Step-2 汇总写 CSV …")
    rows = []
    for jf in MCQ_DIR.glob("*.json"):
        with open(jf, encoding="utf-8") as f:
            items = json.load(f)
        for it in items:
            rows.append({
                "file"    : jf.name,
                "question": it.get("question", "").strip(),
                "A"       : it.get("options", {}).get("A", ""),
                "B"       : it.get("options", {}).get("B", ""),
                "C"       : it.get("options", {}).get("C", ""),
                "D"       : it.get("options", {}).get("D", ""),
                "pred"    : it.get("pred", ""),
                "answer"  : it.get("correct_answer", "")
            })
    df = pd.DataFrame(rows)
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"✅  已写出 {out_file}（共 {len(df)} 行）")

# ---------- 入口 ----------
if __name__ == "__main__":
    step_cache()          # ① 缓存 / 更新 pred
    step_write_csv()      # ② 汇总成 CSV
