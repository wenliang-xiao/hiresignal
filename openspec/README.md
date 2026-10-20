# OpenSpec · HireSignal 项目规格

> 本文档是项目的**单一事实来源**。任何开发者或 AI 模型在动手前必须先读本目录。
> 需求、设计、决策的变更必须同步更新本目录，再提交代码。

## 目录

| 文件 | 内容 |
|------|------|
| [project.md](./project.md) | 项目上下文、技术栈、约定 |
| [AGENTS.md](./AGENTS.md) | AI 开发守则（必读） |
| [specs/product.md](./specs/product.md) | 产品需求规格 |
| [design/architecture.md](./design/architecture.md) | 系统架构 |
| [design/data-layer.md](./design/data-layer.md) | 数据层设计（官方 MCP 优先） |
| [decisions/](./decisions/) | 架构决策记录（ADR） |
| [roadmap.md](./roadmap.md) | 路线图与任务拆解 |

## 核心结论（30 秒速览）

1. **产品**：面向校招/社招求职者的定向求职工具——用「近期融资」信号锁定正在扩张的 startup，直连 CEO/CTO 等决策者，实现「双向奔赴」。
2. **商业模式**：求职者免费 + 雇主付费（招聘曝光）+ 广告。
3. **数据层**：**官方 API/MCP 优先**（鲸准 + 企查查），**不自建爬虫**。
4. **合规**：只聚合公开渠道，不建私人邮箱库，遵守 PIPL / 反不正当竞争法。
