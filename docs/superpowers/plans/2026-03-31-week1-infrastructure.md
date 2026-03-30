# Week 1: 基础设施搭建 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立后端模块化架构、前端类型系统、统计API基础设施

**Architecture:** 后端采用三层架构(Router-Service-Repository)，前端使用TypeScript类型定义+Pinia状态管理，统一错误处理和日志系统

**Tech Stack:** FastAPI, Pydantic, Vue 3, TypeScript, Pinia, ECharts, Axios

---

## File Structure Overview

### Backend Files (New)
```
web/
├── routers/
│   ├── __init__.py          # Router registry
│   └── stats.py             # Statistics endpoints
├── services/
│   ├── __init__.py
│   └── stats_service.py     # Statistics business logic
├── repositories/
│   ├── __init__.py
│   └── stats_repository.py  # Data access layer
├── models/
│   ├── __init__.py
│   ├── responses.py         # Common response models
│   └── stats_models.py      # Statistics data models
├── middleware/
│   ├── __init__.py
│   ├── error_handler.py     # Global error handling
│   └── logging_config.py    # Unified logging
└── utils/
    ├── __init__.py
    └── file_utils.py        # File operation helpers
```

### Frontend Files (New)
```
web-app/src/
├── types/
│   └── api.ts               # API response types
├── stores/
│   └── statsStore.ts        # Statistics state management
├── api/
│   └── stats.ts             # Statistics API client
└── components/stats/
    └── (placeholder for Week 2)
```

### Modified Files
- `web/app.py` - Add new router imports
- `web-app/package.json` - Add vue-echarts dependency

---

## Task 1: 创建后端基础目录结构

**Files:**
- Create: `web/routers/__init__.py`
- Create: `web/services/__init__.py`
- Create: `web/repositories/__init__.py`
- Create: `web/models/__init__.py`
- Create: `web/middleware/__init__.py`
- Create: `web/utils/__init__.py`

- [ ] **Step 1: 创建routers目录和初始化文件**

```bash
mkdir -p web/routers
```

- [ ] **Step 2: 写入routers/__init__.py**

```python
"""
路由模块：处理HTTP请求和响应
"""
from fastapi import APIRouter

__all__ = ["APIRouter"]
```

- [ ] **Step 3: 创建services目录和初始化文件**

```bash
mkdir -p web/services
```

- [ ] **Step 4: 写入services/__init__.py**

```python
"""
服务层：业务逻辑处理
"""

__all__ = []
```

- [ ] **Step 5: 创建repositories目录和初始化文件**

```bash
mkdir -p web/repositories
```

- [ ] **Step 6: 写入repositories/__init__.py**

```python
"""
数据访问层：文件系统和数据库操作
"""

__all__ = []
```

- [ ] **Step 7: 创建models目录和初始化文件**

```bash
mkdir -p web/models
```

- [ ] **Step 8: 写入models/__init__.py**

```python
"""
数据模型：Pydantic模型定义
"""

__all__ = []
```

- [ ] **Step 9: 创建middleware目录和初始化文件**

```bash
mkdir -p web/middleware
```

- [ ] **Step 10: 写入middleware/__init__.py**

```python
"""
中间件：错误处理、日志、CORS等
"""

__all__ = []
```

- [ ] **Step 11: 创建utils目录和初始化文件**

```bash
mkdir -p web/utils
```

- [ ] **Step 12: 写入utils/__init__.py**

```python
"""
工具函数：通用辅助功能
"""

__all__ = []
```

- [ ] **Step 13: 验证目录结构**

```bash
ls -la web/routers web/services web/repositories web/models web/middleware web/utils
```

Expected: 所有目录都存在且包含__init__.py

- [ ] **Step 14: Commit**

```bash
git add web/routers web/services web/repositories web/models web/middleware web/utils
git commit -m "feat: create backend modular directory structure"
```

---

## Task 2: 创建统一响应模型

**Files:**
- Create: `web/models/responses.py`
- Modify: `web/models/__init__.py`

- [ ] **Step 1: 写入responses.py的测试用例**

Create: `tests/web/models/test_responses.py`

```python
"""测试统一响应模型"""
import pytest
from pydantic import ValidationError
from aitext.web.models.responses import SuccessResponse, ErrorResponse, PaginatedResponse


def test_success_response_basic():
    """测试基本成功响应"""
    response = SuccessResponse(data={"message": "ok"})
    assert response.success is True
    assert response.data == {"message": "ok"}
    assert response.message is None


def test_success_response_with_message():
    """测试带消息的成功响应"""
    response = SuccessResponse(data={"count": 5}, message="Found 5 items")
    assert response.success is True
    assert response.data == {"count": 5}
    assert response.message == "Found 5 items"


def test_error_response_basic():
    """测试基本错误响应"""
    response = ErrorResponse(message="Not found", code="NOT_FOUND")
    assert response.success is False
    assert response.message == "Not found"
    assert response.code == "NOT_FOUND"
    assert response.details is None


def test_error_response_with_details():
    """测试带详情的错误响应"""
    response = ErrorResponse(
        message="Validation failed",
        code="VALIDATION_ERROR",
        details={"field": "email", "error": "invalid format"}
    )
    assert response.success is False
    assert response.details == {"field": "email", "error": "invalid format"}


def test_paginated_response():
    """测试分页响应"""
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    response = PaginatedResponse(
        data=items,
        total=10,
        page=1,
        page_size=3
    )
    assert response.success is True
    assert response.data == items
    assert response.total == 10
    assert response.page == 1
    assert response.page_size == 3
    assert response.total_pages == 4  # ceil(10/3)


def test_paginated_response_validation():
    """测试分页参数验证"""
    with pytest.raises(ValidationError):
        PaginatedResponse(data=[], total=-1, page=1, page_size=10)

    with pytest.raises(ValidationError):
        PaginatedResponse(data=[], total=10, page=0, page_size=10)

    with pytest.raises(ValidationError):
        PaginatedResponse(data=[], total=10, page=1, page_size=0)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/web/models/test_responses.py -v
```

Expected: FAIL - 模块不存在

- [ ] **Step 3: 实现responses.py**

```python
"""统一响应模型"""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field
import math

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应"""
    success: bool = Field(default=True, description="请求是否成功")
    data: T = Field(..., description="响应数据")
    message: Optional[str] = Field(default=None, description="附加消息")


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(default=False, description="请求是否成功")
    message: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误代码")
    details: Optional[Any] = Field(default=None, description="错误详情")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    success: bool = Field(default=True, description="请求是否成功")
    data: list[T] = Field(..., description="数据列表")
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, description="每页大小")
    total_pages: int = Field(default=0, description="总页数")

    def __init__(self, **data):
        super().__init__(**data)
        # 计算总页数
        self.total_pages = math.ceil(self.total / self.page_size) if self.page_size > 0 else 0
```

