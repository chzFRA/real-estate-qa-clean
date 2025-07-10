import os
import re
import json

INPUT_DIR = "results"
OUTPUT_DIR = "mcq_clean"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_mcq_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"------ Chunk \d+ ------\s*Q: (.*?)\n\nA\. (.*?)\nB\. (.*?)\nC\. (.*?)\nD\. (.*?)\n\n正确答案: (\w)"
    matches = re.findall(pattern, content, re.DOTALL)

    extracted = []
    for match in matches:
        question = match[0].replace("\n", " ").strip()
        options = {"A": match[1].strip(), "B": match[2].strip(), "C": match[3].strip(), "D": match[4].strip()}
        correct_answer = match[5].strip().upper()
        extracted.append({
            "question": question,
            "options": options,
            "correct_answer": correct_answer
        })
    return extracted

for filename in os.listdir(INPUT_DIR):
    if filename.endswith("_mcq.txt"):
        data = extract_mcq_from_file(os.path.join(INPUT_DIR, filename))
        out_path = os.path.join(OUTPUT_DIR, filename.replace(".txt", ".json"))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已清洗：{filename} -> {out_path}")
