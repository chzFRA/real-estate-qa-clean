"""
check_meta_columns.py
---------------------
检查向量索引目录中所有 *_meta.parquet 文件的列名。
"""

import os
import glob
import pandas as pd

# 向量索引所在目录——按你的项目结构调整
VEC_DIR = "vector_index"          # 例如 E:/code/thesis/legal_crawler/vector_index

# 找到所有 *_meta.parquet 文件
meta_paths = sorted(glob.glob(os.path.join(VEC_DIR, "*_meta.parquet")))

if not meta_paths:
    print(f"❌ 在 {VEC_DIR} 里没有找到任何 *_meta.parquet 文件，请确认路径。")
    raise SystemExit

print(f"🔍 共检测到 {len(meta_paths)} 个 meta 文件：\n")

for path in meta_paths:
    try:
        meta = pd.read_parquet(path, engine="pyarrow")  # 如果没装 pyarrow, pip install pyarrow
    except Exception as e:
        print(f"⚠️  读取 {os.path.basename(path)} 失败：{e}")
        continue

    cols = list(meta.columns)
    print(f"📄 {os.path.basename(path)} — 列名: {cols}")

print("\n✅ 列名检查完毕！")
