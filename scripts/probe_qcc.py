"""探测企查查 MCP 工具清单（校准 providers/qcc.py 的工具名）。

用法：
    export QCC_API_KEY=xxx   # 或写入 .env
    python scripts/probe_qcc.py
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.streamable_http import streamable_http_client  # noqa: E402

load_dotenv()

SERVERS = {
    "company": "https://agent.qcc.com/mcp/company/stream",
    "executive": "https://agent.qcc.com/mcp/executive/stream",
    "risk": "https://agent.qcc.com/mcp/risk/stream",
    "ipr": "https://agent.qcc.com/mcp/ipr/stream",
    "operation": "https://agent.qcc.com/mcp/operation/stream",
    "history": "https://agent.qcc.com/mcp/history/stream",
}


async def probe(name: str, url: str, api_key: str):
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with streamable_http_client(
            url, http_client=httpx.AsyncClient(headers=headers, timeout=30)
        ) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print(f"\n=== [{name}] {len(tools.tools)} 个工具 ===")
                for t in tools.tools:
                    desc = (t.description or "").replace("\n", " ")[:80]
                    print(f"  • {t.name}")
                    if desc:
                        print(f"      {desc}")
                    # 打印入参 schema 的关键字段
                    schema = getattr(t, "inputSchema", None) or {}
                    props = schema.get("properties", {}) if isinstance(schema, dict) else {}
                    if props:
                        print(f"      参数: {', '.join(list(props.keys())[:8])}")
    except BaseException as e:
        def walk(ex):
            if hasattr(ex, "exceptions"):
                for sub in ex.exceptions:
                    walk(sub)
            else:
                print(f"\n=== [{name}] ❌ {type(ex).__name__}: {str(ex)[:200]}")
        walk(e)


async def main():
    api_key = os.getenv("QCC_API_KEY", "")
    if not api_key:
        print("❌ 未配置 QCC_API_KEY。请先到 https://agent.qcc.com 获取，写入 .env 或环境变量。")
        sys.exit(1)
    for name, url in SERVERS.items():
        await probe(name, url, api_key)


if __name__ == "__main__":
    asyncio.run(main())
