"""GeminiCliProvider — 通过本地 gemini CLI (Google OAuth) 调用，无需 API Key"""
import asyncio
import shutil
from typing import AsyncIterator

from domain.ai.services.llm_service import GenerationConfig, GenerationResult
from domain.ai.value_objects.prompt import Prompt
from domain.ai.value_objects.token_usage import TokenUsage
from infrastructure.ai.config.settings import Settings
from infrastructure.ai.providers.base import BaseProvider
from infrastructure.ai.providers.model_resolution import require_resolved_model_id


class GeminiCliProvider(BaseProvider):
    """使用本地 gemini CLI 的 Provider，适合持有 Google 账号但无 API Key 的场景。"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not shutil.which("gemini"):
            raise RuntimeError("gemini CLI 未找到，请先安装：https://github.com/google-gemini/gemini-cli")

    async def generate(self, prompt: Prompt, config: GenerationConfig) -> GenerationResult:
        model = require_resolved_model_id(config.model, self.settings.default_model, provider_label="Gemini CLI")
        full_prompt = f"{prompt.system}\n\n{prompt.user}"
        cmd = (
            "gemini",
            "--prompt", full_prompt,
            "--model", model,
            "--output-format", "text",
            "--yolo",
        )
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.settings.timeout_seconds
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise RuntimeError(f"gemini CLI 超时（>{self.settings.timeout_seconds}s）")

        if proc.returncode != 0:
            raise RuntimeError(f"gemini CLI 失败 (exit {proc.returncode}): {stderr.decode()}")

        content = stdout.decode("utf-8").strip()
        if not content:
            raise RuntimeError("gemini CLI 返回了 empty 内容")

        input_tokens = len(full_prompt) // 4
        output_tokens = len(content) // 4
        return GenerationResult(
            content=content,
            token_usage=TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens),
        )

    async def stream_generate(self, prompt: Prompt, config: GenerationConfig) -> AsyncIterator[str]:
        result = await self.generate(prompt, config)
        chunk_size = 200
        for i in range(0, len(result.content), chunk_size):
            yield result.content[i: i + chunk_size]
