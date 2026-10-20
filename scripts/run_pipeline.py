"""入口：python scripts/run_pipeline.py --source pedaily --limit 20"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hiresignal.config import load_keywords  # noqa: E402
from hiresignal.pipeline import run  # noqa: E402
from hiresignal.store import db  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="HireSignal P1 数据管道")
    ap.add_argument("--source", default="pedaily", help="新闻源 id（默认 pedaily）")
    ap.add_argument("--limit", type=int, default=20, help="抓取条数上限")
    ap.add_argument("--query", action="store_true", help="跑完后列出库内数据")
    args = ap.parse_args()

    keywords = load_keywords().get("ai_hardtech", [])
    events = run(source_id=args.source, limit=args.limit, keywords=keywords)
    print(f"\n本次入库 {len(events)} 条融资事件")

    if args.query:
        rows = db.query_events(limit=args.limit)
        print(f"\n库内共 {len(rows)} 条：")
        for r in rows:
            print(f"  [{r['industry'] or '?'}] {r['company_name'] or '?'} "
                  f"{r['round'] or '?'} {r['amount_text'] or '-'} "
                  f"领投={r['lead_investor'] or '-'}")


if __name__ == "__main__":
    main()