- [ ] **Step 4: 更新models/__init__.py**

```python
"""
数据模型：Pydantic模型定义
"""
from .responses import SuccessResponse, ErrorResponse, PaginatedResponse

__all__ = ["SuccessResponse", "ErrorResponse", "PaginatedResponse"]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/web/models/test_responses.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add web/models/responses.py web/models/__init__.py tests/web/models/test_responses.py
git commit -m "feat: add unified response models with tests"
```

---

## Task 3: 创建统一错误处理中间件

**Files:**
- Create: `web/middleware/error_handler.py`
- Modify: `web/middleware/__init__.py`

- [ ] **Step 1: 写入错误处理测试**

Create: `tests/web/middleware/test_error_handler.py`

```python
"""测试错误处理中间件"""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from aitext.web.middleware.error_handler import add_error_handlers


def test_http_exception_handler():
    """测试HTTP异常处理"""
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/test-404")
    async def test_404():
        raise HTTPException(status_code=404, detail="Not found")

    client = TestClient(app)
    response = client.get("/test-404")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "Not found"
    assert data["code"] == "NOT_FOUND"


def test_validation_error_handler():
    """测试验证错误处理"""
    from pydantic import BaseModel, Field

    app = FastAPI()
    add_error_handlers(app)

    class Item(BaseModel):
        name: str = Field(..., min_length=1)
        count: int = Field(..., ge=0)

    @app.post("/test-validation")
    async def test_validation(item: Item):
        return {"ok": True}

    client = TestClient(app)
    response = client.post("/test-validation", json={"name": "", "count": -1})

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["code"] == "VALIDATION_ERROR"
    assert "details" in data


def test_generic_exception_handler():
    """测试通用异常处理"""
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/test-error")
    async def test_error():
        raise ValueError("Something went wrong")

    client = TestClient(app)
    response = client.get("/test-error")

    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert data["code"] == "INTERNAL_ERROR"
    assert "Something went wrong" in data["message"]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/web/middleware/test_error_handler.py -v
```

Expected: FAIL - 模块不存在

- [ ] **Step 3: 实现error_handler.py**

```python
"""统一错误处理中间件"""
import logging
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    """添加全局错误处理器"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """处理HTTP异常"""
        logger.warning(
            f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url.path}"
        )

        # 映射状态码到错误代码
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            500: "INTERNAL_ERROR",
        }

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "code": code_map.get(exc.status_code, "HTTP_ERROR"),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """处理请求验证错误"""
        logger.warning(
            f"Validation error: {exc.errors()} - {request.method} {request.url.path}"
        )

        # 格式化验证错误
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": errors,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """处理未捕获的异常"""
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)} - "
            f"{request.method} {request.url.path}",
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"Internal server error: {str(exc)}",
                "code": "INTERNAL_ERROR",
            },
        )
```

- [ ] **Step 4: 更新middleware/__init__.py**

```python
"""
中间件：错误处理、日志、CORS等
"""
from .error_handler import add_error_handlers

__all__ = ["add_error_handlers"]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/web/middleware/test_error_handler.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add web/middleware/error_handler.py web/middleware/__init__.py tests/web/middleware/test_error_handler.py
git commit -m "feat: add unified error handling middleware with tests"
```

---

## Task 4: 创建统一日志配置

**Files:**
- Create: `web/middleware/logging_config.py`
- Modify: `web/middleware/__init__.py`

- [ ] **Step 1: 实现logging_config.py**

```python
"""统一日志配置"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> None:
    """
    配置统一的日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，None表示只输出到控制台
        format_string: 自定义日志格式
    """
    if format_string is None:
        format_string = (
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(
        format_string,
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（如果指定）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = logging.Formatter(
            format_string,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器

    Args:
        name: 日志器名称，通常使用 __name__

    Returns:
        配置好的日志器实例
    """
    return logging.getLogger(name)
```

- [ ] **Step 2: 更新middleware/__init__.py**

```python
"""
中间件：错误处理、日志、CORS等
"""
from .error_handler import add_error_handlers
from .logging_config import setup_logging, get_logger

__all__ = ["add_error_handlers", "setup_logging", "get_logger"]
```

- [ ] **Step 3: 测试日志配置**

Create: `tests/web/middleware/test_logging_config.py`

