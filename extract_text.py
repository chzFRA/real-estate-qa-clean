import os
import json
import fitz

CONFIG_PATH = "page_ranges.json"
INPUT_DIR = "pdfs"
OUTPUT_DIR = "texts_raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载页码提取配置
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        page_config = json.load(f)
else:
    page_config = {}

def extract_text_from_pdf(pdf_path: str, ranges=None) -> str:
    doc = fitz.open(pdf_path)
    all_text = []

    if ranges is None:
        ranges = [[1, len(doc)]]

    for start, end in ranges:
        for i in range(start - 1, min(end, len(doc))):
            text = doc[i].get_text()
            all_text.append(text)
    
    return "\n".join(all_text)

def save_text_to_file(text: str, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".pdf"):
            try:
                pdf_path = os.path.join(INPUT_DIR, filename)
                txt_filename = filename.replace(".pdf", "_raw.txt")
                output_path = os.path.join(OUTPUT_DIR, txt_filename)

                if filename in page_config:
                    ranges = page_config[filename]
                    print(f"📄 {filename} => 多段页码提取: {ranges}")
                else:
                    ranges = None
                    print(f"📄 {filename} => 全文提取")

                extracted = extract_text_from_pdf(pdf_path, ranges=ranges)
                save_text_to_file(extracted, output_path)
                print(f"✅ 已提取 {filename} -> {txt_filename}")
            except Exception as e:
                print(f"❌ 处理失败 {filename}: {e}")
