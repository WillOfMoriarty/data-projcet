"""
database.py
SQLite database layer for storing receipt scan results.

Tables:
  receipts    — one row per scan (header info)
  items       — one row per line item, FK to receipts
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from parser import ParsedReceipt, ReceiptItem

DB_PATH = "data/receipts.db"


# ── Connection ────────────────────────────────────────────────────────────────

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Return SQLite connection with row_factory set to Row
    so columns can be accessed by name.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # better concurrent write perf
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── Schema setup ──────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS receipts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path    TEXT,
    store_name    TEXT,
    receipt_date  TEXT,
    subtotal      INTEGER DEFAULT 0,
    discount      INTEGER DEFAULT 0,
    total         INTEGER DEFAULT 0,
    raw_text      TEXT,
    raw_json_path TEXT,
    warnings      TEXT,       -- JSON array of parse warnings
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id  INTEGER NOT NULL,
    item_name   TEXT,
    qty         INTEGER,
    price       INTEGER,
    total       INTEGER,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_items_receipt_id ON items(receipt_id);
CREATE INDEX IF NOT EXISTS idx_receipts_date     ON receipts(receipt_date);
CREATE INDEX IF NOT EXISTS idx_receipts_store    ON receipts(store_name);
"""


def init_db(db_path: str = DB_PATH):
    """Create tables if they don't exist."""
    conn = get_connection(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


# ── Write operations ──────────────────────────────────────────────────────────

def save_receipt(
    parsed: ParsedReceipt,
    image_path: str = "",
    raw_json_path: str = "",
    db_path: str = DB_PATH,
) -> int:
    """
    Insert parsed receipt into DB.

    Returns:
        receipt_id (int) — the newly inserted row's ID
    """
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """
            INSERT INTO receipts
                (image_path, store_name, receipt_date, subtotal, discount, total,
                 raw_text, raw_json_path, warnings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                image_path,
                parsed.store_name,
                parsed.date,
                parsed.subtotal,
                parsed.discount,
                parsed.total,
                parsed.raw_text,
                raw_json_path,
                json.dumps(parsed.parse_warnings),
            ),
        )
        receipt_id = cur.lastrowid

        # Insert items
        for item in parsed.items:
            conn.execute(
                """
                INSERT INTO items (receipt_id, item_name, qty, price, total)
                VALUES (?, ?, ?, ?, ?)
                """,
                (receipt_id, item.item_name, item.qty, item.price, item.total),
            )

        conn.commit()
        return receipt_id
    finally:
        conn.close()


def delete_receipt(receipt_id: int, db_path: str = DB_PATH):
    """Delete a receipt and all its items (CASCADE handles items)."""
    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
        conn.commit()
    finally:
        conn.close()


# ── Read operations ───────────────────────────────────────────────────────────

def get_all_receipts(db_path: str = DB_PATH) -> list[dict]:
    """
    Return all receipts ordered by newest first.
    Each dict has receipt header fields + item_count.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT r.*, COUNT(i.id) as item_count
            FROM receipts r
            LEFT JOIN items i ON i.receipt_id = r.id
            GROUP BY r.id
            ORDER BY r.created_at DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_receipt_by_id(receipt_id: int, db_path: str = DB_PATH) -> Optional[dict]:
    """Return a single receipt with its items list."""
    conn = get_connection(db_path)
    try:
        receipt_row = conn.execute(
            "SELECT * FROM receipts WHERE id = ?", (receipt_id,)
        ).fetchone()

        if not receipt_row:
            return None

        receipt = dict(receipt_row)

        items_rows = conn.execute(
            "SELECT * FROM items WHERE receipt_id = ? ORDER BY id",
            (receipt_id,),
        ).fetchall()
        receipt["items"] = [dict(r) for r in items_rows]
        receipt["warnings"] = json.loads(receipt.get("warnings") or "[]")

        return receipt
    finally:
        conn.close()


def get_items_by_name(name_query: str, db_path: str = DB_PATH) -> list[dict]:
    """Search items by name (case-insensitive partial match)."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT i.*, r.store_name, r.receipt_date
            FROM items i
            JOIN receipts r ON r.id = i.receipt_id
            WHERE UPPER(i.item_name) LIKE UPPER(?)
            ORDER BY r.receipt_date DESC
            """,
            (f"%{name_query}%",),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_summary_stats(db_path: str = DB_PATH) -> dict:
    """
    Return aggregate stats for dashboard display:
      - total receipts scanned
      - total items parsed
      - total spend
      - most scanned store
    """
    conn = get_connection(db_path)
    try:
        stats = {}

        row = conn.execute(
            "SELECT COUNT(*) as cnt, SUM(total) as spend FROM receipts"
        ).fetchone()
        stats["total_receipts"] = row["cnt"] or 0
        stats["total_spend"] = row["spend"] or 0

        row = conn.execute("SELECT COUNT(*) as cnt FROM items").fetchone()
        stats["total_items"] = row["cnt"] or 0

        row = conn.execute(
            """
            SELECT store_name, COUNT(*) as cnt
            FROM receipts
            WHERE store_name IS NOT NULL AND store_name != 'UNKNOWN STORE'
            GROUP BY store_name
            ORDER BY cnt DESC
            LIMIT 1
            """
        ).fetchone()
        stats["top_store"] = row["store_name"] if row else "-"

        return stats
    finally:
        conn.close()
