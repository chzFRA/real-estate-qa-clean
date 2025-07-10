# tools/cache_preds.py
"""
为 mcq_clean/*.json 缓存 LLM 预测结果
用法：python tools/cache_preds.py <json_file> [--model gpt4]
（本脚本会被 run_pipeline.py 调用，无需手动执行）
"""
import json, sys, argparse, pathlib, os, time

# -------- 让根目录可 import --------
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 你项目里本来就有的封装。如果没有，就自己实现一个最简单的 dummy。
try:
    from llm_utils import call_model          # 建议保留原来的
except ImportError:                           # 如果真没有，就用一个假实现
    def call_model(prompt, model="gpt4"):
        print("⚠️  llm_utils.call_model 未找到，返回占位符“抱”")
        return "抱"

GT_KEY = "correct_answer"

# ---------------- argparse -----------------
ap = argparse.ArgumentParser()
ap.add_argument("json_file")
ap.add_argument("--model", default="gpt4")
# 👉 ❶ 删掉 --temp 参数（不再需要）
args = ap.parse_args()
jf = pathlib.Path(args.json_file)

# ---------------- 读入 ---------------------
with open(jf, encoding="utf-8") as f:
    data = json.load(f)

# --------- 构造 prompt 的小工具 -------------
def build_prompt(item: dict) -> str:
    q   = item["question"].strip()
    opt = item.get("options", {})
    if not opt:
        return f"请选择 A/B/C/D 回答：\n\n{q}"
    lines = [f"问题：{q}\n"]
    for key in ["A", "B", "C", "D"]:
        if key in opt:
            lines.append(f"{key}. {opt[key]}")
    opts_text = "\n".join(lines)
    return (
        "你是一名法律考试专家，只需回答正确选项字母（A/B/C/D），不要解释：\n\n"
        f"{opts_text}\n\n回答："
    )

# ---------------- 逐题预测 ------------------
changed = False
for itm in data:
    if itm.get("pred"):          # 已经缓存过，跳过
        continue
    prompt = build_prompt(itm)
    try:
        # 👉 ❷ 调用时 **不再传 temp**
        raw = call_model(prompt, model=args.model).strip().upper()
    except Exception as e:
        print("⚠️ LLM 调用失败 -> 写入占位符“抱”", e)
        raw = "抱"
    pred = next((c for c in raw if c in "ABCD"), "抱")
    itm["pred"] = pred
    changed = True
    time.sleep(0.5)              # 轻微限速

# ---------------- 写回 ----------------------
if changed:
    backup = jf.with_suffix(jf.suffix + ".bak")
    if not backup.exists():                      # 只备份一次
        os.rename(jf, backup)
    with open(jf, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅  已写回 {jf.name}（备份 -> {backup.name}）")
else:
    print(f"✔️  {jf.name} 已有 pred，跳过")
