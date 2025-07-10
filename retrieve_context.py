# === rag_answer_hybrid.py ===

import os, json, argparse
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from bm25_retriever import BM25Retriever
from llm_utils import call_model

# === 路径配置 ===
INDEX_DIR = Path("vector_index")
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5

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
BM25 = BM25Retriever()  # 初始化 BM25 检索器

# === 混合检索 ===
def retrieve_context_hybrid(question, indexes, metas, model, bm25_retriever, top_k=5, lambda_weight=0.45):
    q_vec = model.encode([question]).astype("float32")
    dense_scores = defaultdict(lambda: {'dense': 0.0, 'bm25': 0.0})

    for idx, index in enumerate(indexes):
        D, I = index.search(q_vec, top_k * 2)
        meta = metas[idx]
        for score, ix in zip(D[0], I[0]):
            if ix == -1: continue
            row = meta.iloc[ix]
            chunk_id = str(row.get("id", ix))
            text = row.get("chunk_text", row.get("doc", ""))
            dense_scores[chunk_id]['dense'] = float(score)
            dense_scores[chunk_id]['text'] = text.strip()

    bm25_results = bm25_retriever.search(question, top_k * 2)
    for doc_id, score in bm25_results:
        dense_scores[doc_id]['bm25'] = float(score)

    for v in dense_scores.values():
        v['score'] = lambda_weight * v['bm25'] + (1 - lambda_weight) * v['dense']

    top_chunks = sorted(dense_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:top_k]
    return "\n\n".join([v['text'] for _, v in top_chunks if 'text' in v])

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
    ctx = retrieve_context_hybrid(q_text, INDEXES, METAS, MODEL, BM25, top_k=TOP_K)
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
        ctx = retrieve_context_hybrid(q_text, INDEXES, METAS, MODEL, BM25, top_k=TOP_K)
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
