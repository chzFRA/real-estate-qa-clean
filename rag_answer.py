import os, glob, json, argparse
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import faiss
from sentence_transformers import SentenceTransformer
from llm_utils import call_model

# === 路径配置 ===
INDEX_DIR = Path("vector_index")
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5  # 检索条文片段数量

# === 向量检索 & 加载 ===
def load_indexes():
    indexes, metas = [], []
    for faiss_fp in INDEX_DIR.glob("*.faiss"):
        meta_fp = faiss_fp.with_name(f"{faiss_fp.stem}_meta.parquet")
        if not meta_fp.exists():
            continue
        index = faiss.read_index(str(faiss_fp))
        meta = pd.read_parquet(meta_fp, engine="pyarrow")
        indexes.append(index)
        metas.append(meta)
    return indexes, metas

INDEXES, METAS = load_indexes()
MODEL = SentenceTransformer(EMBED_MODEL)

# === 检索相关条文 ===
def retrieve_context(question: str, indexes, metas, model, top_k=5):
    q_vec = model.encode([question]).astype("float32")
    context_chunks = []
    for idx, index in enumerate(indexes):
        D, I = index.search(q_vec, top_k)
        meta = metas[idx]
        for _, ix in zip(D[0], I[0]):
            if ix == -1: continue
            row = meta.iloc[ix]
            chunk = row.get("chunk_text", row.get("doc", ""))  # 尝试取 chunk_text，没有则取 doc 列
            context_chunks.append(chunk.strip())
    return "\n\n".join(context_chunks)

# === 构建 Prompt ===
def build_prompt(question: str, context: str):
    return f"""你是一名房地产法律专家，结合以下法规内容回答问题：

【法规条文】：
{context}

【问题】：
{question}

请直接回答正确选项的字母（A/B/C/D），无需解释。"""

# === 单题测试 ===
def answer_one_question(q_text: str):
    ctx = retrieve_context(q_text, INDEXES, METAS, MODEL, top_k=TOP_K)
    prompt = build_prompt(q_text, ctx)
    model_ans = call_model(prompt, model="deepseek")
    print("\n🧠 LLM 选择的答案：", model_ans.strip())
    print("——— 完成 ——\n")

# === 批量测试 ===
def run_batch(mcq_file):
    with open(mcq_file, "r", encoding="utf-8") as f:
        content = f.read()

    questions = content.split("------ Chunk")
    total = len(questions) - 1

    correct = 0
    for q in tqdm(questions[1:], desc="📖 批量评测中"):
        parts = q.strip().split("正确答案:")
        if len(parts) < 2: continue
        q_text, correct_ans = parts[0], parts[1].strip()[0]
        ctx = retrieve_context(q_text, INDEXES, METAS, MODEL, top_k=TOP_K)
        prompt = build_prompt(q_text, ctx)
        pred_ans = call_model(prompt, model="deepseek").strip()[0]

        if pred_ans.upper() == correct_ans.upper():
            correct += 1

    print(f"\n✅ 批量测试完成，准确率：{correct}/{total} = {correct/total:.2%}")

# === 主程序入口 ===
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mcq_file", help="批量评测：指定一份 _mcq.txt / .json 文件")
    ap.add_argument("--top_k", type=int, default=5)
    args = ap.parse_args()

    if args.mcq_file:
        run_batch(args.mcq_file)
    else:
        print("✨ 进入交互测试：直接粘贴一道题（包含四个选项），输入空行结束，Ctrl+C 退出\n")
        try:
            while True:
                lines = []
                print("请粘贴完整题目（空行结束）：")
                while True:
                    ln = input()
                    if not ln.strip(): break
                    lines.append(ln)
                q = "\n".join(lines).strip()
                if q:
                    answer_one_question(q)
        except KeyboardInterrupt:
            print("\n👋 再见 ~")
