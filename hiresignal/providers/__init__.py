"""数据源抽象：官方 API / MCP 优先，稳定可审计。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Company:
    """公司（统一模型，由各 provider 映射）。"""

    name: str
    name_cn: str | None = None
    full_name: str | None = None
    website: str | None = None
    industry: str | None = None
    founded: str | None = None
    description: str | None = None
    round: str | None = None  # 最近融资轮次
    financing: list[dict] = field(default_factory=list)  # 融资历史
    executives: list[dict] = field(default_factory=list)  # 决策者 {name, title}
    contacts: list[dict] = field(default_factory=list)  # {type, value}
    source: str = ""


class DataProvider(ABC):
    """数据源统一接口。"""

    id: str

    @abstractmethod
    def search_company(self, keyword: str) -> list[Company]:
        """按关键词搜索公司。"""

    @abstractmethod
    def get_company(self, name: str) -> Company | None:
        """按名称获取公司详情。"""
