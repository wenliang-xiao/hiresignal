# 系统架构（Architecture）

## 分层

```
数据层 providers/          官方 MCP 优先，稳定可审计
 ├── jingdata.py           鲸准 MCP（融资事件/创业公司/团队背景/行业）
 └── qcc.py                企查查 MCP（工商/高管/官网/风险）
        │
服务层 services/           搜索编排 + AI 问答
 ├── search.py             SearchService：聚合 provider + LLM 问答
        │
展示层 web/                FastAPI + 原生前端
 ├── app.py                REST API + 静态页
 └── static/index.html     搜索页（原生 HTML/JS/CSS）
```

## 数据流

```
用户输入（搜索词 / 自然语言问题）
   → services.SearchService
      ├── 搜索：遍历 providers.search_company() 聚合
      ├── 详情：遍历 providers.get_company() 合并
      └── 问答：LLM 整理（可扩展为 MCP 工具调用）
   → FastAPI JSON 响应
   → 前端渲染
```

## 统一模型

`providers.Company`：所有 provider 的返回统一映射为该模型，字段：
`name / name_cn / full_name / website / industry / founded / description / round / financing[] / executives[] / contacts[] / source`

## 关键接口（REST）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 搜索页 |
| GET | `/api/status` | 数据源就绪状态 |
| GET | `/api/search?q=` | 公司搜索 |
| GET | `/api/company?name=` | 公司详情 |
| POST | `/api/ask` | AI 问答 |

## 扩展方向（P2/P3）

- 存储：SQLite → PostgreSQL + Elasticsearch（搜索）+ 图库（关系图谱）。
- 缓存：本地缓存官方数据，节省 API 积分。
- 结构化：MCP 返回的文本 → 结构化字段（融资历史、决策者卡片）。
