# AI 开发守则（AGENTS.md）

> 任何 AI 模型或开发者在本仓库动手前，**必须先读本文件**。它约束「怎么改、改完做什么」，保证交接一致性。

## 1. 先读规格，再写代码

- 动手前读 [OpenSpec README](./README.md) 与 [project.md](./project.md)。
- 涉及数据层，必读 [data-layer.md](./design/data-layer.md)。
- 涉及需求变更，必读 [product.md](./specs/product.md) 并同步更新。

## 2. 变更必须同步文档（硬性）

每完成一次代码变更，**同一 PR/commit 内必须**：

1. 更新 `openspec/` 下受影响的 md（specs / design / roadmap）。
2. 若改变了架构方向或关键技术选型，新增一条 ADR 到 `decisions/`。
3. 更新根 `README.md` 中受影响的部分。

> 原则：**文档与代码同版本演进**。宁可文档先行，不可代码先行。

## 3. 数据层红线

- **只走官方 API/MCP**（鲸准、企查查），**禁止**重新引入自建爬虫，除非新增 ADR 并说明理由。
- **禁止**爬取天眼查/企查查/IT桔子/企名片等商业付费库（反不正当竞争法「数据专款」）。
- 联系方式只聚合**公开渠道**（官网公开邮箱、公开主页链接），**不建私人邮箱数据库**（PIPL）。

## 4. 凭据与安全

- 凭证一律读环境变量，**禁止硬编码**。
- `.env`、`data/` 已在 `.gitignore`，提交前确认 `git status` 无敏感文件。

## 5. Git 规范

- commit message 用英文（GitHub 开源项目）。
- 与 `origin` 对比前先 `git fetch -p`。
- 不提交本地工具目录（`.trellis/`、`.opencode/`、`.pi/` 等）。

## 6. 新功能开发流程

1. 在 `openspec/` 明确需求与设计（可先写 spec 再写代码）。
2. 更新 `roadmap.md` 标注状态（计划中 → 进行中 → 完成）。
3. 实现 + 自测（运行 `/api/status`、搜索、AI 问答验证）。
4. 提交时带上文档更新。

## 7. 当前待办（交接点）

- 企查查 `QCC_API_KEY`、鲸准 `JINGDATA_TOKEN` 尚未配置 → provider 调用未端到端验证。
- 企查查 MCP 工具清单待探测（`scripts/probe_qcc.py`），拿到 Key 后校准 `qcc.py` 里的工具名。
- 搜索结果结构化（融资历史 / 决策者卡片 / 联系方式）待 P2 完成。
