# build_index_stream.py
"""
逐文件→逐 batch 写 FAISS，避免一次吃光内存
依赖: pip install sentence-transformers faiss-cpu pandas tqdm
"""

import os, glob, json, gc
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss

TXT_DIR   = "texts_clean"
INDEX_DIR = "vector_index"
os.makedirs(INDEX_DIR, exist_ok=True)

CHUNK_SIZE = 800      # 字符
OVERLAP    = 100
BATCH_SIZE = 64       # 向量化 batch

def lazy_chunk(text):
    """生成器：按 CHUNK_SIZE 滑窗切片，yield chunk 字符串"""
    start = 0
    ln = len(text)
    while start < ln:
        end = min(start + CHUNK_SIZE, ln)
        yield text[start:end]
        start = end - OVERLAP

# ---------- 初始化 FAISS ----------
model = SentenceTransformer("BAAI/bge-base-zh")
d = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(d)          # 也可以换成 IndexHNSWFlat 等

# 在这同时把元数据写 parquet（追加式）
meta_path = os.path.join(INDEX_DIR, "meta.parquet")
meta_df_list = []

# ---------- 逐文件流式处理 ----------
for txt_path in tqdm(glob.glob(os.path.join(TXT_DIR, "*.txt"))):
    with open(txt_path, encoding="utf-8") as f:
        text = f.read()
    basename = os.path.basename(txt_path)

    # 按 batch 做 embedding
    buffer = []
    meta_buffer = []
    for i, chunk in enumerate(lazy_chunk(text)):
        buffer.append(chunk)
        meta_buffer.append({"doc": basename, "chunk_id": i})
        # 满一个 batch 或最后一个 chunk 时 flush
        if len(buffer) == BATCH_SIZE or (i == 0 and len(text) < CHUNK_SIZE):
            print(f"🧠 正在编码 {basename} 中的第 {i+1} 块，共 {len(buffer)} 条...")
            embs = model.encode(buffer, batch_size=len(buffer))
            index.add(embs)
            meta_df_list.extend(meta_buffer)
            buffer.clear()
            meta_buffer.clear()
            gc.collect()

    # flush 余下不足 batch 的
    if buffer:
        embs = model.encode(buffer, batch_size=len(buffer))
        index.add(embs)
        meta_df_list.extend(meta_buffer)
        buffer.clear()
        meta_buffer.clear()
        gc.collect()

# ---------- 保存索引和元数据 ----------
faiss.write_index(index, os.path.join(INDEX_DIR, "legal_index.faiss"))
pd.DataFrame(meta_df_list).to_parquet(meta_path, index=False)
print(f"🎉 索引完成！共 {index.ntotal} 条向量，元数据已写 {meta_path}")
