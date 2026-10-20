"""LLM 封装：OpenAI 兼容接口，用于融资事件/决策者抽取。"""

import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=os.getenv("LLM_BASE_URL", "http://model.mify.ai.srv/v1/"),
            api_key=os.getenv("LLM_API_KEY", ""),
        )
    return _client


def get_model() -> str:
    return os.getenv("LLM_MODEL", "deepseek/deepseek-v4-flash")


def chat(messages: list[dict], temperature: float = 0.1, max_tokens: int = 2000) -> str:
    """调用 chat completion，返回文本内容。"""
    resp = get_client().chat.completions.create(
        model=get_model(),
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def chat_json(messages: list[dict], temperature: float = 0.1, max_tokens: int = 2000) -> dict:
    """调用并要求返回 JSON，容错解析（剥离 ```json 围栏 / 提取首个 {...}）。"""
    text = chat(messages, temperature=temperature, max_tokens=max_tokens)
    # 剥离 markdown 代码围栏
    text = re.sub(r"```(?:json)?", "", text).strip()
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 提取首个 JSON 对象
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"LLM 未返回合法 JSON：{text[:200]}")
