"""Infrastructure AI providers module.

仅强制导出基础类型；具体 Provider 在各自依赖可用时再按需导入。
"""

from .base import BaseProvider

__all__ = ["BaseProvider"]

try:
    from .anthropic_provider import AnthropicProvider
    __all__.append("AnthropicProvider")
except ModuleNotFoundError:
    AnthropicProvider = None

try:
    from .openai_provider import OpenAIProvider
    __all__.append("OpenAIProvider")
except ModuleNotFoundError:
    OpenAIProvider = None

try:
    from .gemini_provider import GeminiProvider
    __all__.append("GeminiProvider")
except ModuleNotFoundError:
    GeminiProvider = None

try:
    from .claude_cli_provider import ClaudeCliProvider
    __all__.append("ClaudeCliProvider")
except ModuleNotFoundError:
    ClaudeCliProvider = None

try:
    from .gemini_cli_provider import GeminiCliProvider
    __all__.append("GeminiCliProvider")
except ModuleNotFoundError:
    GeminiCliProvider = None
