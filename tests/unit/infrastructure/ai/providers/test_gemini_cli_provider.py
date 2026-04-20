"""GeminiCliProvider 测试 — 通过 gemini CLI subprocess 调用"""
import pytest
from unittest.mock import AsyncMock, patch
from domain.ai.value_objects.prompt import Prompt
from domain.ai.services.llm_service import GenerationConfig
from infrastructure.ai.config.settings import Settings
from infrastructure.ai.providers.gemini_cli_provider import GeminiCliProvider


class TestGeminiCliProvider:

    @pytest.fixture
    def settings(self):
        return Settings(default_model="gemini-2.0-flash")

    @pytest.fixture
    def prompt(self):
        return Prompt(system="你是作家", user="写一段故事")

    @pytest.fixture
    def config(self):
        return GenerationConfig(model="gemini-2.0-flash", max_tokens=2048, temperature=0.7)

    def test_raises_if_gemini_cli_not_found(self, settings):
        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="gemini"):
                GeminiCliProvider(settings)

    def test_instantiates_when_cli_found(self, settings):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            provider = GeminiCliProvider(settings)
        assert provider is not None

    def test_does_not_require_api_key(self):
        settings = Settings(default_model="gemini-2.0-flash", api_key=None)
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            provider = GeminiCliProvider(settings)
        assert provider is not None

    @pytest.mark.asyncio
    async def test_generate_returns_content(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            provider = GeminiCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"\xe7\x94\x9f\xe6\x88\x90\xe7\x9a\x84\xe5\x86\x85\xe5\xae\xb9", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await provider.generate(prompt, config)

        assert result.content == "生成的内容"
        assert result.token_usage.input_tokens >= 0
        assert result.token_usage.output_tokens >= 0

    @pytest.mark.asyncio
    async def test_generate_combines_system_and_user_prompt(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            provider = GeminiCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"output", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            await provider.generate(prompt, config)

        call_args = list(mock_exec.call_args[0])
        full_prompt_arg = " ".join(call_args)
        assert "你是作家" in full_prompt_arg
        assert "写一段故事" in full_prompt_arg

    @pytest.mark.asyncio
    async def test_generate_raises_on_cli_failure(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            provider = GeminiCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(b"", b"error"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="gemini CLI"):
                await provider.generate(prompt, config)

    @pytest.mark.asyncio
    async def test_generate_raises_on_empty_output(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            provider = GeminiCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with pytest.raises(RuntimeError, match="empty"):
                await provider.generate(prompt, config)

    @pytest.mark.asyncio
    async def test_stream_generate_yields_full_content(self, settings, prompt, config):
        with patch("shutil.which", return_value="/usr/bin/gemini"):
            provider = GeminiCliProvider(settings)

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"hello world", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            chunks = []
            async for chunk in provider.stream_generate(prompt, config):
                chunks.append(chunk)

        assert "".join(chunks) == "hello world"
