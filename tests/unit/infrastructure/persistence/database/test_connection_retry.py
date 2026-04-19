"""测试 DatabaseConnection 在 SQLite 写锁竞争下的重试行为。

场景：daemon 子进程频繁写 DB 时，API 进程调用 start_autopilot 会触发
sqlite3.OperationalError: database is locked。execute_write 必须在锁
释放后自动重试成功，而不是把锁定错误抛回 API。
"""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

import pytest


def _holder_thread_locks_for(seconds: float, db_path: str, started: threading.Event):
    """开一个连接持有写锁 N 秒，模拟 daemon 写章节期间。"""
    conn = sqlite3.connect(db_path, timeout=0.1)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("BEGIN IMMEDIATE;")  # 立即抢 RESERVED 锁
    conn.execute("INSERT INTO t (x) VALUES (1);")
    started.set()
    time.sleep(seconds)
    conn.commit()
    conn.close()


def _make_db(tmp_path: Path):
    db = tmp_path / "lock_test.db"
    boot = sqlite3.connect(str(db))
    boot.execute("PRAGMA journal_mode=WAL;")
    boot.execute("CREATE TABLE t (x INTEGER);")
    boot.commit()
    boot.close()
    return str(db)


def test_execute_write_retries_until_lock_released(tmp_path: Path) -> None:
    """另一个连接持锁 1.5 秒；execute_write 应等待并最终成功。"""
    from infrastructure.persistence.database.connection import DatabaseConnection

    db_path = _make_db(tmp_path)
    db = DatabaseConnection(db_path)

    started = threading.Event()
    holder = threading.Thread(
        target=_holder_thread_locks_for,
        args=(1.5, db_path, started),
        daemon=True,
    )
    holder.start()
    started.wait(timeout=2)

    # 现在锁被持住，普通的 conn.execute("UPDATE...") 在 busy_timeout
    # 默认下会等待，但我们要保证 execute_write 即便遇到瞬时 locked 也能重试
    t0 = time.monotonic()
    db.execute_write("INSERT INTO t (x) VALUES (?)", (42,))
    db.commit()
    elapsed = time.monotonic() - t0

    holder.join(timeout=3)

    rows = db.fetch_all("SELECT x FROM t ORDER BY x")
    assert {r["x"] for r in rows} == {1, 42}, f"两条写入都应保留，实际 {rows}"
    assert elapsed >= 1.0, f"应等待锁释放（>=1s），实际 {elapsed:.2f}s"


def test_execute_write_does_not_swallow_non_lock_errors(tmp_path: Path) -> None:
    """非"locked/busy" 类的 OperationalError（如 SQL 语法错）必须立即抛出，
    不能被 retry 循环静默吞掉。否则真正的 bug 会被掩盖成超时。"""
    from infrastructure.persistence.database.connection import DatabaseConnection

    db_path = _make_db(tmp_path)
    db = DatabaseConnection(db_path)

    t0 = time.monotonic()
    with pytest.raises(sqlite3.OperationalError):
        db.execute_write("INSERT INTO no_such_table (x) VALUES (?)", (1,))
    elapsed = time.monotonic() - t0
    # 立即抛出，不应当走完整个 60s 重试预算
    assert elapsed < 1.0, f"非锁错误必须立即抛出，实际等了 {elapsed:.2f}s"
