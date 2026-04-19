"""Unit tests for scripts/db_checkpoint.py."""
import os
import sqlite3
import sys
from pathlib import Path


# 让 scripts.db_checkpoint 可被 import
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _populate_db_with_wal(db_path: Path):
    """建 WAL 模式 DB 并写入数据，返回保持打开的连接（close 时 WAL 会被自动 checkpoint 消失）。"""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA wal_autocheckpoint=0;")  # 禁止自动 checkpoint，保留 WAL 内容
    conn.execute("CREATE TABLE t (x INTEGER);")
    conn.executemany("INSERT INTO t(x) VALUES (?);", [(i,) for i in range(500)])
    conn.commit()
    return conn


def test_checkpoint_truncates_wal_file(tmp_path: Path) -> None:
    db = tmp_path / "sample.db"
    writer = _populate_db_with_wal(db)
    try:
        wal = tmp_path / "sample.db-wal"
        assert wal.exists() and wal.stat().st_size > 0, "前置：WAL 文件应有内容"

        from scripts.db_checkpoint import checkpoint_wal

        rc = checkpoint_wal(str(db))

        assert rc == 0, "checkpoint 应返回 0 表示成功"
        # WAL 被 TRUNCATE 后应为 0 字节
        assert wal.stat().st_size == 0
    finally:
        writer.close()


def test_checkpoint_missing_db_returns_nonzero(tmp_path: Path) -> None:
    from scripts.db_checkpoint import checkpoint_wal

    rc = checkpoint_wal(str(tmp_path / "does_not_exist.db"))

    assert rc != 0, "DB 文件不存在应返回非 0"
