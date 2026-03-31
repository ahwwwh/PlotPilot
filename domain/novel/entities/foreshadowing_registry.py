# domain/novel/entities/foreshadowing_registry.py
from typing import List, Optional
from dataclasses import replace

from domain.shared.base_entity import BaseEntity
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.foreshadowing import (
    Foreshadowing,
    ForeshadowingStatus
)
from domain.shared.exceptions import InvalidOperationError


class ForeshadowingRegistry(BaseEntity):
    """伏笔注册表实体"""

    def __init__(self, id: str, novel_id: NovelId):
        super().__init__(id)
        self.novel_id = novel_id
        self._foreshadowings: List[Foreshadowing] = []

    @property
    def foreshadowings(self) -> List[Foreshadowing]:
        """返回伏笔列表的副本"""
        return self._foreshadowings.copy()

    def register(self, foreshadowing: Foreshadowing) -> None:
        """注册新伏笔，检查重复"""
        if any(f.id == foreshadowing.id for f in self._foreshadowings):
            raise InvalidOperationError(
                f"Foreshadowing with id '{foreshadowing.id}' already exists"
            )
        self._foreshadowings.append(foreshadowing)

    def mark_resolved(self, foreshadowing_id: str, resolved_in_chapter: int) -> None:
        """标记伏笔为已解决，创建新的不可变对象"""
        for i, foreshadowing in enumerate(self._foreshadowings):
            if foreshadowing.id == foreshadowing_id:
                # 创建新的不可变 Foreshadowing 对象
                resolved_foreshadowing = replace(
                    foreshadowing,
                    status=ForeshadowingStatus.RESOLVED,
                    resolved_in_chapter=resolved_in_chapter
                )
                self._foreshadowings[i] = resolved_foreshadowing
                return

        raise InvalidOperationError(
            f"Foreshadowing with id '{foreshadowing_id}' not found"
        )

    def get_by_id(self, foreshadowing_id: str) -> Optional[Foreshadowing]:
        """通过 ID 获取伏笔"""
        for foreshadowing in self._foreshadowings:
            if foreshadowing.id == foreshadowing_id:
                return foreshadowing
        return None

    def get_unresolved(self) -> List[Foreshadowing]:
        """获取所有未解决的伏笔（PLANTED 状态）"""
        return [
            f for f in self._foreshadowings
            if f.status == ForeshadowingStatus.PLANTED
        ]

    def get_ready_to_resolve(self, current_chapter: int) -> List[Foreshadowing]:
        """获取准备解决的伏笔"""
        return [
            f for f in self._foreshadowings
            if f.status == ForeshadowingStatus.PLANTED
            and f.suggested_resolve_chapter is not None
            and f.suggested_resolve_chapter <= current_chapter
        ]
