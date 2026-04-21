"""ClaudeCliProvider — 通过本地 claude CLI (OAuth 授权) 调用，无需 API Key"""
import asyncio
import json
import os
import shutil
import subprocess
from typing import AsyncIterator, Optional

from domain.ai.services.llm_service import GenerationConfig, GenerationResult
from domain.ai.value_objects.prompt import Prompt
from domain.ai.value_objects.token_usage import TokenUsage
from infrastructure.ai.config.settings import Settings
from infrastructure.ai.providers.base import BaseProvider
from infrastructure.ai.providers.model_resolution import require_resolved_model_id


def _read_oauth_token_from_keychain() -> Optional[str]:
    """从 macOS keychain 读取 Claude Code OAuth access token。

    subprocess 环境下 claude CLI 直接访问 keychain 可能失败，我们主动读出来通过
    ANTHROPIC_API_KEY 注入子进程。claude CLI 对 OAuth token 走 API Key 通道是可用的
    （OAuth 直接发请求被 Anthropic API 拒绝，但 API Key 通道会转换）。
    """
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None
        payload = json.loads(result.stdout.strip())
        token = payload.get("claudeAiOauth", {}).get("accessToken")
        return token or None
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        return None


class ClaudeCliProvider(BaseProvider):
    """使用本地 claude CLI (Claude Code) 的 Provider，适合持有 OAuth 订阅但无 API Key 的场景。"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not shutil.which("claude"):
            raise RuntimeError("claude CLI 未找到，请先安装 Claude Code：https://claude.ai/code")

    async def generate(self, prompt: Prompt, config: GenerationConfig) -> GenerationResult:
        model = require_resolved_model_id(config.model, self.settings.default_model, provider_label="Claude CLI")
        cmd = (
            "claude",
            "--bare",
            "--print",
            "--output-format", "text",
            "--no-session-persistence",
            "--system-prompt", prompt.system,
            "--model", model,
            prompt.user,
        )

        env = os.environ.copy()
        if not env.get("ANTHROPIC_API_KEY"):
            token = _read_oauth_token_from_keychain()
            if token:
                env["ANTHROPIC_API_KEY"] = token

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.settings.timeout_seconds
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise RuntimeError(f"claude CLI 超时（>{self.settings.timeout_seconds}s）")

        if proc.returncode != 0:
            err = stderr.decode().strip() or stdout.decode().strip() or "(无输出)"
            raise RuntimeError(f"claude CLI 失败 (exit {proc.returncode}): {err}")

        content = stdout.decode("utf-8").strip()
        if not content:
            raise RuntimeError("claude CLI 返回了 empty 内容")
        # 常见鉴权失败会走 exit 0 + stdout "Not logged in"
        low = content.lower()
        if "not logged in" in low or "please run /login" in low:
            raise RuntimeError(f"claude CLI 鉴权失败: {content[:200]}")

        input_tokens = (len(prompt.system) + len(prompt.user)) // 4
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
