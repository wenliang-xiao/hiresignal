"""P1 数据管道编排：抓取 → LLM 抽取 → 存储。"""

import time

from .crawler.news_sources import PedailySource
from .extract.funding_event import extract_funding_event
from .store import db

SOURCES = {
    "pedaily": PedailySource,
    "36kr": None,  # 36氪 JS 渲染，待接入 Playwright
}


def run(source_id: str = "pedaily", limit: int = 20, keywords: list[str] | None = None) -> list[dict]:
    """跑一条管道，返回入库的融资事件列表。"""
    src_cls = SOURCES.get(source_id)
    if src_cls is None:
        raise ValueError(f"未知或未实现的源：{source_id}")

    src = src_cls()
    articles = src.list_articles(limit=limit)
    print(f"[crawler] {src.name} 抓到 {len(articles)} 条候选新闻")

    events = []
    for i, art in enumerate(articles, 1):
        try:
            detail = src.fetch_article(art["url"])
            event = extract_funding_event(detail["text"], source_url=art["url"], keywords=keywords)
            if not event.get("is_funding", True):
                print(f"  [{i}/{len(articles)}] 跳过（非融资）: {art['title'][:30]}")
                continue
            event_id = db.insert_funding_event(event, raw_text=detail["text"])
            event["id"] = event_id
            events.append(event)
            print(f"  [{i}/{len(articles)}] ✓ {event.get('company_name','?')} | "
                  f"{event.get('round','?')} | {event.get('amount_text') or '-'} | "
                  f"领投 {event.get('lead_investor') or '-'}")
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(articles)}] ✗ 失败: {art['title'][:30]} -> {e}")
        time.sleep(0.5)  # 礼貌限速
    return events


if __name__ == "__main__":
    run()
