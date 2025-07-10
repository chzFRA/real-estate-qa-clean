"""
build_index_incremental.py
--------------------------
扫描 texts_clean/ 下的 *_cleaned.txt，
为每个文件构建 Faiss 向量索引，并把
   - chunk_text
   - doc (文件 id)
   - chunk_id
保存到同名 *_meta.parquet。
重复执行会自动跳过已存在的 .faiss（除非设置 FORCE_REBUILD）。
"""

from pathlib import Path
import faiss, json, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ==== 配置 ====
TXT_DIR       = Path("texts_clean")
INDEX_DIR     = Path("vector_index")
EMBED_MODEL   = "paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_LEN     = 200          # 与之前保持一致
FORCE_REBUILD = True         # True=无条件重建，False=已存在则跳过

INDEX_DIR.mkdir(exist_ok=True)
model = SentenceTransformer(EMBED_MODEL)

def build_index_for_file(txt_path: Path):
    fname = txt_path.stem                           # e.g. 096be8ed81xxxx_cleaned
    faiss_path = INDEX_DIR / f"{fname}.faiss"
    meta_path  = INDEX_DIR / f"{fname}_meta.parquet"

    if not FORCE_REBUILD and faiss_path.exists() and meta_path.exists():
        return

    # --- 读文本并切块 ---
    chunks = []
    with txt_path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            # 很简单地每 CHUNK_LEN 字符一块
            for start in range(0, len(line), CHUNK_LEN):
                chunk = line[start : start + CHUNK_LEN]
                chunks.append({"chunk_text": chunk,
                               "doc": fname,
                               "chunk_id": len(chunks)})

    if not chunks:
        print(f"⚠️  {fname} 无内容，跳过")
        return

    # --- 向量化 ---
    texts   = [c["chunk_text"] for c in chunks]
    vectors = model.encode(texts, batch_size=64, show_progress_bar=True).astype("float32")

    # --- 写 Faiss ---
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(vectors)
    index.add(vectors)
    faiss.write_index(index, str(faiss_path))

    # --- 写 meta ---
    pd.DataFrame(chunks).to_parquet(meta_path, engine="pyarrow")

    print(f"🎉 完成 {fname}：{len(chunks)} 向量 -> {faiss_path.name}")

def main():
    txt_files = sorted(TXT_DIR.glob("*_cleaned.txt"))
    print(f"📚 共 {len(txt_files)} 个待处理文件\n")
    for f in tqdm(txt_files, desc="文件进度"):
        build_index_for_file(f)
    print("🏁 全部法规处理完成！")

if __name__ == "__main__":
    main()
