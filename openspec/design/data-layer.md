# 数据层设计（Data Layer）

> 数据是产品命根。**稳定 > 便宜 > 全量**。核心原则：官方 API/MCP 优先，不自建爬虫。

## 数据源全景（已调研验证）

| 数据源 | 覆盖 | 官方能力 | 获取方式 | 角色 |
|--------|------|---------|---------|------|
| **鲸准**（36氪/海创汇） | 融资事件 42万+、创业项目 110万+、团队背景、行业标签 1.5万、工商、机构/基金/LP、产业链 | MCP + API + SKILL | 商务洽谈 `jingdata.com/data-service/mcp/` | **核心源**：融资信号 + 决策者 |
| **企查查** | 工商、高管、官网、风险、知产 | MCP（10 个 server）+ API | 自助注册 `agent.qcc.com`，注册即领 500 积分 | 补充：工商 + 高管 + 官网 |

## 数据映射

| 产品需要的数据 | 来源 |
|--------------|------|
| 融资信号（近期 X 轮融资，按行业） | 鲸准 MCP（融资事件） |
| 创业公司列表（按赛道/城市/行业） | 鲸准 MCP（创业公司） |
| 决策者（CEO/CTO/director 以上） | 鲸准（团队背景）+ 企查查（qcc-executive 高管） |
| 工商基础信息（注册资本/成立时间/经营范围） | 企查查（qcc-company） |
| 官网 / 联系方式 | 企查查（官网字段）+ 官网公开邮箱 |

## MCP 接口详情

### 企查查（agent.qcc.com）

标准 MCP http stream + Bearer Token，10 个 server：

| server | 端点 | 用途 |
|--------|------|------|
| qcc-company | `agent.qcc.com/mcp/company/stream` | 企业数据（工商/股东） |
| qcc-executive | `agent.qcc.com/mcp/executive/stream` | **高管** |
| qcc-risk | `agent.qcc.com/mcp/risk/stream` | 风险 |
| qcc-ipr | `agent.qcc.com/mcp/ipr/stream` | 知识产权 |
| 其他 | operation / history / regulation / case / tender / document | 经营/历史/法务/标讯/文档 |

### 鲸准（jingdata.com）

标准 MCP http + Bearer Token（服务地址以文档为准，商务洽谈发放）：

```json
{ "mcpServers": { "jingdata": { "type": "http", "url": "<服务地址>", "headers": { "Authorization": "Bearer <访问令牌>" } } } }
```

覆盖 8 类数据：融资事件、创业公司、企业工商、投资机构、基金与 LP、行业赛道、产业链、出资人。

## 实现约定

- 每个数据源一个 provider 类，实现 `DataProvider` 接口（`search_company` / `get_company`）。
- 凭证从环境变量读取（`JINGDATA_MCP_URL`/`JINGDATA_TOKEN`、`QCC_API_KEY`）。
- 工具名**动态发现**（`list_tools`），减少对文档的硬依赖；拿到真实 Key 后校准。
- MCP 返回的文本 → 结构化字段，由 services 层处理。

## 为什么不自建爬虫（ADR-0002）

爬虫反爬、改版、断源、合规风险高，且收益有限（早期 startup 的官网 SEO 差、搜索引擎难发现）。官方 API/MCP 稳定、合规、可审计，是产品命根。

## 成本提示

- 企查查：免费积分（500 + 每日赠送），可低成本起步验证。
- 鲸准：商务洽谈（B 端定价）。这是刚性数据采购成本，商业模式需覆盖（见 ADR-0003）。