```python
"""测试日志配置"""
import logging
import tempfile
from pathlib import Path
from aitext.web.middleware.logging_config import setup_logging, get_logger


def test_setup_logging_console_only():
    """测试仅控制台日志"""
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    assert logger.level == logging.DEBUG
    assert len(logging.getLogger().handlers) >= 1


def test_setup_logging_with_file():
    """测试文件日志"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        setup_logging(level="INFO", log_file=log_file)

        logger = get_logger(__name__)
        logger.info("Test message")

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test message" in content


def test_get_logger():
    """测试获取日志器"""
    logger1 = get_logger("test.module1")
    logger2 = get_logger("test.module2")

    assert logger1.name == "test.module1"
    assert logger2.name == "test.module2"
    assert logger1 is not logger2
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/web/middleware/test_logging_config.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 5: Commit**

```bash
git add web/middleware/logging_config.py web/middleware/__init__.py tests/web/middleware/test_logging_config.py
git commit -m "feat: add unified logging configuration with tests"
```

---

## Task 5: 创建统计数据模型

**Files:**
- Create: `web/models/stats_models.py`
- Modify: `web/models/__init__.py`

- [ ] **Step 1: 写入统计模型测试**

Create: `tests/web/models/test_stats_models.py`

```python
"""测试统计数据模型"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from aitext.web.models.stats_models import (
    GlobalStats,
    BookStats,
    ChapterStats,
    WritingProgress,
    ContentAnalysis,
)


def test_global_stats_basic():
    """测试全局统计基本功能"""
    stats = GlobalStats(
        total_books=5,
        total_chapters=50,
        total_words=100000,
        total_characters=15,
        books_by_stage={"planning": 2, "writing": 2, "completed": 1},
    )
    assert stats.total_books == 5
    assert stats.total_chapters == 50
    assert stats.total_words == 100000
    assert stats.books_by_stage["completed"] == 1


def test_book_stats_basic():
    """测试书籍统计基本功能"""
    stats = BookStats(
        slug="test-book",
        title="Test Book",
        total_chapters=10,
        completed_chapters=5,
        total_words=50000,
        avg_chapter_words=5000,
        completion_rate=0.5,
        last_updated=datetime.now(),
    )
    assert stats.slug == "test-book"
    assert stats.completion_rate == 0.5
    assert stats.completed_chapters == 5


def test_chapter_stats_basic():
    """测试章节统计基本功能"""
    stats = ChapterStats(
        chapter_id=1,
        title="Chapter 1",
        word_count=5000,
        character_count=8000,
        paragraph_count=50,
        has_content=True,
    )
    assert stats.chapter_id == 1
    assert stats.word_count == 5000
    assert stats.has_content is True


def test_writing_progress_validation():
    """测试写作进度验证"""
    # 正常情况
    progress = WritingProgress(
        date="2026-03-31",
        words_written=1000,
        chapters_completed=1,
    )
    assert progress.words_written == 1000

    # 负数应该失败
    with pytest.raises(ValidationError):
        WritingProgress(
            date="2026-03-31",
            words_written=-100,
            chapters_completed=0,
        )


def test_content_analysis_basic():
    """测试内容分析基本功能"""
    analysis = ContentAnalysis(
        character_mentions={"Alice": 50, "Bob": 30},
        dialogue_ratio=0.35,
        scene_count=10,
        avg_paragraph_length=120.5,
    )
    assert analysis.character_mentions["Alice"] == 50
    assert analysis.dialogue_ratio == 0.35
    assert 0 <= analysis.dialogue_ratio <= 1
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/web/models/test_stats_models.py -v
```

Expected: FAIL - 模块不存在

- [ ] **Step 3: 实现stats_models.py**

```python
"""统计数据模型"""
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class GlobalStats(BaseModel):
    """全局统计数据"""
    total_books: int = Field(..., ge=0, description="总书籍数")
    total_chapters: int = Field(..., ge=0, description="总章节数")
    total_words: int = Field(..., ge=0, description="总字数")
    total_characters: int = Field(..., ge=0, description="总人物数")
    books_by_stage: Dict[str, int] = Field(
        default_factory=dict, description="各阶段书籍数量"
    )


class BookStats(BaseModel):
    """单本书籍统计"""
    slug: str = Field(..., description="书籍标识")
    title: str = Field(..., description="书籍标题")
    total_chapters: int = Field(..., ge=0, description="总章节数")
    completed_chapters: int = Field(..., ge=0, description="已完成章节数")
    total_words: int = Field(..., ge=0, description="总字数")
    avg_chapter_words: float = Field(..., ge=0, description="平均章节字数")
    completion_rate: float = Field(..., ge=0, le=1, description="完成率")
    last_updated: datetime = Field(..., description="最后更新时间")


class ChapterStats(BaseModel):
    """章节统计"""
    chapter_id: int = Field(..., ge=1, description="章节ID")
    title: str = Field(..., description="章节标题")
    word_count: int = Field(..., ge=0, description="字数")
    character_count: int = Field(..., ge=0, description="字符数")
    paragraph_count: int = Field(..., ge=0, description="段落数")
    has_content: bool = Field(..., description="是否有内容")


class WritingProgress(BaseModel):
    """写作进度数据点"""
    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    words_written: int = Field(..., ge=0, description="当日写作字数")
    chapters_completed: int = Field(..., ge=0, description="当日完成章节数")


class ContentAnalysis(BaseModel):
    """内容分析数据"""
    character_mentions: Dict[str, int] = Field(
        default_factory=dict, description="人物出场次数"
    )
    dialogue_ratio: float = Field(..., ge=0, le=1, description="对话占比")
    scene_count: int = Field(..., ge=0, description="场景数量")
    avg_paragraph_length: float = Field(..., ge=0, description="平均段落长度")
```

- [ ] **Step 4: 更新models/__init__.py**

```python
"""
数据模型：Pydantic模型定义
"""
from .responses import SuccessResponse, ErrorResponse, PaginatedResponse
from .stats_models import (
    GlobalStats,
    BookStats,
    ChapterStats,
    WritingProgress,
    ContentAnalysis,
)

__all__ = [
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "GlobalStats",
    "BookStats",
    "ChapterStats",
    "WritingProgress",
    "ContentAnalysis",
]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/web/models/test_stats_models.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add web/models/stats_models.py web/models/__init__.py tests/web/models/test_stats_models.py
git commit -m "feat: add statistics data models with tests"
```

---

## Task 6: 创建统计数据访问层

**Files:**
- Create: `web/repositories/stats_repository.py`
- Modify: `web/repositories/__init__.py`

- [ ] **Step 1: 写入Repository测试**

Create: `tests/web/repositories/test_stats_repository.py`

```python
"""测试统计数据访问层"""
import pytest
import tempfile
from pathlib import Path
from aitext.web.repositories.stats_repository import StatsRepository


@pytest.fixture
def temp_books_dir():
    """创建临时书籍目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        books_dir = Path(tmpdir) / "books"
        books_dir.mkdir()

        # 创建测试书籍1
        book1 = books_dir / "test-book-1"
        book1.mkdir()
        (book1 / "manifest.json").write_text('{"title": "Test Book 1", "stage": "writing"}')
        (book1 / "outline.json").write_text('{"chapters": [{"id": 1, "title": "Chapter 1"}]}')

        # 创建章节内容
        ch1_dir = book1 / "chapters" / "ch-0001"
        ch1_dir.mkdir(parents=True)
        (ch1_dir / "body.md").write_text("# Chapter 1\n\nThis is test content with 100 words. " * 10)

        yield books_dir


def test_get_all_book_slugs(temp_books_dir):
    """测试获取所有书籍slug"""
    repo = StatsRepository(temp_books_dir)
    slugs = repo.get_all_book_slugs()

    assert len(slugs) == 1
    assert "test-book-1" in slugs


def test_get_book_manifest(temp_books_dir):
    """测试获取书籍manifest"""
    repo = StatsRepository(temp_books_dir)
    manifest = repo.get_book_manifest("test-book-1")

    assert manifest is not None
    assert manifest["title"] == "Test Book 1"
    assert manifest["stage"] == "writing"


def test_get_book_outline(temp_books_dir):
    """测试获取书籍大纲"""
    repo = StatsRepository(temp_books_dir)
    outline = repo.get_book_outline("test-book-1")

    assert outline is not None
    assert len(outline["chapters"]) == 1
    assert outline["chapters"][0]["id"] == 1


def test_get_chapter_content(temp_books_dir):
    """测试获取章节内容"""
    repo = StatsRepository(temp_books_dir)
    content = repo.get_chapter_content("test-book-1", 1)

    assert content is not None
    assert "Chapter 1" in content
    assert len(content) > 0


