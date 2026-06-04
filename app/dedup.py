import asyncio
import hashlib
import sqlite3
import time
from pathlib import Path

_DB_PATH = Path("/data/dedup.db")
_TTL_SECONDS = 7 * 24 * 3600


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _make_key(sender: str, text: str) -> str:
    payload = f"{sender}||{_normalize(text)}"
    return hashlib.sha256(payload.encode()).hexdigest()


def _init_sync() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_requests (
                hash TEXT PRIMARY KEY,
                ts   REAL NOT NULL
            )
        """)


def _check_and_register_sync(key: str) -> bool:
    """Retorna True si el pedido ya fue procesado en los últimos 7 días."""
    cutoff = time.time() - _TTL_SECONDS
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute("DELETE FROM seen_requests WHERE ts < ?", (cutoff,))
        row = conn.execute(
            "SELECT ts FROM seen_requests WHERE hash = ?", (key,)
        ).fetchone()
        if row:
            return True
        conn.execute(
            "INSERT INTO seen_requests (hash, ts) VALUES (?, ?)",
            (key, time.time()),
        )
    return False


async def init_db() -> None:
    await asyncio.to_thread(_init_sync)


async def is_duplicate(sender: str, text: str) -> bool:
    key = _make_key(sender, text)
    return await asyncio.to_thread(_check_and_register_sync, key)
