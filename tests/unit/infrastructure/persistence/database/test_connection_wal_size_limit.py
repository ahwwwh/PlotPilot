"""验证 DatabaseConnection 初始化时给 SQLite WAL 施加 64MB 上限。

背景：两本小说 autopilot daemon 24h 连续写入时，WAL 文件在真实环境涨到
1.9GB 仍未触发 checkpoint，一旦进程崩溃恢复会回放数以万计的事务，磁盘
也会被吃爆。PRAGMA journal_size_limit 让 SQLite 在每次 checkpoint/commit
后把 WAL 截到给定上限之下，从而把 WAL 体积锁在可控范围。
"""
from __future__ import annotations

from pathlib import Path

from infrastructure.persistence.database.connection import DatabaseConnection


def test_connection_caps_wal_size_at_64mb(tmp_path: Path) -> None:
    db = DatabaseConnection(str(tmp_path / "size_limit.db"))
    conn = db.get_connection()
    (limit,) = conn.execute("PRAGMA journal_size_limit;").fetchone()
    assert limit == 67108864, (
        f"WAL 需要限定在 64MB，当前 journal_size_limit={limit}。"
        "daemon 长期写入会导致 WAL 无限膨胀，见 CLAUDE.md 合并 SOP。"
    )
