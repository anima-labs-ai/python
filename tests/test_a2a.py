"""Tests for A2AResource.dispatch (fire-and-forget task dispatch by DID)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import A2ATaskOutput
from anima.resources.a2a import A2AResource, AsyncA2AResource

from .conftest import A2A_TASK_RAW


class TestDispatch:
    def test_dispatch(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = A2A_TASK_RAW
        resource = A2AResource(mock_http)
        result = resource.dispatch(
            "ag_1",
            to_did="did:web:example.com",
            type="ping",
            input={},
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/agents/ag_1/a2a/dispatch",
            {"fromAgentId": "ag_1", "toDid": "did:web:example.com", "type": "ping", "input": {}},
            options=None,
        )
        assert isinstance(result, A2ATaskOutput)
        assert result.id == "task_001"
        assert result.agent_id == "agent_001"


class TestAsyncDispatch:
    @pytest.mark.asyncio
    async def test_dispatch(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = A2A_TASK_RAW
        resource = AsyncA2AResource(mock_http)
        result = await resource.dispatch(
            "ag_1",
            to_did="did:web:example.com",
            type="ping",
            input={},
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/agents/ag_1/a2a/dispatch",
            {"fromAgentId": "ag_1", "toDid": "did:web:example.com", "type": "ping", "input": {}},
            options=None,
        )
        assert isinstance(result, A2ATaskOutput)
        assert result.id == "task_001"
