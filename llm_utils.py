import os
import time
from dotenv import load_dotenv
import openai
import anthropic

load_dotenv()

# 模型映射表
MODEL_CONFIG = {
    "gpt3.5": {
        "provider": "openai",
        "model_id": "gpt-3.5-turbo",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1"
    },
    "claude": {
        "provider": "anthropic",
        "model_id": "claude-3-opus-20240229",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
    },
    "deepseek": {
        "provider": "openai",
        "model_id": "deepseek-chat",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com"
    },
    "gpt4": {
        "provider": "openai",
        "model_id": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1"
    }
}


def call_model(prompt, model="gpt3.5", temperature=0.7, max_tokens=1024):
    cfg = MODEL_CONFIG[model]

    # ---------- OpenAI / DeepSeek ----------
    if cfg["provider"] == "openai":
        client = openai.OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])

        # 自动重试（速率或网络错）——最多 5 次
        for retry in range(5):
            try:
                resp = client.chat.completions.create(
                    model=cfg["model_id"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return resp.choices[0].message.content

            except openai.RateLimitError as e:
                wait = 5 + retry * 5          # 5s, 10s, 15s, ...
                print(f"⏳ RateLimit（{model}）第 {retry+1}/5 次重试，等待 {wait}s")
                time.sleep(wait)
            except openai.APIError as e:
                wait = 3
                print(f"⚠️ OpenAI APIError：{e}. {wait}s 后重试 ({retry+1}/5)")
                time.sleep(wait)
            except Exception as e:
                # 其他错误直接抛，让主程序决定
                print(f"❌ OpenAI 其它错误：{e}")
                raise
        # 全部失败
        raise RuntimeError("❌ OpenAI 连续 5 次重试仍失败")

    # ---------- Anthropic / Claude ----------
    elif cfg["provider"] == "anthropic":
        client = anthropic.Anthropic(api_key=cfg["api_key"])
        resp = client.messages.create(
            model=cfg["model_id"],
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp.content[0].text

    else:
        raise ValueError(f"Unsupported provider: {cfg['provider']}")