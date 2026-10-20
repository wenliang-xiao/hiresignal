"""SQLite 存储：融资事件 + 决策者。"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(os.getenv("DB_PATH", "data/hiresignal.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS funding_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    company_name_cn TEXT,
    round TEXT,
    amount_text TEXT,
    amount_cny REAL,
    currency TEXT,
    investors TEXT,          -- JSON array
    lead_investor TEXT,
    announce_date TEXT,
    industry TEXT,
    source_url TEXT,
    raw_text TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS decision_makers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funding_event_id INTEGER,
    name TEXT,
    title TEXT,
    contact TEXT,
    FOREIGN KEY (funding_event_id) REFERENCES funding_events(id)
);

CREATE INDEX IF NOT EXISTS idx_events_industry ON funding_events(industry);
CREATE INDEX IF NOT EXISTS idx_events_round ON funding_events(round);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def insert_funding_event(event: dict, raw_text: str = "") -> int:
    """插入一条融资事件及其决策者，返回 event id。重复(source_url+company)则跳过。"""
    conn = get_conn()
    try:
        # 简单去重：同 source_url 同公司名已存在则跳过
        exists = conn.execute(
            "SELECT id FROM funding_events WHERE source_url = ? AND company_name = ?",
            (event.get("source_url", ""), event.get("company_name", "")),
        ).fetchone()
        if exists:
            return exists["id"]

        cur = conn.execute(
            """INSERT INTO funding_events
               (company_name, company_name_cn, round, amount_text, amount_cny, currency,
                investors, lead_investor, announce_date, industry, source_url, raw_text, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event.get("company_name"),
                event.get("company_name_cn"),
                event.get("round"),
                event.get("amount_text"),
                event.get("amount_cny"),
                event.get("currency"),
                json.dumps(event.get("investors") or [], ensure_ascii=False),
                event.get("lead_investor"),
                event.get("announce_date"),
                event.get("industry"),
                event.get("source_url", ""),
                raw_text[:20000],
                datetime.now().isoformat(),
            ),
        )
        event_id = cur.lastrowid

        for dm in event.get("decision_makers") or []:
            conn.execute(
                "INSERT INTO decision_makers (funding_event_id, name, title, contact) VALUES (?, ?, ?, ?)",
                (event_id, dm.get("name"), dm.get("title"), dm.get("contact")),
            )
        conn.commit()
        return event_id
    finally:
        conn.close()


def query_events(industry: str | None = None, limit: int = 50) -> list[dict]:
    conn = get_conn()
    try:
        sql = "SELECT * FROM funding_events"
        args = []
        if industry:
            sql += " WHERE industry LIKE ?"
            args.append(f"%{industry}%")
        sql += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        rows = conn.execute(sql, args).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