def test_count_words():
    """测试字数统计"""
    repo = StatsRepository(Path("/tmp"))

    text1 = "Hello world"
    assert repo.count_words(text1) == 2

    text2 = "这是中文测试"
    assert repo.count_words(text2) == 6

    text3 = "Mixed 中文 and English"
    assert repo.count_words(text3) == 6
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/web/repositories/test_stats_repository.py -v
```

Expected: FAIL - 模块不存在

- [ ] **Step 3: 实现stats_repository.py**

```python
"""统计数据访问层"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class StatsRepository:
    """统计数据访问层"""

    def __init__(self, books_root: Path):
        """
        初始化Repository

        Args:
            books_root: 书籍根目录路径
        """
        self.books_root = Path(books_root)

    def get_all_book_slugs(self) -> List[str]:
        """
        获取所有书籍的slug

        Returns:
            书籍slug列表
        """
        if not self.books_root.exists():
            return []

        slugs = []
        for item in self.books_root.iterdir():
            if item.is_dir() and (item / "manifest.json").exists():
                slugs.append(item.name)

        return sorted(slugs)

    def get_book_manifest(self, slug: str) -> Optional[Dict]:
        """
        获取书籍manifest

        Args:
            slug: 书籍标识

        Returns:
            manifest字典，不存在返回None
        """
        manifest_path = self.books_root / slug / "manifest.json"
        if not manifest_path.exists():
            return None

        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to read manifest for {slug}: {e}")
            return None

    def get_book_outline(self, slug: str) -> Optional[Dict]:
        """
        获取书籍大纲

        Args:
            slug: 书籍标识

        Returns:
            outline字典，不存在返回None
        """
        outline_path = self.books_root / slug / "outline.json"
        if not outline_path.exists():
            return None

        try:
            return json.loads(outline_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to read outline for {slug}: {e}")
            return None

    def get_chapter_content(self, slug: str, chapter_id: int) -> Optional[str]:
        """
        获取章节内容

        Args:
            slug: 书籍标识
            chapter_id: 章节ID

        Returns:
            章节内容文本，不存在返回None
        """
        chapter_dir = self.books_root / slug / "chapters" / f"ch-{chapter_id:04d}"
        body_path = chapter_dir / "body.md"

        if not body_path.exists():
            return None

        try:
            return body_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read chapter {chapter_id} for {slug}: {e}")
            return None

    def count_words(self, text: str) -> int:
        """
        统计文本字数（支持中英文）

        Args:
            text: 文本内容

        Returns:
            字数
        """
        # 移除Markdown标记
        text = re.sub(r'[#*`\[\]()]', '', text)

        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

        # 统计英文单词
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))

        return chinese_chars + english_words
```

- [ ] **Step 4: 更新repositories/__init__.py**

```python
"""
数据访问层：文件系统和数据库操作
"""
from .stats_repository import StatsRepository

__all__ = ["StatsRepository"]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/web/repositories/test_stats_repository.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add web/repositories/stats_repository.py web/repositories/__init__.py tests/web/repositories/test_stats_repository.py
git commit -m "feat: add statistics repository with tests"
```

---

## Task 7: 创建统计服务层

**Files:**
- Create: `web/services/stats_service.py`
- Modify: `web/services/__init__.py`

- [ ] **Step 1: 写入服务层测试**

Create: `tests/web/services/test_stats_service.py`

```python
"""测试统计服务层"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from aitext.web.services.stats_service import StatsService
from aitext.web.repositories.stats_repository import StatsRepository


