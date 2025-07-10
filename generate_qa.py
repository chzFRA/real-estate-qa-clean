import os
import json
from llm_utils import call_model

INPUT_DIR = "texts_clean"
OUTPUT_DIR = "results"
ERROR_LOG = "error.log"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 分块函数：尽量在句子边界切断
def chunk_text(text, max_chunk_size=2000):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chunk_size, len(text))
        while end < len(text) and text[end] not in ".。！？\n":
            end += 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks

# 选择题 prompt
def generate_mcq(chunk, model="deepseek"):
    prompt = f"""你是一名法律考试题库设计专家。请阅读以下有关于房地产的法律条文,设计1道选择题,要求如下：

1. 问题贴近普通房地产用户可能会问的问题；
2. 给出4个选项(A/B/C/D),其中一个是正确答案，其余为干扰项；
3. 所有选项必须基于条文内容；
4. 指出哪一个选项是正确答案；
5. 使用简洁清晰的语言,不要死板并且体现出diversity和个性化。

以下是法律条文：
{chunk}

请用如下格式输出：
Q: ...
A. ...
B. ...
C. ...
D. ...
正确答案: X
"""
    return call_model(prompt, model=model)

# 主流程
if __name__ == "__main__":
    model = "deepseek"

    with open(ERROR_LOG, "w", encoding="utf-8") as log:
        for filename in os.listdir(INPUT_DIR):
            if not filename.endswith(".txt"):
                continue

            input_path = os.path.join(INPUT_DIR, filename)
            base_name = filename.replace(".txt", f"_{model}_mcq")
            output_txt = os.path.join(OUTPUT_DIR, base_name + ".txt")
            output_json = os.path.join(OUTPUT_DIR, base_name + ".json")

            if os.path.exists(output_txt) and os.path.exists(output_json):
                print(f"⚠️ 已存在，跳过：{base_name}")
                continue

            with open(input_path, "r", encoding="utf-8") as f:
                full_text = f.read()

            chunks = chunk_text(full_text)
            results = []

            for i, chunk in enumerate(chunks):
                print(f"\n📦 正在处理 {filename} 的第 {i+1} 块文本...")
                try:
                    mcq = generate_mcq(chunk, model=model)
                    results.append({
                        "chunk_id": i,
                        "mcq_text": mcq,
                        "source": chunk.strip()[:100] + "..."
                    })
                except Exception as e:
                    err_msg = f"❌ 出错文件 {filename}，块 {i}，原因：{e}\n"
                    print(err_msg)
                    log.write(err_msg)

            # 保存纯文本
            with open(output_txt, "w", encoding="utf-8") as f:
                for r in results:
                    f.write(f"------ Chunk {r['chunk_id']} ------\n")
                    f.write(r['mcq_text'] + "\n\n")
            print(f"✅ 已保存纯文本选择题：{output_txt}")

            # 保存结构化 JSON
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存结构化 JSON：{output_json}")
