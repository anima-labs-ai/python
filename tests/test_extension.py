"""Tests for ExtensionResource (headless connect)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import ConnectExtensionResult
from anima.resources.extension import AsyncExtensionResource, ExtensionResource

from .conftest import EXTENSION_CONNECT_RAW


class TestConnect:
    def test_connect_agent_key_omits_agent_id(self, mock_http: MagicMock) -> None:
        # Agent key path: caller omits agent_id, so no `agentId` in the body.
        mock_http.request.return_value = EXTENSION_CONNECT_RAW
        resource = ExtensionResource(mock_http)
        result = resource.connect()

        mock_http.request.assert_called_once_with(
            "POST",
            "/extension/connect",
            None,
            options=None,
        )
        assert isinstance(result, ConnectExtensionResult)
        assert result.connect_url == "https://useanima.sh/extension/connect#exch_abc123"
        assert result.agent_id == "agent_001"
        assert result.exchange_expires_at == "2025-01-01T00:05:00Z"
        assert result.expires_at == "2025-01-01T01:00:00Z"
        assert result.policy == "pre_approved"

    def test_connect_master_key_sends_agent_id(self, mock_http: MagicMock) -> None:
        # Master key path: caller passes agent_id, which is sent as `agentId`.
        mock_http.request.return_value = EXTENSION_CONNECT_RAW
        resource = ExtensionResource(mock_http)
        resource.connect(agent_id="agent_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/extension/connect",
            {"agentId": "agent_001"},
            options=None,
        )

    def test_connect_with_ttl(self, mock_http: MagicMock) -> None:
        # Only provided keys are sent; both agentId and ttl here.
        mock_http.request.return_value = EXTENSION_CONNECT_RAW
        resource = ExtensionResource(mock_http)
        resource.connect(agent_id="agent_001", ttl="15m")

        mock_http.request.assert_called_once_with(
            "POST",
            "/extension/connect",
            {"agentId": "agent_001", "ttl": "15m"},
            options=None,
        )

    def test_connect_ttl_only(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = EXTENSION_CONNECT_RAW
        resource = ExtensionResource(mock_http)
        resource.connect(ttl="session")

        call_body = mock_http.request.call_args[0][2]
        assert call_body == {"ttl": "session"}

    def test_connect_expires_at_null(self, mock_http: MagicMock) -> None:
        # Pre-approved-with-no-expiry: expiresAt may be null.
        raw = {**EXTENSION_CONNECT_RAW, "expiresAt": None, "policy": "session"}
        mock_http.request.return_value = raw
        resource = ExtensionResource(mock_http)
        result = resource.connect()

        assert result.expires_at is None
        assert result.policy == "session"


class TestAsyncConnect:
    @pytest.mark.asyncio
    async def test_connect(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = EXTENSION_CONNECT_RAW
        resource = AsyncExtensionResource(mock_http)
        result = await resource.connect(agent_id="agent_001", ttl="1h")

        mock_http.request.assert_called_once_with(
            "POST",
            "/extension/connect",
            {"agentId": "agent_001", "ttl": "1h"},
            options=None,
        )
        assert isinstance(result, ConnectExtensionResult)
        assert result.connect_url == "https://useanima.sh/extension/connect#exch_abc123"

    @pytest.mark.asyncio
    async def test_connect_agent_key_omits_agent_id(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = EXTENSION_CONNECT_RAW
        resource = AsyncExtensionResource(mock_http)
        await resource.connect()

        mock_http.request.assert_called_once_with(
            "POST",
            "/extension/connect",
            None,
            options=None,
        )
