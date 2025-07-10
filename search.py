# search.py  —— 终端检索工具
import argparse, glob, os, pickle, faiss
from pathlib import Path
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

def load_all_indexes(index_dir: str):
    indexes, metas = [], []
    for fp in glob.glob(f"{index_dir}/*.faiss"):
        meta_fp = fp.replace(".faiss", "_meta.parquet")
        index    = faiss.read_index(fp)
        meta_df  = pd.read_parquet(meta_fp, engine="pyarrow")
        indexes.append(index)
        metas.append(meta_df)
    return indexes, metas

def search(query: str, indexes, metas, model, top_k=5):
    q_vec = model.encode([query]).astype("float32")
    hits  = []        # (score, law_name, chunk_id, snippet)

    for idx, index in enumerate(indexes):
        D, I = index.search(q_vec, top_k)
        meta = metas[idx]
        for dist, ix in zip(D[0], I[0]):
            if ix == -1: continue
            row = meta.iloc[ix]
            law   = Path(row['doc']).stem        # 若 doc 存原文件名
            snippet = row["chunk_text"][:150].replace("\n", " ") + "..."
            hits.append((dist, law, row['chunk_id'], snippet))

    hits = sorted(hits, key=lambda x: x[0])[:top_k]
    return hits

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--index_dir", default="vector_index")
    ap.add_argument("--top_k", type=int, default=5)
    args = ap.parse_args()

    print("🔄 载入模型与索引…")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    indexes, metas = load_all_indexes(args.index_dir)
    print(f"✅ 索引数: {len(indexes)}")

    while True:
        try:
            query = input("\n❓ 请输入查询（回车结束，Ctrl+C 退出）：").strip()
        except KeyboardInterrupt:
            break
        if not query: continue
        results = search(query, indexes, metas, model, args.top_k)
        print("\n🔍 最相似片段：")
        for i, (d, law, cid, snip) in enumerate(results, 1):
            print(f"{i:02d}. 距离={d:.4f} | {law} #chunk{cid} | {snip}")
