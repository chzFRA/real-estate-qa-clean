import os
from llm_utils import call_model

# 自动选取 texts_clean 文件夹下第一个 .txt 文件
INPUT_DIR = "texts_clean"
def find_first_txt_file(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            return os.path.join(input_dir, filename)
    return None

# 读取一个 txt 文件，取前 2000 字
def load_sample_chunk(filepath, max_len=2000):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return text[:max_len]

def main():
    test_txt_path = find_first_txt_file(INPUT_DIR)
    if not test_txt_path:
        print("❌ 未在 texts_clean 文件夹中找到任何 .txt 文件！")
        return

    print(f"🔍 正在读取文件：{test_txt_path}")
    chunk = load_sample_chunk(test_txt_path)

    # 构造提示词
    prompt = f"""你是一名法律专家,阅读以下法律法规条文,生成3个普通房地产用户可能会问的问题,并对每个问题根据条文进行专业、简洁的回答,回答不要死板并且体现出diversity和个性化。

条文如下：
{chunk}

请输出如下格式：
Q1: ...
A1: ...
Q2: ...
A2: ...
Q3: ...
A3: ...
"""

    print("\n📨 正在调用模型生成问答...")
    result = call_model(prompt, model="deepseek")
    print("\n📋 模型返回内容如下：\n")
    print(result)

if __name__ == "__main__":
    main()
