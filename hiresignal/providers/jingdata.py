"""鲸准 MCP Provider：一级市场创投数据（融资事件/创业公司/团队背景/行业）。

鲸准（36氪/海创汇旗下）将一级市场投融资数据库封装为标准 MCP http 服务，
覆盖：融资事件 42万+、创业项目 110万+、公司团队背景、行业标签 1.5万、
工商、投资机构、基金/LP、产业链。

获取方式：商务洽谈（https://www.jingdata.com/data-service/mcp/），
凭发放的访问令牌（Bearer Token）接入，服务地址以鲸准文档为准。

配置（环境变量）：
    JINGDATA_MCP_URL   MCP 服务地址
    JINGDATA_TOKEN     访问令牌
"""

import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv

from . import Company, DataProvider

load_dotenv()


class JingdataProvider(DataProvider):
    id = "jingdata"

    def __init__(self, url: str | None = None, token: str | None = None):
        self.url = url or os.getenv("JINGDATA_MCP_URL", "")
        self.token = token or os.getenv("JINGDATA_TOKEN", "")

    @property
    def ready(self) -> bool:
        return bool(self.url and self.token)

    async def _call(self, tool: str, arguments: dict[str, Any]) -> Any:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with streamable_http_client(
            self.url,
            http_client=httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.token}"}, timeout=30
            ),
        ) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool, arguments)

    def _call_sync(self, tool: str, arguments: dict[str, Any]) -> Any:
        return asyncio.run(self._call(tool, arguments))

    def _list_tools(self) -> list:
        async def _go():
            from mcp import ClientSession
            from mcp.client.streamable_http import streamable_http_client

            async with streamable_http_client(
                self.url,
                http_client=httpx.AsyncClient(
                    headers={"Authorization": f"Bearer {self.token}"}, timeout=30
                ),
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    r = await session.list_tools()
                    return list(r.tools)

        return asyncio.run(_go())

    def search_company(self, keyword: str) -> list[Company]:
        """按行业/赛道/城市/关键词找创业公司。"""
        if not self.ready:
            return []
        # 工具名以接入文档为准，先动态发现含 search/company 的工具
        try:
            tools = [t.name for t in self._list_tools()]
        except Exception:  # noqa: BLE001
            tools = []
        tool = next((t for t in tools if "search" in t or "company" in t), tools[0] if tools else "search_company")
        try:
            res = self._call_sync(tool, {"keyword": keyword})
        except Exception:  # noqa: BLE001
            return []
        return [Company(name=keyword, description=str(res), source="jingdata")]

    def get_company(self, name: str) -> Company | None:
        """获取创业公司详情（画像 + 团队背景 + 融资历史）。"""
        if not self.ready:
            return None
        comp = Company(name=name, source="jingdata")
        try:
            tools = [t.name for t in self._list_tools()]
        except Exception:  # noqa: BLE001
            tools = []
        # 公司详情 + 融资 + 团队，工具名以文档为准
        for hint, field in (("company", "description"), ("financ", "financing"), ("team", "executives")):
            tool = next((t for t in tools if hint in t), None)
            if not tool:
                continue
            try:
                res = self._call_sync(tool, {"company_name": name})
                if field == "financing":
                    comp.financing = [{"raw": str(res)}]
                elif field == "executives":
                    comp.executives = [{"name": "", "title": "", "raw": str(res)}]
                else:
                    comp.description = str(res)
            except Exception:  # noqa: BLE001
                continue
        return comp
