import os
import re
import shutil
from collections import Counter

INPUT_DIR = "texts_raw"
OUTPUT_DIR = "texts_clean"

# 清空旧的清洗结果
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def detect_repetitive_lines(texts):
    line_counter = Counter()
    for text in texts:
        for line in text.splitlines():
            line = line.strip()
            if len(line) > 3:
                line_counter[line] += 1
    common_lines = {line for line, count in line_counter.items() if count >= 3}
    return common_lines

def clean_text(text, repetitive_lines):
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if re.fullmatch(r"[-\s]*\d+[-\s]*", line):
            continue  # 页码
        if line in repetitive_lines:
            continue  # 页眉/页脚
        if line == "":
            continue  # 空行
        cleaned.append(line)
    return "\n".join(cleaned)

if __name__ == "__main__":
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".txt"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename.replace("_raw.txt", "_cleaned.txt"))

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            common_lines = detect_repetitive_lines([text])
            cleaned = clean_text(text, common_lines)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            print(f"✅ 已清理保存: {filename} -> {os.path.basename(output_path)}")
