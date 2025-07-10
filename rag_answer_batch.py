import os, json
from pathlib import Path
from tqdm import tqdm
from llm_utils import call_model

INDEX_DIR = Path("vector_index")
MCQ_DIR = Path("mcq_clean")
MODEL = "gpt4"  # 默认使用的模型，可以切换 gpt3.5 / gpt4 / claude / deepseek

def build_prompt(q_obj):
    q = q_obj["question"]
    opts = q_obj["options"]
    return f"""你是一名房地产法律考试专家，根据以下问题选择正确答案：

问题：{q}

A. {opts['A']}
B. {opts['B']}
C. {opts['C']}
D. {opts['D']}

请直接返回字母 A/B/C/D，表示正确选项，无需解释。"""

def evaluate_model(mcq_file):
    with open(mcq_file, "r", encoding="utf-8") as f:
        mcqs = json.load(f)

    correct = 0
    total = len(mcqs)

    for q_obj in tqdm(mcqs, desc=f"📝 正在评估 {mcq_file.name}"):
        prompt = build_prompt(q_obj)
        pred = call_model(prompt, model=MODEL).strip().upper()[0]
        if pred == q_obj["correct_answer"]:
            correct += 1

    acc = correct / total if total > 0 else 0
    print(f"\n📊 文件：{mcq_file.name} | 准确率：{correct}/{total} = {acc:.2%}")

if __name__ == "__main__":
    for mcq_file in MCQ_DIR.glob("*.json"):
        evaluate_model(mcq_file)
