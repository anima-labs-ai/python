"""Tests for Anima and AsyncAnima client initialization and configuration."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from anima._client import Anima, AsyncAnima
from anima._http import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT


class TestAnimaInit:
    """Sync client initialization tests."""

    def test_default_params(self) -> None:
        client = Anima(api_key="sk-test")
        assert client._http._api_key == "sk-test"
        assert client._http._base_url == DEFAULT_BASE_URL
        assert client._http._timeout == DEFAULT_TIMEOUT
        assert client._http._max_retries == DEFAULT_MAX_RETRIES
        client.close()

    def test_custom_params(self) -> None:
        client = Anima(
            api_key="sk-custom",
            base_url="https://custom.api.com/",
            timeout=60.0,
            max_retries=5,
        )
        assert client._http._api_key == "sk-custom"
        assert client._http._base_url == "https://custom.api.com"  # trailing slash stripped
        assert client._http._timeout == 60.0
        assert client._http._max_retries == 5
        client.close()

    def test_context_manager(self) -> None:
        with Anima(api_key="sk-test") as client:
            assert client._http._api_key == "sk-test"
        # After exiting, the client should be closed (no explicit assertion needed,
        # just verifying no exception is raised)

    def test_has_all_resources(self) -> None:
        client = Anima(api_key="sk-test")
        resource_names = [
            "addresses", "agents", "cards", "domains", "emails",
            "events", "identity", "messages", "organizations",
            "phones", "pods", "registry", "security", "vault",
            "wallet", "webhooks", "a2a", "audit", "compliance", "anomaly",
        ]
        for name in resource_names:
            assert hasattr(client, name), f"Missing resource: {name}"
        client.close()

    def test_close_calls_http_close(self) -> None:
        client = Anima(api_key="sk-test")
        with patch.object(client._http, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()


class TestAsyncAnimaInit:
    """Async client initialization tests."""

    def test_default_params(self) -> None:
        client = AsyncAnima(api_key="sk-test")
        assert client._http._api_key == "sk-test"
        assert client._http._base_url == DEFAULT_BASE_URL

    def test_custom_params(self) -> None:
        client = AsyncAnima(
            api_key="sk-custom",
            base_url="https://custom.api.com/",
            timeout=15.0,
            max_retries=1,
        )
        assert client._http._base_url == "https://custom.api.com"
        assert client._http._timeout == 15.0
        assert client._http._max_retries == 1

    def test_has_all_resources(self) -> None:
        client = AsyncAnima(api_key="sk-test")
        resource_names = [
            "addresses", "agents", "cards", "domains", "emails",
            "events", "identity", "messages", "organizations",
            "phones", "pods", "registry", "security", "vault",
            "wallet", "webhooks", "a2a", "audit", "compliance", "anomaly",
        ]
        for name in resource_names:
            assert hasattr(client, name), f"Missing resource: {name}"

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with AsyncAnima(api_key="sk-test") as client:
            assert client._http._api_key == "sk-test"

    @pytest.mark.asyncio
    async def test_async_close(self) -> None:
        client = AsyncAnima(api_key="sk-test")
        with patch.object(client._http, "close") as mock_close:
            await client.close()
            mock_close.assert_called_once()
