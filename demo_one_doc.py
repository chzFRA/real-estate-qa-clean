"""
demo_one_doc.py
---------------
在向量索引中检索目标句子，输出最相似的若干正文片段。
运行前请先安装：
    pip install sentence-transformers faiss-cpu pandas pyarrow numpy
"""

from pathlib import Path
import glob, faiss, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer

# === 路径配置 ===
VEC_DIR = Path("vector_index")                 # 保存 *.faiss / *_meta.parquet 的目录
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5                                      # 返回最相似的前 K 条

# === 加载句向量模型 ===
print("📥 正在加载 MiniLM 模型…")
model = SentenceTransformer(EMBED_MODEL)

# === 载入所有索引与元数据 ===
faiss_indexes = []
meta_dfs      = []

for faiss_path in VEC_DIR.glob("*.faiss"):
    meta_path = faiss_path.parent / f"{faiss_path.stem}_meta.parquet"
    if not meta_path.exists():
        print(f"⚠️  找不到元数据文件: {meta_path} (跳过该索引)")
        continue

    index = faiss.read_index(str(faiss_path))
    faiss_indexes.append(index)

    meta = pd.read_parquet(meta_path, engine="pyarrow")
    meta_dfs.append(meta)

print(f"✅ 已加载 {len(faiss_indexes)} 个 faiss 索引")

if not faiss_indexes:
    raise SystemExit("❌ 没有可用的索引，无法检索。")

# === 需要查询的文本 ===
query = input("请输入查询内容：").strip()
query_vec = model.encode([query]).astype("float32")

# === 检索 ===
hits = []  # (distance, snippet)

for index, meta in zip(faiss_indexes, meta_dfs):
    D, I = index.search(query_vec, TOP_K)  # D=距离, I=索引号
    for dist, ix in zip(D[0], I[0]):
        if ix == -1:
            continue                        # 该索引不足 TOP_K 条
        row     = meta.iloc[ix]
        snippet = row["chunk_text"][:120].replace("\n", " ") + "..."
        hits.append((dist, snippet))

if not hits:
    print("🤔 没找到任何匹配结果")
    raise SystemExit

# === 结果排序并打印 ===
hits = sorted(hits, key=lambda x: x[0])[:TOP_K]

print("\n🔍 最相似的片段：")
for rank, (dist, snippet) in enumerate(hits, 1):
    print(f"{rank:02d}. 距离={dist:.4f} | {snippet}")
