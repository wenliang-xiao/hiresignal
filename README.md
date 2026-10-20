# HireSignal · 融资雷达

> 用融资数据锁定「有钱且在扩张」的 startup，直连能拍板的人。

> 📘 **开发者/模型请先读 [OpenSpec](./openspec/README.md)**：项目规格、架构、决策记录均沉淀在此，保证交接一致。

面向校招/社招求职者的**定向求职工具**：搜索国内按行业分类的「近期 X 轮融资」公司，识别 CEO/CTO/director 以上决策者，聚合公开联系方式，帮你主动触达，实现「双向奔赴」。

## 为什么是它

| 渠道 | 痛点 | HireSignal 解法 |
|------|------|----------------|
| 内推 | 吃人脉资源 | 不需要人脉，直接 cold outreach |
| 招聘软件（BOSS/猎聘） | 被动海投、HR 筛选、定向不准 | 主动定向、直连决策者 |
| 猎头 | 服务高端、收费 | 免费、服务所有人 |

**核心洞察**：融资的钱主要花在「招人」上。「近期融资」是最前瞻的招聘扩张信号，比招聘软件的在招岗位列表更早、更准。

## 数据层：官方 API / MCP 优先（稳定数据源）

> 自建爬虫反爬/改版/断源/合规风险高，不是产品命根。**稳定数据源走官方能力**。

| 数据源 | 覆盖 | 官方能力 | 获取 |
|--------|------|---------|------|
| **鲸准**（36氪/海创汇） | 融资事件 42万+、创业项目 110万+、团队背景、行业标签、机构/基金/LP | MCP + API + SKILL | 商务洽谈 `jingdata.com/data-service/mcp/` |
| **企查查** | 工商、高管、官网、风险、知产 | MCP（10 个 server）+ API | 自助注册 `agent.qcc.com`，**注册即领 500 积分+每日赠送** |

- 融资信号 + 决策者（团队背景）→ 鲸准 MCP
- 工商 + 官网 + 高管 → 企查查 MCP（`qcc-company` / `qcc-executive`）

## 架构

```
数据层 providers/         官方 MCP 优先，稳定可审计
 ├── jingdata.py          鲸准 MCP（融资事件/创业公司/团队背景）
 └── qcc.py               企查查 MCP（工商/高管/官网）
        │
服务层 services/search.py  搜索编排 + AI 问答（LLM）
        │
展示层 web/                FastAPI + 原生前端
```

## 目录结构

```
hiresignal/
├── hiresignal/
│   ├── providers/         # 官方数据源（MCP）
│   ├── services/          # 搜索编排 + AI 问答
│   ├── extract/llm.py     # LLM 封装
│   ├── store/db.py        # 本地缓存（可选）
│   └── web/               # FastAPI + 前端
└── scripts/run_web.py     # 启动入口
```

## 快速开始

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 填 LLM + 鲸准/企查查凭证

python scripts/run_web.py   # 打开 http://127.0.0.1:8000
```

**凭证获取**：
- 企查查：注册 `agent.qcc.com` → 接入指南 → 获取 API Key（免费积分可立刻验证）
- 鲸准：`jingdata.com/data-service/mcp/` 联系获取访问令牌（覆盖融资事件+团队背景，核心源）

未配置凭证时，搜索返回空、AI 问答可用（会如实说明数据未接入）。

## 路线图

- **P1（当前）**：官方 MCP 数据层 + Web 搜索页 + AI 问答。
- **P2**：搜索结果结构化（融资历史、决策者卡片、联系方式聚合）、本地缓存省积分。
- **P3**：订阅推送、雇主侧招聘曝光（双边变现）、API 开放。

## License

[MIT](./LICENSE) © 2026 Wenliang Xiao