@pytest.fixture
def temp_books_dir():
    """创建临时书籍目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        books_dir = Path(tmpdir) / "books"
        books_dir.mkdir()

        # 创建测试书籍
        book1 = books_dir / "book-1"
        book1.mkdir()
        (book1 / "manifest.json").write_text(
            '{"title": "Book 1", "stage": "writing", "genre": "fantasy"}'
        )
        (book1 / "outline.json").write_text(
            '{"chapters": [{"id": 1, "title": "Ch1"}, {"id": 2, "title": "Ch2"}]}'
        )

        # 创建章节内容
        ch1 = book1 / "chapters" / "ch-0001"
        ch1.mkdir(parents=True)
        (ch1 / "body.md").write_text("Test content " * 100)

        yield books_dir


@pytest.fixture
def stats_service(temp_books_dir):
    """创建统计服务实例"""
    repo = StatsRepository(temp_books_dir)
    return StatsService(repo)


def test_get_global_stats(stats_service):
    """测试获取全局统计"""
    stats = stats_service.get_global_stats()

    assert stats.total_books == 1
    assert stats.total_chapters == 2
    assert stats.total_words > 0
    assert "writing" in stats.books_by_stage


def test_get_book_stats(stats_service):
    """测试获取书籍统计"""
    stats = stats_service.get_book_stats("book-1")

    assert stats is not None
    assert stats.slug == "book-1"
    assert stats.title == "Book 1"
    assert stats.total_chapters == 2
    assert stats.completed_chapters >= 0
    assert 0 <= stats.completion_rate <= 1


def test_get_book_stats_not_found(stats_service):
    """测试获取不存在的书籍"""
    stats = stats_service.get_book_stats("nonexistent")
    assert stats is None


def test_get_chapter_stats(stats_service):
    """测试获取章节统计"""
    stats = stats_service.get_chapter_stats("book-1", 1)

    assert stats is not None
    assert stats.chapter_id == 1
    assert stats.word_count > 0
    assert stats.has_content is True


def test_get_writing_progress(stats_service):
    """测试获取写作进度"""
    progress = stats_service.get_writing_progress("book-1", days=7)

    assert isinstance(progress, list)
    # 可能为空，因为没有历史数据
    assert len(progress) >= 0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/web/services/test_stats_service.py -v
```

Expected: FAIL - 模块不存在

- [ ] **Step 3: 实现stats_service.py**

```python
"""统计服务层"""
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from ..models.stats_models import (
    GlobalStats,
    BookStats,
    ChapterStats,
    WritingProgress,
)
from ..repositories.stats_repository import StatsRepository

logger = logging.getLogger(__name__)


class StatsService:
    """统计服务"""

    def __init__(self, repository: StatsRepository):
        """
        初始化服务

        Args:
            repository: 统计数据访问层
        """
        self.repo = repository

    def get_global_stats(self) -> GlobalStats:
        """
        获取全局统计数据

        Returns:
            全局统计对象
        """
        slugs = self.repo.get_all_book_slugs()

        total_books = len(slugs)
        total_chapters = 0
        total_words = 0
        total_characters = 0
        books_by_stage = {}

        for slug in slugs:
            manifest = self.repo.get_book_manifest(slug)
            if not manifest:
                continue

            # 统计阶段
            stage = manifest.get("stage", "unknown")
            books_by_stage[stage] = books_by_stage.get(stage, 0) + 1

            # 统计章节和字数
            outline = self.repo.get_book_outline(slug)
            if outline and "chapters" in outline:
                chapters = outline["chapters"]
                total_chapters += len(chapters)

                for chapter in chapters:
                    content = self.repo.get_chapter_content(slug, chapter["id"])
                    if content:
                        total_words += self.repo.count_words(content)

        return GlobalStats(
            total_books=total_books,
            total_chapters=total_chapters,
            total_words=total_words,
            total_characters=total_characters,
            books_by_stage=books_by_stage,
        )

    def get_book_stats(self, slug: str) -> Optional[BookStats]:
        """
        获取单本书籍统计

        Args:
            slug: 书籍标识

        Returns:
            书籍统计对象，不存在返回None
        """
        manifest = self.repo.get_book_manifest(slug)
        if not manifest:
            return None

        outline = self.repo.get_book_outline(slug)
        if not outline or "chapters" not in outline:
            return None

        chapters = outline["chapters"]
        total_chapters = len(chapters)
        completed_chapters = 0
        total_words = 0

        for chapter in chapters:
            content = self.repo.get_chapter_content(slug, chapter["id"])
            if content:
                completed_chapters += 1
                total_words += self.repo.count_words(content)

        avg_chapter_words = total_words / total_chapters if total_chapters > 0 else 0
        completion_rate = completed_chapters / total_chapters if total_chapters > 0 else 0

        return BookStats(
            slug=slug,
            title=manifest.get("title", "Untitled"),
            total_chapters=total_chapters,
            completed_chapters=completed_chapters,
            total_words=total_words,
            avg_chapter_words=avg_chapter_words,
            completion_rate=completion_rate,
            last_updated=datetime.now(),
        )

    def get_chapter_stats(self, slug: str, chapter_id: int) -> Optional[ChapterStats]:
        """
        获取章节统计

        Args:
            slug: 书籍标识
            chapter_id: 章节ID

        Returns:
            章节统计对象，不存在返回None
        """
        outline = self.repo.get_book_outline(slug)
        if not outline or "chapters" not in outline:
            return None

        # 查找章节标题
        chapter_title = "Unknown"
        for ch in outline["chapters"]:
            if ch["id"] == chapter_id:
                chapter_title = ch.get("title", f"Chapter {chapter_id}")
                break

        content = self.repo.get_chapter_content(slug, chapter_id)
        has_content = content is not None

        if not has_content:
            return ChapterStats(
                chapter_id=chapter_id,
                title=chapter_title,
                word_count=0,
                character_count=0,
                paragraph_count=0,
                has_content=False,
            )

        word_count = self.repo.count_words(content)
        character_count = len(content)
        paragraph_count = len([p for p in content.split("\n\n") if p.strip()])

        return ChapterStats(
            chapter_id=chapter_id,
            title=chapter_title,
            word_count=word_count,
            character_count=character_count,
            paragraph_count=paragraph_count,
            has_content=True,
        )

    def get_writing_progress(self, slug: str, days: int = 30) -> List[WritingProgress]:
        """
        获取写作进度（最近N天）

        Args:
            slug: 书籍标识
            days: 天数

        Returns:
            写作进度列表
        """
        # TODO: 实现基于文件修改时间的进度追踪
        # 当前返回空列表，Week 2实现
        return []
```

- [ ] **Step 4: 更新services/__init__.py**

```python
"""
服务层：业务逻辑处理
"""
from .stats_service import StatsService

__all__ = ["StatsService"]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/web/services/test_stats_service.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add web/services/stats_service.py web/services/__init__.py tests/web/services/test_stats_service.py
git commit -m "feat: add statistics service layer with tests"
```

---

## Task 8: 创建统计API路由

**Files:**
- Create: `web/routers/stats.py`
- Modify: `web/routers/__init__.py`

- [ ] **Step 1: 写入路由测试**

Create: `tests/web/routers/test_stats.py`

```python
"""测试统计API路由"""
import pytest
import tempfile
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from aitext.web.routers.stats import create_stats_router
from aitext.web.repositories.stats_repository import StatsRepository
from aitext.web.services.stats_service import StatsService
from aitext.web.middleware.error_handler import add_error_handlers


@pytest.fixture
def test_app():
    """创建测试应用"""
    with tempfile.TemporaryDirectory() as tmpdir:
        books_dir = Path(tmpdir) / "books"
        books_dir.mkdir()

        # 创建测试数据
        book1 = books_dir / "test-book"
        book1.mkdir()
        (book1 / "manifest.json").write_text('{"title": "Test", "stage": "writing"}')
        (book1 / "outline.json").write_text('{"chapters": [{"id": 1, "title": "Ch1"}]}')

        ch1 = book1 / "chapters" / "ch-0001"
        ch1.mkdir(parents=True)
        (ch1 / "body.md").write_text("Test " * 100)

        # 创建应用
        app = FastAPI()
        add_error_handlers(app)

        repo = StatsRepository(books_dir)
        service = StatsService(repo)
        router = create_stats_router(service)

        app.include_router(router, prefix="/api/stats")

        yield app


def test_get_global_stats(test_app):
    """测试获取全局统计"""
    client = TestClient(test_app)
    response = client.get("/api/stats/global")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["total_books"] == 1


def test_get_book_stats(test_app):
    """测试获取书籍统计"""
    client = TestClient(test_app)
    response = client.get("/api/stats/book/test-book")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["slug"] == "test-book"
    assert data["data"]["total_chapters"] == 1


def test_get_book_stats_not_found(test_app):
    """测试获取不存在的书籍"""
    client = TestClient(test_app)
    response = client.get("/api/stats/book/nonexistent")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["code"] == "NOT_FOUND"


def test_get_chapter_stats(test_app):
    """测试获取章节统计"""
    client = TestClient(test_app)
    response = client.get("/api/stats/book/test-book/chapter/1")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["chapter_id"] == 1


def test_get_writing_progress(test_app):
    """测试获取写作进度"""
    client = TestClient(test_app)
    response = client.get("/api/stats/book/test-book/progress?days=7")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/web/routers/test_stats.py -v
```

Expected: FAIL - 模块不存在

- [ ] **Step 3: 实现stats.py路由**

```python
"""统计API路由"""
from fastapi import APIRouter, HTTPException, Query
from typing import List

from ..models.responses import SuccessResponse
from ..models.stats_models import (
    GlobalStats,
    BookStats,
    ChapterStats,
    WritingProgress,
)
from ..services.stats_service import StatsService


def create_stats_router(stats_service: StatsService) -> APIRouter:
    """
    创建统计路由

    Args:
        stats_service: 统计服务实例

    Returns:
        配置好的路由器
    """
    router = APIRouter(tags=["statistics"])

    @router.get("/global", response_model=SuccessResponse[GlobalStats])
    async def get_global_stats():
        """获取全局统计数据"""
        stats = stats_service.get_global_stats()
        return SuccessResponse(data=stats)

    @router.get("/book/{slug}", response_model=SuccessResponse[BookStats])
    async def get_book_stats(slug: str):
        """获取单本书籍统计"""
        stats = stats_service.get_book_stats(slug)
        if not stats:
            raise HTTPException(status_code=404, detail=f"Book '{slug}' not found")
        return SuccessResponse(data=stats)

    @router.get("/book/{slug}/chapter/{chapter_id}", response_model=SuccessResponse[ChapterStats])
    async def get_chapter_stats(slug: str, chapter_id: int):
        """获取章节统计"""
        stats = stats_service.get_chapter_stats(slug, chapter_id)
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter {chapter_id} not found in book '{slug}'"
            )
        return SuccessResponse(data=stats)

    @router.get("/book/{slug}/progress", response_model=SuccessResponse[List[WritingProgress]])
    async def get_writing_progress(
        slug: str,
        days: int = Query(default=30, ge=1, le=365, description="天数")
    ):
        """获取写作进度（最近N天）"""
        progress = stats_service.get_writing_progress(slug, days)
        return SuccessResponse(data=progress)

    return router
```

- [ ] **Step 4: 更新routers/__init__.py**

```python
"""
路由模块：处理HTTP请求和响应
"""
from fastapi import APIRouter
from .stats import create_stats_router

__all__ = ["APIRouter", "create_stats_router"]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/web/routers/test_stats.py -v
```

Expected: PASS - 所有测试通过

- [ ] **Step 6: Commit**

```bash
git add web/routers/stats.py web/routers/__init__.py tests/web/routers/test_stats.py
git commit -m "feat: add statistics API router with tests"
```

---

## Task 9: 集成统计路由到主应用

**Files:**
- Modify: `web/app.py`

- [ ] **Step 1: 在app.py中导入新模块**

在 `web/app.py` 的导入部分添加：

```python
from .middleware.error_handler import add_error_handlers
from .middleware.logging_config import setup_logging
from .repositories.stats_repository import StatsRepository
from .services.stats_service import StatsService
from .routers.stats import create_stats_router
```

- [ ] **Step 2: 在app.py中初始化统计模块**

在创建 FastAPI app 之后，添加：

```python
# 设置日志
setup_logging(level="INFO")

# 添加错误处理
add_error_handlers(app)

# 初始化统计模块
books_root = Path(__file__).parent.parent / "books"
stats_repo = StatsRepository(books_root)
stats_service = StatsService(stats_repo)
stats_router = create_stats_router(stats_service)

# 注册统计路由
app.include_router(stats_router, prefix="/api/stats", tags=["statistics"])
```

- [ ] **Step 3: 测试统计API端点**

启动服务器：

```bash
cd aitext
python -m aitext.web.app
```

在另一个终端测试：

```bash
curl http://localhost:8000/api/stats/global
```

Expected: 返回JSON格式的全局统计数据

- [ ] **Step 4: 测试API文档**

访问: http://localhost:8000/docs

Expected: 看到新的 `/api/stats/*` 端点

- [ ] **Step 5: Commit**

```bash
git add web/app.py
git commit -m "feat: integrate statistics router into main app"
```

---

## Task 10: 创建前端API类型定义

**Files:**
- Create: `web-app/src/types/api.ts`

- [ ] **Step 1: 创建types目录**

```bash
mkdir -p web-app/src/types
```

- [ ] **Step 2: 创建api.ts类型定义文件**

```typescript
/**
 * API响应类型定义
 */

// ============ 通用响应类型 ============

export interface SuccessResponse<T> {
  success: true
  data: T
  message?: string
}

export interface ErrorResponse {
  success: false
  message: string
  code: string
  details?: any
}

export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse

// ============ 统计数据类型 ============

export interface GlobalStats {
  total_books: number
  total_chapters: number
  total_words: number
  total_characters: number
  books_by_stage: Record<string, number>
}

export interface BookStats {
  slug: string
  title: string
  total_chapters: number
  completed_chapters: number
  total_words: number
  avg_chapter_words: number
  completion_rate: number
  last_updated: string
}

export interface ChapterStats {
  chapter_id: number
  title: string
  word_count: number
  character_count: number
  paragraph_count: number
  has_content: boolean
}

export interface WritingProgress {
  date: string
  words_written: number
  chapters_completed: number
}

export interface ContentAnalysis {
  character_mentions: Record<string, number>
  dialogue_ratio: number
  scene_count: number
  avg_paragraph_length: number
}

// ============ 书籍相关类型 ============

export interface BookListItem {
  title: string
  slug: string
  genre: string
  stage_label: string
  has_bible?: boolean
  has_outline?: boolean
}

export interface BookDesk {
  book: BookListItem | null
  chapters: Array<{
    id: number
    title: string
    has_file: boolean
    one_liner?: string
  }>
}

export interface Character {
  id: string
  name: string
  aliases: string[]
  role: string
  traits: string
  note: string
}

export interface Relationship {
  id: string
  source_id: string
  target_id: string
  label: string
  note: string
  directed: boolean
}

export interface CastGraph {
  version: number
  characters: Character[]
  relationships: Relationship[]
}

// ============ 章节相关类型 ============

export interface ChapterBody {
  content: string
  filename: string | null
}

export interface ChapterReview {
  status: string
  memo: string
}

export interface ChapterStructure {
  chapter_id: number
  storage_dir: string | null
  meta: Record<string, unknown> | null
  has_content: boolean
  composite_char_len: number
}

// ============ 聊天相关类型 ============

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatResponse {
  ok: boolean
  reply?: string
  llm_enabled?: boolean
  tool_calls?: Array<{
    name: string
    ok: boolean
    detail: string
  }>
}

export interface ChatStreamEvent {
  type: 'chunk' | 'tool' | 'done' | 'error'
  content?: string
  tool_name?: string
  tool_detail?: string
  error?: string
}

// ============ 任务相关类型 ============

export interface JobStatus {
  status: string
  message?: string
  phase?: string
  error?: string
  done?: boolean
}

export interface JobCreateResponse {
  job_id: string
}
```

- [ ] **Step 3: 验证TypeScript编译**

```bash
cd web-app
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 4: Commit**

```bash
git add web-app/src/types/api.ts
git commit -m "feat: add frontend API type definitions"
```

---

## Task 11: 创建统计API客户端

**Files:**
- Create: `web-app/src/api/stats.ts`
- Modify: `web-app/src/api/book.ts`

- [ ] **Step 1: 创建stats.ts API客户端**

```typescript
import axios from 'axios'
import type {
  GlobalStats,
  BookStats,
  ChapterStats,
  WritingProgress,
  SuccessResponse,
} from '../types/api'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 添加响应拦截器
request.interceptors.response.use(response => response.data)

export const statsApi = {
  /**
   * 获取全局统计数据
   */
  getGlobal: () =>
    request.get<SuccessResponse<GlobalStats>>('/stats/global')
      .then(res => res.data),

  /**
   * 获取单本书籍统计
   */
  getBook: (slug: string) =>
    request.get<SuccessResponse<BookStats>>(`/stats/book/${slug}`)
      .then(res => res.data),

  /**
   * 获取章节统计
   */
  getChapter: (slug: string, chapterId: number) =>
    request.get<SuccessResponse<ChapterStats>>(`/stats/book/${slug}/chapter/${chapterId}`)
      .then(res => res.data),

  /**
   * 获取写作进度
   */
  getProgress: (slug: string, days: number = 30) =>
    request.get<SuccessResponse<WritingProgress[]>>(`/stats/book/${slug}/progress`, {
      params: { days }
    }).then(res => res.data),

  /**
   * 并行获取书籍的所有统计数据
   */
  getBookAllStats: async (slug: string) => {
    const [bookStats, progress] = await Promise.all([
      statsApi.getBook(slug),
      statsApi.getProgress(slug, 30),
    ])

    return {
      bookStats,
      progress,
    }
  },
}
```

- [ ] **Step 2: 更新book.ts使用新类型**

在 `web-app/src/api/book.ts` 顶部添加导入：

```typescript
import type {
  BookListItem,
  BookDesk,
  CastGraph,
  ChapterBody,
  ChapterReview,
  ChapterStructure,
  ChatMessage,
  ChatResponse,
  JobStatus,
  JobCreateResponse,
} from '../types/api'
```

- [ ] **Step 3: 替换book.ts中的any类型**

将 `getList` 的返回类型改为：

```typescript
getList: () => request.get('/books') as Promise<BookListItem[]>,
```

将 `create` 的返回类型改为：

```typescript
create: (data: any) => request.post('/jobs/create-book', data) as Promise<JobCreateResponse>,
```

- [ ] **Step 4: 验证TypeScript编译**

```bash
cd web-app
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 5: Commit**

```bash
git add web-app/src/api/stats.ts web-app/src/api/book.ts
git commit -m "feat: add statistics API client with type safety"
```

---

## Task 12: 创建统计状态管理Store

**Files:**
- Create: `web-app/src/stores/statsStore.ts`

- [ ] **Step 1: 创建stores目录（如果不存在）**

```bash
mkdir -p web-app/src/stores
```

- [ ] **Step 2: 创建statsStore.ts**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statsApi } from '../api/stats'
import type {
  GlobalStats,
  BookStats,
  ChapterStats,
  WritingProgress,
} from '../types/api'

export const useStatsStore = defineStore('stats', () => {
  // ============ State ============
  const globalStats = ref<GlobalStats | null>(null)
  const bookStatsCache = ref<Map<string, BookStats>>(new Map())
  const chapterStatsCache = ref<Map<string, ChapterStats>>(new Map())
  const progressCache = ref<Map<string, WritingProgress[]>>(new Map())

  const loading = ref(false)
  const error = ref<string | null>(null)

  // ============ Getters ============
  const hasGlobalStats = computed(() => globalStats.value !== null)

  const getBookStats = computed(() => (slug: string) => {
    return bookStatsCache.value.get(slug) || null
  })

  const getChapterStats = computed(() => (slug: string, chapterId: number) => {
    const key = `${slug}-${chapterId}`
    return chapterStatsCache.value.get(key) || null
  })

  const getProgress = computed(() => (slug: string) => {
    return progressCache.value.get(slug) || []
  })

  // ============ Actions ============

  /**
   * 加载全局统计
   */
  async function loadGlobalStats(force = false) {
    if (!force && globalStats.value) {
      return globalStats.value
    }

    loading.value = true
    error.value = null

    try {
      const data = await statsApi.getGlobal()
      globalStats.value = data
      return data
    } catch (err: any) {
      error.value = err.message || 'Failed to load global stats'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载书籍统计
   */
  async function loadBookStats(slug: string, force = false) {
    if (!force && bookStatsCache.value.has(slug)) {
      return bookStatsCache.value.get(slug)!
    }

    loading.value = true
    error.value = null

    try {
      const data = await statsApi.getBook(slug)
      bookStatsCache.value.set(slug, data)
      return data
    } catch (err: any) {
      error.value = err.message || `Failed to load stats for ${slug}`
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载章节统计
   */
  async function loadChapterStats(slug: string, chapterId: number, force = false) {
    const key = `${slug}-${chapterId}`

    if (!force && chapterStatsCache.value.has(key)) {
      return chapterStatsCache.value.get(key)!
    }

    loading.value = true
    error.value = null

    try {
      const data = await statsApi.getChapter(slug, chapterId)
      chapterStatsCache.value.set(key, data)
      return data
    } catch (err: any) {
      error.value = err.message || `Failed to load chapter ${chapterId} stats`
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载写作进度
   */
  async function loadProgress(slug: string, days = 30, force = false) {
    if (!force && progressCache.value.has(slug)) {
      return progressCache.value.get(slug)!
    }

    loading.value = true
    error.value = null

    try {
      const data = await statsApi.getProgress(slug, days)
      progressCache.value.set(slug, data)
      return data
    } catch (err: any) {
      error.value = err.message || `Failed to load progress for ${slug}`
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 并行加载书籍所有统计数据
   */
  async function loadBookAllStats(slug: string, force = false) {
    loading.value = true
    error.value = null

    try {
      const { bookStats, progress } = await statsApi.getBookAllStats(slug)

      bookStatsCache.value.set(slug, bookStats)
      progressCache.value.set(slug, progress)

      return { bookStats, progress }
    } catch (err: any) {
      error.value = err.message || `Failed to load all stats for ${slug}`
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 清除缓存
   */
  function clearCache(slug?: string) {
    if (slug) {
      bookStatsCache.value.delete(slug)
      progressCache.value.delete(slug)

      // 清除该书籍的所有章节缓存
      const keysToDelete: string[] = []
      chapterStatsCache.value.forEach((_, key) => {
        if (key.startsWith(`${slug}-`)) {
          keysToDelete.push(key)
        }
      })
      keysToDelete.forEach(key => chapterStatsCache.value.delete(key))
    } else {
      globalStats.value = null
      bookStatsCache.value.clear()
      chapterStatsCache.value.clear()
      progressCache.value.clear()
    }
  }

  /**
   * 重置错误状态
   */
  function clearError() {
    error.value = null
  }

  return {
    // State
    globalStats,
    loading,
    error,

    // Getters
    hasGlobalStats,
    getBookStats,
    getChapterStats,
    getProgress,

    // Actions
    loadGlobalStats,
    loadBookStats,
    loadChapterStats,
    loadProgress,
    loadBookAllStats,
    clearCache,
    clearError,
  }
})
```

- [ ] **Step 3: 验证TypeScript编译**

```bash
cd web-app
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 4: Commit**

```bash
git add web-app/src/stores/statsStore.ts
git commit -m "feat: add statistics Pinia store with caching"
```

---

## Task 13: 安装和配置ECharts

**Files:**
- Modify: `web-app/package.json`
- Create: `web-app/src/plugins/echarts.ts`

- [ ] **Step 1: 安装vue-echarts和echarts**

```bash
cd web-app
npm install echarts vue-echarts
```

- [ ] **Step 2: 验证安装**

```bash
npm list echarts vue-echarts
```

Expected: 显示已安装的版本

- [ ] **Step 3: 创建plugins目录**

```bash
mkdir -p web-app/src/plugins
```

- [ ] **Step 4: 创建echarts.ts配置文件**

```typescript
/**
 * ECharts 配置和注册
 */
import { use } from 'echarts/core'

// 导入图表类型
import {
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
  GraphChart,
} from 'echarts/charts'

// 导入组件
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent,
} from 'echarts/components'

// 导入渲染器
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
use([
  // 图表类型
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  RadarChart,
  GraphChart,

  // 组件
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent,

  // 渲染器
  CanvasRenderer,
])

// 默认主题配置
export const defaultTheme = {
  color: [
    '#5470c6',
    '#91cc75',
    '#fac858',
    '#ee6666',
    '#73c0de',
    '#3ba272',
    '#fc8452',
    '#9a60b4',
    '#ea7ccc',
  ],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  title: {
    textStyle: {
      fontSize: 16,
      fontWeight: 600,
    },
  },
  tooltip: {
    backgroundColor: 'rgba(50, 50, 50, 0.95)',
    borderWidth: 0,
    textStyle: {
      color: '#fff',
    },
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true,
  },
}

// 通用图表配置
export const commonChartOptions = {
  animation: true,
  animationDuration: 750,
  animationEasing: 'cubicOut',
}
```

- [ ] **Step 5: 在main.ts中注册ECharts**

在 `web-app/src/main.ts` 中添加：

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ECharts from 'vue-echarts'
import App from './App.vue'
import router from './router'

// 导入ECharts配置
import './plugins/echarts'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 全局注册ECharts组件
app.component('VChart', ECharts)

app.mount('#app')
```

- [ ] **Step 6: 验证构建**

```bash
cd web-app
npm run build
```

Expected: 构建成功，无错误

- [ ] **Step 7: Commit**

```bash
git add web-app/package.json web-app/package-lock.json web-app/src/plugins/echarts.ts web-app/src/main.ts
git commit -m "feat: install and configure ECharts with vue-echarts"
```

---

## Task 14: 创建测试目录结构

**Files:**
- Create: `tests/web/models/__init__.py`
- Create: `tests/web/middleware/__init__.py`
- Create: `tests/web/repositories/__init__.py`
- Create: `tests/web/services/__init__.py`
- Create: `tests/web/routers/__init__.py`

- [ ] **Step 1: 创建测试目录结构**

```bash
mkdir -p tests/web/models
mkdir -p tests/web/middleware
mkdir -p tests/web/repositories
mkdir -p tests/web/services
mkdir -p tests/web/routers
```

- [ ] **Step 2: 创建__init__.py文件**

```bash
touch tests/web/__init__.py
touch tests/web/models/__init__.py
touch tests/web/middleware/__init__.py
touch tests/web/repositories/__init__.py
touch tests/web/services/__init__.py
touch tests/web/routers/__init__.py
```

- [ ] **Step 3: 创建pytest配置**

Create: `tests/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

- [ ] **Step 4: 验证pytest可以发现测试**

```bash
pytest --collect-only tests/web/
```

Expected: 显示所有测试用例

- [ ] **Step 5: Commit**

```bash
git add tests/web/ tests/pytest.ini
git commit -m "feat: create test directory structure"
```

---

## Task 15: 运行所有测试并验证

**Files:**
- None (verification task)

- [ ] **Step 1: 运行所有后端测试**

```bash
pytest tests/web/ -v
```

Expected: 所有测试通过

- [ ] **Step 2: 检查测试覆盖率**

```bash
pytest tests/web/ --cov=aitext.web --cov-report=term-missing
```

Expected: 覆盖率报告显示

- [ ] **Step 3: 运行前端类型检查**

```bash
cd web-app
npm run type-check
```

Expected: 无类型错误

- [ ] **Step 4: 运行前端构建**

```bash
cd web-app
npm run build
```

Expected: 构建成功

- [ ] **Step 5: 启动开发服务器测试**

启动后端：

```bash
cd aitext
python -m aitext.web.app
```

启动前端：

```bash
cd web-app
npm run dev
```

访问: http://localhost:5173

Expected: 应用正常启动，无控制台错误

- [ ] **Step 6: 测试统计API端点**

```bash
curl http://localhost:8000/api/stats/global
```

Expected: 返回JSON格式的统计数据

- [ ] **Step 7: 最终提交**

```bash
git add -A
git commit -m "chore: Week 1 infrastructure complete - all tests passing"
```

---

## Summary

Week 1 完成的工作：

### 后端 (Backend)
- ✅ 创建模块化目录结构 (routers, services, repositories, models, middleware, utils)
- ✅ 实现统一响应模型 (SuccessResponse, ErrorResponse, PaginatedResponse)
- ✅ 实现统一错误处理中间件
- ✅ 实现统一日志配置
- ✅ 创建统计数据模型 (GlobalStats, BookStats, ChapterStats, etc.)
- ✅ 实现统计数据访问层 (StatsRepository)
- ✅ 实现统计服务层 (StatsService)
- ✅ 实现统计API路由 (5个端点)
- ✅ 集成到主应用

### 前端 (Frontend)
- ✅ 创建完整的TypeScript类型定义 (api.ts)
- ✅ 创建统计API客户端 (stats.ts)
- ✅ 更新现有API使用类型安全
- ✅ 创建Pinia统计Store (带缓存)
- ✅ 安装和配置ECharts + vue-echarts
- ✅ 创建ECharts插件配置

### 测试 (Testing)
- ✅ 完整的单元测试覆盖
- ✅ 测试目录结构
- ✅ Pytest配置

### API端点
- `GET /api/stats/global` - 全局统计
- `GET /api/stats/book/{slug}` - 书籍统计
- `GET /api/stats/book/{slug}/chapter/{chapter_id}` - 章节统计
- `GET /api/stats/book/{slug}/progress` - 写作进度

---

## Next Steps (Week 2)

Week 2 将实现：
- 主页侧边栏统计卡片
- 工作台顶部统计条
- 3个核心图表组件
- 替换vis-network为ECharts Graph
- 实现响应式布局

---
