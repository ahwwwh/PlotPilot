"""SQLite WAL checkpoint 工具。

迁移或备份 SQLite 数据库前建议先 checkpoint，把 -wal 文件的内容合并回主库文件，
避免跨机器拷贝时因为 WAL 状态不一致导致数据看似"丢失"。

用法:
    python scripts/db_checkpoint.py [db_path]

默认路径: data/aitext.db
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path


def checkpoint_wal(db_path: str) -> int:
    """执行 WAL TRUNCATE checkpoint，把 WAL 内容合并进主库文件。

    Returns:
        0 表示成功；非 0 表示失败。
    """
    path = Path(db_path)
    if not path.exists():
        print(f"[ERR ] DB file not found: {db_path}", file=sys.stderr)
        return 2

    try:
        conn = sqlite3.connect(str(path))
        try:
            cur = conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            busy, log_frames, checkpointed = cur.fetchone()
            conn.commit()
        finally:
            conn.close()
    except sqlite3.Error as e:
        print(f"[ERR ] checkpoint failed: {e}", file=sys.stderr)
        return 1

    print(
        f"[ OK ] checkpoint: busy={busy} log_frames={log_frames} checkpointed={checkpointed}"
    )
    return 0


def main() -> int:
    default_db = os.path.join("data", "aitext.db")
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db
    return checkpoint_wal(db_path)


if __name__ == "__main__":
    raise SystemExit(main())
