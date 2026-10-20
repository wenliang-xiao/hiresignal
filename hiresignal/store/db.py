"""SQLite 存储：公司 / 融资事件 / 决策者 / 联系方式。"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(os.getenv("DB_PATH", "data/hiresignal.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,                -- 品牌名/简称
    name_cn TEXT,             -- 中文名
    full_name TEXT,           -- 工商全称
    website TEXT,             -- 官网
    industry TEXT,
    description TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS funding_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    round TEXT,
    amount_text TEXT,
    amount_cny REAL,
    currency TEXT,
    investors TEXT,           -- JSON array
    lead_investor TEXT,
    announce_date TEXT,
    source_url TEXT,
    raw_text TEXT,
    created_at TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    name TEXT,
    title TEXT,               -- 职位
    is_executive INTEGER DEFAULT 0,  -- 是否 director 以上决策者
    bio TEXT,
    source TEXT,
    created_at TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    person_id INTEGER,        -- 可空：公司级联系邮箱 person_id 为空
    type TEXT,                -- email / linkedin / wechat / phone / website
    value TEXT,
    source TEXT,
    created_at TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE INDEX IF NOT EXISTS idx_events_company ON funding_events(company_id);
CREATE INDEX IF NOT EXISTS idx_people_company ON people(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


# ---------- company ----------

def upsert_company(name: str, **fields) -> int:
    """按 name 去重，返回 company_id。fields 可为 name_cn/full_name/website/industry/description。"""
    conn = get_conn()
    try:
        row = conn.execute("SELECT id FROM companies WHERE name = ?", (name,)).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            """INSERT INTO companies (name, name_cn, full_name, website, industry, description, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                fields.get("name_cn"),
                fields.get("full_name"),
                fields.get("website"),
                fields.get("industry"),
                fields.get("description"),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_company(company_id: int, **fields) -> None:
    """按字段更新公司（仅更新传入的非空字段）。"""
    allowed = {"name_cn", "full_name", "website", "industry", "description"}
    sets = {k: v for k, v in fields.items() if k in allowed and v}
    if not sets:
        return
    sql = "UPDATE companies SET " + ", ".join(f"{k} = ?" for k in sets) + " WHERE id = ?"
    conn = get_conn()
    try:
        conn.execute(sql, (*sets.values(), company_id))
        conn.commit()
    finally:
        conn.close()


# ---------- funding event ----------

def insert_funding_event(company_id: int, event: dict, raw_text: str = "") -> int:
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO funding_events
               (company_id, round, amount_text, amount_cny, currency, investors, lead_investor,
                announce_date, source_url, raw_text, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                company_id,
                event.get("round"),
                event.get("amount_text"),
                event.get("amount_cny"),
                event.get("currency"),
                json.dumps(event.get("investors") or [], ensure_ascii=False),
                event.get("lead_investor"),
                event.get("announce_date"),
                event.get("source_url", ""),
                raw_text[:20000],
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ---------- people ----------

def insert_person(company_id: int, person: dict, source: str = "") -> int:
    conn = get_conn()
    try:
        # 去重：同公司同名不重复插入
        exists = conn.execute(
            "SELECT id FROM people WHERE company_id = ? AND name = ?",
            (company_id, person.get("name")),
        ).fetchone()
        if exists:
            return exists["id"]
        cur = conn.execute(
            """INSERT INTO people (company_id, name, title, is_executive, bio, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                company_id,
                person.get("name"),
                person.get("title"),
                1 if person.get("is_executive", True) else 0,
                person.get("bio"),
                source,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ---------- contacts ----------

def insert_contact(company_id: int, contact: dict, person_id: int | None = None, source: str = "") -> int:
    conn = get_conn()
    try:
        # 去重：同公司同类型同值不重复插入
        exists = conn.execute(
            "SELECT id FROM contacts WHERE company_id = ? AND type = ? AND value = ?",
            (company_id, contact.get("type"), contact.get("value")),
        ).fetchone()
        if exists:
            return exists["id"]
        cur = conn.execute(
            """INSERT INTO contacts (company_id, person_id, type, value, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                company_id,
                person_id,
                contact.get("type"),
                contact.get("value"),
                source,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ---------- query ----------

def query_companies(keyword: str | None = None, industry: str | None = None, limit: int = 50) -> list[dict]:
    conn = get_conn()
    try:
        sql = "SELECT * FROM companies"
        conds, args = [], []
        if keyword:
            conds.append("(name LIKE ? OR name_cn LIKE ? OR full_name LIKE ?)")
            args += [f"%{keyword}%"] * 3
        if industry:
            conds.append("industry LIKE ?")
            args.append(f"%{industry}%")
        if conds:
            sql += " WHERE " + " AND ".join(conds)
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


def query_people(company_id: int) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM people WHERE company_id = ? ORDER BY is_executive DESC, id ASC", (company_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def query_contacts(company_id: int) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM contacts WHERE company_id = ?", (company_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def query_events(company_id: int | None = None, limit: int = 50) -> list[dict]:
    conn = get_conn()
    try:
        sql = "SELECT * FROM funding_events"
        args = []
        if company_id:
            sql += " WHERE company_id = ?"
            args.append(company_id)
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


def stats() -> dict:
    conn = get_conn()
    try:
        return {
            "companies": conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
            "funding_events": conn.execute("SELECT COUNT(*) FROM funding_events").fetchone()[0],
            "people": conn.execute("SELECT COUNT(*) FROM people").fetchone()[0],
            "contacts": conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0],
        }
    finally:
        conn.close()
