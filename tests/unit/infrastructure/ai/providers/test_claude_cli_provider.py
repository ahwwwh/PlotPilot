"""ClaudeCliProvider 测试 — 通过 claude CLI subprocess 调用"""
import pytest
from unittest.mock import AsyncMock, patch
from domain.ai.value_objects.prompt import Prompt
from domain.ai.services.llm_service import GenerationConfig
from infrastructure.ai.config.settings import Settings
from infrastructure.ai.providers.claude_cli_provider import ClaudeCliProvider


class TestClaudeCliProvider:

    @pytest.fixture
    def settings(self):
        return Settings(default_model="claude-opus-4-5")

    @pytest.fixture
    def prompt(self):
        return Prompt(system="你是作家", user="写一段故事")

    @pytest.fixture
    def config(self):
        return GenerationConfig(model="claude-opus-4-5", max_tokens=2048, temperature=0.7)

    def test_raises_if_claude_cli_not_found(self, settings):
        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="claude"):
                ClaudeCliProvider(settings)

    def test_instantiates_when_cli_found(self, settings):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            provider = ClaudeCliProvider(settings)
        assert provider is not None

    @pytest.mark.asyncio
    async def test_generate_returns_content(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            provider = ClaudeCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"\xe7\x94\x9f\xe6\x88\x90\xe7\x9a\x84\xe5\x86\x85\xe5\xae\xb9", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await provider.generate(prompt, config)

        assert result.content == "生成的内容"
        assert result.token_usage.input_tokens >= 0
        assert result.token_usage.output_tokens >= 0

    @pytest.mark.asyncio
    async def test_generate_passes_system_prompt_arg(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            provider = ClaudeCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"output", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            await provider.generate(prompt, config)

        call_args = list(mock_exec.call_args[0])
        assert "--system-prompt" in call_args
        idx = call_args.index("--system-prompt")
        assert call_args[idx + 1] == "你是作家"

    @pytest.mark.asyncio
    async def test_generate_raises_on_cli_failure(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            provider = ClaudeCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(b"", b"error message"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="claude CLI"):
                await provider.generate(prompt, config)

    @pytest.mark.asyncio
    async def test_generate_raises_on_empty_output(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            provider = ClaudeCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"   ", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="empty"):
                await provider.generate(prompt, config)

    @pytest.mark.asyncio
    async def test_stream_generate_yields_full_content(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            provider = ClaudeCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"hello world", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            chunks = []
            async for chunk in provider.stream_generate(prompt, config):
                chunks.append(chunk)

        assert "".join(chunks) == "hello world"
