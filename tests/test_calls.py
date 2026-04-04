"""Tests for CallsResource with mocked HTTP."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from anima._types import CallOutput, CallTranscript, CreateCallOutput
from anima.resources.calls import CallsResource

from .conftest import mock_http  # noqa: F401 – used via fixture name

# ---------------------------------------------------------------------------
# Raw API response fixtures
# ---------------------------------------------------------------------------

CALL_RAW: dict[str, Any] = {
    "id": "call_001",
    "agentId": "agent_001",
    "phoneIdentityId": "phi_001",
    "direction": "OUTBOUND",
    "tier": "basic",
    "state": "completed",
    "from": "+15550001234",
    "to": "+15559876543",
    "startedAt": "2026-04-03T10:00:00Z",
    "answeredAt": "2026-04-03T10:00:05Z",
    "endedAt": "2026-04-03T10:03:00Z",
    "endReason": "hangup",
    "durationSeconds": 175,
    "createdAt": "2026-04-03T10:00:00Z",
}

CALL_LIST_RAW: dict[str, Any] = {
    "calls": [CALL_RAW],
    "total": 1,
}

CREATE_CALL_RAW: dict[str, Any] = {
    "callId": "call_002",
    "state": "initiated",
    "from": "+15550001234",
    "to": "+15559876543",
    "tier": "basic",
    "direction": "OUTBOUND",
}

TRANSCRIPT_RAW: dict[str, Any] = {
    "callId": "call_001",
    "segments": [
        {
            "speaker": "agent",
            "text": "Hello, how can I help?",
            "startTime": 0.0,
            "endTime": 2.5,
            "confidence": 0.98,
            "isFinal": True,
        },
        {
            "speaker": "caller",
            "text": "I need to check my order status.",
            "startTime": 3.0,
            "endTime": 5.5,
            "confidence": 0.95,
            "isFinal": True,
        },
    ],
}


class TestCallsList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CALL_LIST_RAW
        resource = CallsResource(mock_http)
        result = resource.list()

        mock_http.request.assert_called_once_with(
            "GET", "/voice/calls", query=None, options=None
        )
        assert isinstance(result["calls"][0], CallOutput)
        assert result["total"] == 1

    def test_list_with_filters(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CALL_LIST_RAW
        resource = CallsResource(mock_http)
        resource.list(agent_id="agent_001", direction="OUTBOUND", state="completed", limit=10)

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["agentId"] == "agent_001"
        assert query["direction"] == "OUTBOUND"
        assert query["state"] == "completed"
        assert query["limit"] == "10"

    def test_list_parses_call_output(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CALL_LIST_RAW
        resource = CallsResource(mock_http)
        result = resource.list()

        call = result["calls"][0]
        assert isinstance(call, CallOutput)
        assert call.id == "call_001"
        assert call.agent_id == "agent_001"
        assert call.direction.value == "OUTBOUND"
        assert call.tier.value == "basic"
        assert call.from_number == "+15550001234"
        assert call.duration_seconds == 175


class TestCallsGet:
    def test_get(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CALL_RAW
        resource = CallsResource(mock_http)
        result = resource.get("call_001")

        mock_http.request.assert_called_once_with(
            "GET", "/voice/calls/call_001", options=None
        )
        assert isinstance(result, CallOutput)
        assert result.id == "call_001"
        assert result.state == "completed"
        assert result.end_reason == "hangup"

    def test_get_parses_nullable_fields(self, mock_http: MagicMock) -> None:
        in_progress = {**CALL_RAW, "answeredAt": None, "endedAt": None, "endReason": None, "durationSeconds": None}
        mock_http.request.return_value = in_progress
        resource = CallsResource(mock_http)
        result = resource.get("call_001")

        assert result.answered_at is None
        assert result.ended_at is None
        assert result.end_reason is None
        assert result.duration_seconds is None


class TestCallsCreate:
    def test_create_minimal(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CREATE_CALL_RAW
        resource = CallsResource(mock_http)
        result = resource.create(to="+15559876543")

        call_body = mock_http.request.call_args[0][2]
        assert call_body["to"] == "+15559876543"
        assert "agentId" not in call_body
        assert isinstance(result, CreateCallOutput)
        assert result.call_id == "call_002"
        assert result.state == "initiated"

    def test_create_with_all_options(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CREATE_CALL_RAW
        resource = CallsResource(mock_http)
        resource.create(
            to="+15559876543",
            agent_id="agent_001",
            tier="premium",
            greeting="Hello!",
            from_number="+15550001234",
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["to"] == "+15559876543"
        assert call_body["agentId"] == "agent_001"
        assert call_body["tier"] == "premium"
        assert call_body["greeting"] == "Hello!"
        assert call_body["fromNumber"] == "+15550001234"

    def test_create_omits_none_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CREATE_CALL_RAW
        resource = CallsResource(mock_http)
        resource.create(to="+15559876543")

        call_body = mock_http.request.call_args[0][2]
        assert "agentId" not in call_body
        assert "tier" not in call_body
        assert "greeting" not in call_body
        assert "fromNumber" not in call_body


class TestCallsGetTranscript:
    def test_get_transcript(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = TRANSCRIPT_RAW
        resource = CallsResource(mock_http)
        result = resource.get_transcript("call_001")

        mock_http.request.assert_called_once_with(
            "GET", "/voice/calls/call_001/transcript", options=None
        )
        assert isinstance(result, CallTranscript)
        assert result.call_id == "call_001"
        assert len(result.segments) == 2

    def test_transcript_segments_parsed(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = TRANSCRIPT_RAW
        resource = CallsResource(mock_http)
        result = resource.get_transcript("call_001")

        seg = result.segments[0]
        assert seg.speaker == "agent"
        assert seg.text == "Hello, how can I help?"
        assert seg.start_time == 0.0
        assert seg.end_time == 2.5
        assert seg.confidence == 0.98
        assert seg.is_final is True
