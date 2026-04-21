"""验证 StoryNodeRepository 自建连接有正确的 SQLite 并发设置"""
import sqlite3
import tempfile
import os
import pytest

from infrastructure.persistence.database.story_node_repository import StoryNodeRepository


def test_repository_connection_has_busy_timeout_and_wal():
    """自建连接必须设 PRAGMA busy_timeout + journal_mode=WAL，
    否则多本并发写时 'database is locked' 立即抛出，daemon 真并发被破坏。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        # 初始化一个合法 DB
        c = sqlite3.connect(db_path)
        c.executescript("""
            CREATE TABLE story_nodes (id TEXT PRIMARY KEY);
        """)
        c.close()

        repo = StoryNodeRepository(db_path)
        conn = repo._get_connection()
        try:
            # busy_timeout 毫秒，必须 >0（默认 0 = 立即失败）
            busy_timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
            assert busy_timeout >= 1000, f"busy_timeout 必须 >= 1000ms，实际 {busy_timeout}"

            # journal_mode 应为 WAL（并发性能关键）
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            assert journal_mode.lower() == "wal", f"journal_mode 必须是 wal，实际 {journal_mode}"
        finally:
            conn.close()
    finally:
        os.unlink(db_path)
