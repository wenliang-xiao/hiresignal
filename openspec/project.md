# Project Context

## 一句话

HireSignal（融资雷达）：用融资数据锁定「有钱且在扩张」的 startup，用公开渠道直连「能拍板的人」，面向校招/社招求职者的定向求职工具。

## 定位与差异化

| 渠道 | 痛点 | HireSignal 解法 |
|------|------|----------------|
| 内推 | 吃人脉资源 | 不需要人脉，直接 cold outreach |
| 招聘软件（BOSS/猎聘） | 被动海投、HR 筛选、定向不准 | 主动定向、直连决策者 |
| 猎头 | 服务高端、收费 | 免费、服务所有人 |

**核心洞察**：融资的钱主要花在「招人」上。「近期融资」是最前瞻的招聘扩张信号。

## 目标用户

- 校招 / 社招求职者（免费使用）
- 变现方：正在招聘的 startup（雇主付费）、招聘相关服务商（广告）

## 技术栈

- 语言：Python 3.12+
- Web：FastAPI + 原生前端（无框架，MVP）
- LLM：OpenAI 兼容接口（本地开发用内网 mify）
- MCP 客户端：`mcp` SDK（streamable HTTP）
- 存储：SQLite（后续 PostgreSQL / ES）

## 关键约定

1. **凭证一律走环境变量**（`.env`，绝不硬编码、绝不提交）。
2. **数据层只走官方 API/MCP**，不自建爬虫（见 [ADR-0002](./decisions/0002-official-mcp-over-crawler.md)）。
3. **每次代码变更同步更新 OpenSpec 文档**。
4. Git 规范：commit message 用英文（GitHub 开源项目）。

## 常用命令

```bash
# 安装与启动
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 启动 Web 服务
python scripts/run_web.py        # http://127.0.0.1:8000

# 探测企查查 MCP 工具清单
python scripts/probe_qcc.py
```
