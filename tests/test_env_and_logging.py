"""Tests for environment variable fallback and debug logging."""

from __future__ import annotations

import logging
import os
from unittest.mock import patch

import pytest

from anima._client import Anima, AsyncAnima
from anima._http import DEFAULT_BASE_URL


class TestEnvVarFallback:
    """Test ANIMA_API_KEY and ANIMA_API_URL env var fallback."""

    def test_uses_env_api_key(self) -> None:
        with patch.dict(os.environ, {"ANIMA_API_KEY": "sk_env_test"}, clear=False):
            client = Anima()
            assert client._http._api_key == "sk_env_test"
            client.close()

    def test_explicit_key_takes_precedence(self) -> None:
        with patch.dict(os.environ, {"ANIMA_API_KEY": "sk_env"}, clear=False):
            client = Anima(api_key="sk_explicit")
            assert client._http._api_key == "sk_explicit"
            client.close()

    def test_raises_without_key(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "ANIMA_API_KEY"}
        with (
            patch.dict(os.environ, env, clear=True),
            pytest.raises(ValueError, match="Missing API key"),
        ):
            Anima()

    def test_uses_env_api_url(self) -> None:
        with patch.dict(
            os.environ,
            {"ANIMA_API_KEY": "sk_test", "ANIMA_API_URL": "https://custom.example.com"},
            clear=False,
        ):
            client = Anima()
            assert client._http._base_url == "https://custom.example.com"
            client.close()

    def test_explicit_url_takes_precedence(self) -> None:
        with patch.dict(
            os.environ,
            {"ANIMA_API_KEY": "sk_test", "ANIMA_API_URL": "https://env.example.com"},
            clear=False,
        ):
            client = Anima(base_url="https://explicit.example.com")
            assert client._http._base_url == "https://explicit.example.com"
            client.close()

    def test_defaults_to_production_url(self) -> None:
        env = {k: v for k, v in os.environ.items() if k not in ("ANIMA_API_URL",)}
        with patch.dict(os.environ, env, clear=True):
            client = Anima(api_key="sk_test")
            assert client._http._base_url == DEFAULT_BASE_URL
            client.close()


class TestAsyncEnvVarFallback:
    """Test env var fallback for async client."""

    def test_uses_env_api_key(self) -> None:
        with patch.dict(os.environ, {"ANIMA_API_KEY": "sk_async_env"}, clear=False):
            client = AsyncAnima()
            assert client._http._api_key == "sk_async_env"

    def test_raises_without_key(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "ANIMA_API_KEY"}
        with (
            patch.dict(os.environ, env, clear=True),
            pytest.raises(ValueError, match="Missing API key"),
        ):
            AsyncAnima()

    def test_uses_env_api_url(self) -> None:
        with patch.dict(
            os.environ,
            {"ANIMA_API_KEY": "sk_test", "ANIMA_API_URL": "https://async.example.com"},
            clear=False,
        ):
            client = AsyncAnima()
            assert client._http._base_url == "https://async.example.com"


class TestDebugLogging:
    """Test that debug logging is properly configured."""

    def test_logger_exists(self) -> None:
        anima_logger = logging.getLogger("anima")
        assert anima_logger is not None

    def test_debug_logging_activates_with_env(self) -> None:
        with patch.dict(os.environ, {"ANIMA_LOG": "debug"}, clear=False):
            # Re-import to trigger module-level setup
            import importlib

            import anima._logger

            importlib.reload(anima._logger)

            anima_logger = logging.getLogger("anima")
            assert anima_logger.level == logging.DEBUG
            assert len(anima_logger.handlers) > 0

            # Clean up
            anima_logger.handlers.clear()
            anima_logger.setLevel(logging.WARNING)
