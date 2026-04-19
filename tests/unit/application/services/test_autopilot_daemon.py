import asyncio
import time
import pytest
from unittest.mock import AsyncMock, Mock

from application.engine.services.autopilot_daemon import AutopilotDaemon
from domain.novel.entities.novel import AutopilotStatus, Novel, NovelStage
from domain.novel.value_objects.novel_id import NovelId


@pytest.mark.asyncio
async def test_process_novels_concurrently_runs_in_parallel():
    """多本活跃小说必须被并发（而非串行）处理：3 本 ×0.2s sleep，总耗时应 < 0.5s。"""
    daemon = AutopilotDaemon(
        novel_repository=Mock(),
        llm_service=Mock(),
        context_builder=None,
        background_task_service=Mock(),
        planning_service=Mock(),
        story_node_repo=Mock(),
        chapter_repository=Mock(),
    )

    async def fake_process(novel):
        await asyncio.sleep(0.2)

    daemon._process_novel = AsyncMock(side_effect=fake_process)

    novels = [
        Novel(
            id=NovelId(f"novel-parallel-{i}"),
            title=f"并发测试-{i}",
            author="作者",
            target_chapters=10,
            autopilot_status=AutopilotStatus.RUNNING,
            current_stage=NovelStage.WRITING,
        )
        for i in range(3)
    ]

    t0 = time.monotonic()
    await daemon._process_novels_concurrently(novels)
    elapsed = time.monotonic() - t0

    assert elapsed < 0.5, f"预期并发 (~0.2s)，实际耗时 {elapsed:.2f}s 说明仍是串行"
    assert daemon._process_novel.await_count == 3


@pytest.mark.asyncio
async def test_process_novels_concurrently_isolates_exceptions():
    """任一本小说抛异常不得中断其他本的处理。"""
    daemon = AutopilotDaemon(
        novel_repository=Mock(),
        llm_service=Mock(),
        context_builder=None,
        background_task_service=Mock(),
        planning_service=Mock(),
        story_node_repo=Mock(),
        chapter_repository=Mock(),
    )

    processed_ids: list[str] = []

    async def fake_process(novel):
        if novel.novel_id.value == "novel-boom":
            raise RuntimeError("boom")
        processed_ids.append(novel.novel_id.value)

    daemon._process_novel = AsyncMock(side_effect=fake_process)

    novels = [
        Novel(
            id=NovelId(nid),
            title=nid,
            author="a",
            target_chapters=10,
            autopilot_status=AutopilotStatus.RUNNING,
            current_stage=NovelStage.WRITING,
        )
        for nid in ("novel-ok-1", "novel-boom", "novel-ok-2")
    ]

    await daemon._process_novels_concurrently(novels)

    assert set(processed_ids) == {"novel-ok-1", "novel-ok-2"}
