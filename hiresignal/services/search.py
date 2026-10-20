"""搜索编排：聚合官方数据源 + AI 问答。"""

import json

from ..extract.llm import chat, chat_json
from ..providers import Company, DataProvider
from ..providers.jingdata import JingdataProvider
from ..providers.qcc import QccProvider


def build_providers() -> list[DataProvider]:
    """按配置构建可用 provider（有凭证的才启用）。"""
    providers: list[DataProvider] = []
    jd = JingdataProvider()
    if jd.ready:
        providers.append(jd)
    qcc = QccProvider()
    if qcc.api_key:
        providers.append(qcc)
    return providers


class SearchService:
    def __init__(self):
        self.providers = build_providers()

    # ---------- 搜索 ----------

    def search(self, keyword: str) -> list[dict]:
        """聚合搜索公司。"""
        results: dict[str, Company] = {}
        for p in self.providers:
            try:
                for c in p.search_company(keyword):
                    results.setdefault(c.name, c)
            except Exception as e:  # noqa: BLE001
                print(f"[search] provider {p.id} 失败: {e}")
        return [self._to_dict(c) for c in results.values()]

    def company_detail(self, name: str) -> dict | None:
        """聚合公司详情。"""
        merged = Company(name=name)
        for p in self.providers:
            try:
                c = p.get_company(name)
                if c:
                    merged = self._merge(merged, c)
            except Exception as e:  # noqa: BLE001
                print(f"[detail] provider {p.id} 失败: {e}")
        return self._to_dict(merged) if merged.source else None

    # ---------- AI 问答 ----------

    def ask(self, question: str) -> str:
        """自然语言问答：LLM 整理，可扩展为工具调用官方数据源。"""
        context = f"当前可用数据源：{', '.join(p.id for p in self.providers) or '无（未配置凭证）'}"
        return chat([
            {"role": "system", "content":
                "你是融资雷达（HireSignal）助手，帮求职者通过融资信号发现正在扩张的 startup。"
                f"{context}。数据未配置时如实说明，不编造。"},
            {"role": "user", "content": question},
        ])

    # ---------- 内部 ----------

    @staticmethod
    def _merge(a: Company, b: Company) -> Company:
        for f in ("name_cn", "full_name", "website", "industry", "founded", "description", "round"):
            if not getattr(a, f) and getattr(b, f):
                setattr(a, f, getattr(b, f))
        a.financing = a.financing or b.financing
        a.executives = a.executives or b.executives
        a.contacts = a.contacts or b.contacts
        if not a.source:
            a.source = b.source
        else:
            a.source = f"{a.source}+{b.source}"
        return a

    @staticmethod
    def _to_dict(c: Company) -> dict:
        return {
            "name": c.name,
            "name_cn": c.name_cn,
            "full_name": c.full_name,
            "website": c.website,
            "industry": c.industry,
            "founded": c.founded,
            "description": c.description,
            "round": c.round,
            "financing": c.financing,
            "executives": c.executives,
            "contacts": c.contacts,
            "source": c.source,
        }
