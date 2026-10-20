# HireSignal · 融资雷达

> 用融资数据锁定「有钱且在扩张」的 startup，用公开渠道直连「能拍板的人」。

面向校招/社招求职者的**定向求职工具**：搜索国内按行业分类的「近期 X 轮融资」公司，识别 CEO/CTO/director 以上决策者，聚合公开联系方式，帮你主动触达，实现「双向奔赴」。

## 为什么是它

| 渠道 | 痛点 | HireSignal 解法 |
|------|------|----------------|
| 内推 | 吃人脉资源 | 不需要人脉，直接 cold outreach |
| 招聘软件（BOSS/猎聘） | 被动海投、HR 筛选、定向不准 | 主动定向、直连决策者 |
| 猎头 | 服务高端、收费 | 免费、服务所有人 |

**核心洞察**：融资的钱主要花在「招人」上。「近期融资」是最前瞻的招聘扩张信号，比招聘软件的在招岗位列表更早、更准。

## 数据管道架构

```
数据源(融资新闻/官网/JD/公开渠道)
   → 采集层 crawler (requests + bs4)
   → 抽取层 extract (LLM 结构化 + 决策者识别)
   → 对齐层 align (实体归一/消歧，待建)
   → 存储层 store (SQLite → PostgreSQL/ES)
   → 服务层 (搜索/图谱/AI问答，待建)
```

## 合规红线

- 只采**公开一手源**（新闻、官网、官方公告），**不爬**天眼查/企查查/IT桔子等商业付费库（反不正当竞争法「数据专款」）。
- 联系方式只聚合「企业公开邮箱 + 决策者公开主页链接」，**不建私人邮箱数据库**（PIPL）。
- 新闻做「事实抽取」，不全文转载。

## 目录结构

```
hiresignal/
├── config/                 # 数据源、赛道关键词配置
│   ├── sources.yaml
│   └── keywords.yaml
├── hiresignal/
│   ├── crawler/            # 采集层
│   │   ├── base.py         #   通用抓取
│   │   └── news_sources.py #   融资新闻源
│   ├── extract/            # 抽取层
│   │   ├── llm.py          #   LLM 封装（OpenAI 兼容）
│   │   └── funding_event.py#   融资事件 + 决策者抽取
│   ├── store/
│   │   └── db.py           # SQLite 存储
│   └── pipeline.py         # 编排
├── scripts/run_pipeline.py # 入口
└── tests/
```

## 快速开始

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 填写 LLM_BASE_URL / LLM_API_KEY
python scripts/run_pipeline.py --source 36kr --limit 20
```

## 路线图

- **P1（当前）**：AI/硬科技赛道融资新闻 → LLM 抽取融资事件 + 决策者 → SQLite，可查询。
- **P2**：公司详情、决策者聚合、关系图谱、榜单。
- **P3**：AI 问答、订阅推送、雇主侧招聘曝光、API。

## License

[MIT](./LICENSE) © 2026 Wenliang Xiao
