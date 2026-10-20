"""企查查 MCP Provider：工商数据 + 高管（决策者）+ 风险校验。

企查查智能体数据平台（agent.qcc.com）提供标准 MCP http stream 接口，
注册即领 500 积分，每日赠送。API Key 登录后于 /profile/api-key 获取。

接入示例（Bearer 鉴权）：
    qcc-company   -> https://agent.qcc.com/mcp/company/stream   企业数据
    qcc-executive -> https://agent.qcc.com/mcp/executive/stream 高管
    qcc-risk      -> https://agent.qcc.com/mcp/risk/stream      风险
    qcc-ipr       -> https://agent.qcc.com/mcp/ipr/stream       知识产权
"""

import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv

from . import Company, DataProvider

load_dotenv()

QCC_SERVERS = {
    "company": "https://agent.qcc.com/mcp/company/stream",
    "executive": "https://agent.qcc.com/mcp/executive/stream",
    "risk": "https://agent.qcc.com/mcp/risk/stream",
    "ipr": "https://agent.qcc.com/mcp/ipr/stream",
}


class QccProvider(DataProvider):
    id = "qcc"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("QCC_API_KEY", "")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def _call(self, server: str, tool: str, arguments: dict[str, Any]) -> Any:
        """调用企查查 MCP 工具。"""
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        url = QCC_SERVERS[server]
        async with streamable_http_client(
            url, http_client=httpx.AsyncClient(headers=self._headers(), timeout=30)
        ) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments)
                return result

    def _call_sync(self, server: str, tool: str, arguments: dict[str, Any]) -> Any:
        return asyncio.run(self._call(server, tool, arguments))

    def _to_text(self, result: Any) -> str:
        """把 CallToolResult 转成文本。"""
        for c in getattr(result, "content", []):
            if getattr(c, "type", "") == "text":
                return c.text
        return str(result)

    # ---------- 企业数据 ----------

    def search_company(self, keyword: str) -> list[Company]:
        """按关键词查企业（qcc-company 的实体识别/搜索工具）。"""
        # 先尝试列出工具，找到搜索/基础信息工具
        try:
            tools = self._list_tools("company")
        except Exception:  # noqa: BLE001
            tools = []
        search_tool = None
        for t in tools:
            if any(k in t.name for k in ("search", "basic", "info", "entity")):
                search_tool = t.name
                break
        if search_tool is None:
            search_tool = "search_company"  # 兜底猜测
        res = self._call_sync("company", search_tool, {"keyword": keyword})
        # 解析略：以文本形式暂存，交由上层结构化
        return [Company(name=keyword, description=self._to_text(res), source="qcc")]

    def _list_tools(self, server: str) -> list:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async def _go():
            url = QCC_SERVERS[server]
            async with streamable_http_client(
                url, http_client=httpx.AsyncClient(headers=self._headers(), timeout=30)
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    r = await session.list_tools()
                    return list(r.tools)

        return asyncio.run(_go())

    def get_company(self, name: str) -> Company | None:
        """获取公司详情（工商 + 高管 + 官网）。"""
        comp = Company(name=name, source="qcc")
        try:
            comp.description = self._get_basic_info(name)
        except Exception as e:  # noqa: BLE001
            comp.description = f"[企业信息获取失败: {e}]"
        try:
            comp.executives = self._get_executives(name)
        except Exception as e:  # noqa: BLE001
            comp.executives = [{"name": "", "title": f"[高管获取失败: {e}]"}]
        return comp

    def _get_basic_info(self, name: str) -> str:
        res = self._call_sync("company", "get_basic_info", {"company_name": name})
        return self._to_text(res)

    def _get_executives(self, name: str) -> list[dict]:
        res = self._call_sync("executive", "get_executives", {"company_name": name})
        # 高管结果通常为文本/JSON，此处先以文本返回，上层可再结构化
        text = self._to_text(res)
        return [{"name": name, "title": "高管", "raw": text}] if text else []
