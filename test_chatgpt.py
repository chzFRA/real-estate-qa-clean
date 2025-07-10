""" import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    messages = [
        {"role": "user", "content": "你好，能简单介绍一下你是做什么的吗？"}
    ]

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )

    print("模型回复：", response.choices[0].message.content)

if __name__ == "__main__":
    main()
 """

""" import anthropic

client = anthropic.Anthropic(api_key="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")

response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    temperature=0.7,
    messages=[
        {"role": "user", "content": "请简要介绍房地产开发中土地使用权的政策风险。"}
    ]
)

print(response.content[0].text)
 """

import openai
import os

# 从环境变量中读取 DeepSeek 的 API Key
openai.api_key = "sk-b20bb03245cb4d409fdcae34f560a801"
openai.base_url = "https://api.deepseek.com"  # ✅ 注意是 DeepSeek 的地址

def main():
    messages = [
        {"role": "user", "content": "你好，能简单介绍一下你是做什么的吗？"}
    ]

    response = openai.chat.completions.create(
        model="deepseek-chat",  # 或者 "deepseek-coder"
        messages=messages,
        temperature=0.7,
        max_tokens=1024
    )

    print("模型回复：", response.choices[0].message.content)

if __name__ == "__main__":
    main()


