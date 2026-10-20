"""融资事件 + 决策者抽取：LLM 将新闻/公告文本结构化。"""

from .llm import chat_json

SYSTEM_PROMPT = """你是一名一级市场数据标注专家。从给定的中文融资新闻文本中，抽取结构化信息。

严格要求：
1. 只输出一个 JSON 对象，不要输出任何解释、markdown 或多余文本。
2. 字段说明：
   - company_name: 被投资公司全称（优先工商名，其次品牌名）
   - company_name_cn: 中文名
   - round: 融资轮次，取值仅限：种子轮/天使轮/Pre-A轮/A轮/A+轮/B轮/C轮/D轮/E轮/战略投资/并购/其他/未知
   - amount_text: 金额原文表述（如"数千万""近亿元""5000万元"），没有则 null
   - amount_cny: 折算为人民币的金额（单位：万元，数字），无法确定则 null
   - currency: 币种（CNY/USD/其他）
   - investors: 投资方列表（数组），领投方放第一位
   - lead_investor: 领投方（字符串或 null）
   - announce_date: 融资公布日期，格式 YYYY-MM-DD，无法确定则 null
   - industry: 所属行业/赛道（如"人工智能""半导体"）
   - is_funding: 是否是融资事件（true/false），非融资新闻（如产品发布、财报）返回 false
   - decision_makers: 决策者数组，从文中/公司背景中识别 CEO/CTO/联合创始人等 director 以上角色，
     每项为 {name: 姓名, title: 职位, contact: 公开联系方式或 null}
3. 无法确定的字段填 null，不要编造。
"""


def extract_funding_event(text: str, source_url: str = "", keywords: list[str] | None = None) -> dict:
    """从新闻文本抽取融资事件。返回结构化 dict。"""
    kw_hint = ""
    if keywords:
        kw_hint = f"\n参考赛道关键词：{', '.join(keywords[:30])}"
    user_prompt = f"来源：{source_url}\n{kw_hint}\n\n新闻文本：\n{text[:6000]}"
    result = chat_json(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )
    result.setdefault("source_url", source_url)
    return result
