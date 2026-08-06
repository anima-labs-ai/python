"""Tests for CallsResource with mocked HTTP."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from anima._types import CallOutput, CallTranscript, CreateCallOutput
from anima._voice_connection import VoiceConnection
from anima.resources.calls import CallsResource

# ---------------------------------------------------------------------------
# Raw API response fixtures
# ---------------------------------------------------------------------------

CALL_RAW: dict[str, Any] = {
    "id": "call_001",
    "agentId": "agent_001",
    "phoneIdentityId": "phi_001",
    "direction": "OUTBOUND",
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

        mock_http.request.assert_called_once_with("GET", "/voice/calls", query=None, options=None)
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
        assert call.from_number == "+15550001234"
        assert call.duration_seconds == 175


class TestCallsGet:
    def test_get(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CALL_RAW
        resource = CallsResource(mock_http)
        result = resource.get("call_001")

        mock_http.request.assert_called_once_with("GET", "/voice/calls/call_001", options=None)
        assert isinstance(result, CallOutput)
        assert result.id == "call_001"
        assert result.state == "completed"
        assert result.end_reason == "hangup"

    def test_get_parses_nullable_fields(self, mock_http: MagicMock) -> None:
        in_progress = {
            **CALL_RAW,
            "answeredAt": None,
            "endedAt": None,
            "endReason": None,
            "durationSeconds": None,
        }
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
            greeting="Hello!",
            from_number="+15550001234",
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["to"] == "+15559876543"
        assert call_body["agentId"] == "agent_001"
        assert call_body["greeting"] == "Hello!"
        assert call_body["fromNumber"] == "+15550001234"

    def test_create_omits_none_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CREATE_CALL_RAW
        resource = CallsResource(mock_http)
        resource.create(to="+15559876543")

        call_body = mock_http.request.call_args[0][2]
        assert "agentId" not in call_body
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


class TestVoiceConnectionUnknownFrames:
    """The live-call WebSocket must never crash on an unrecognized frame.

    ``/ws/voice`` emits speculative frames such as ``call.transcription.eager``
    (a pre-final Flux end-of-turn hint, sent so harnesses can pre-warm their
    LLM) ahead of the authoritative ``call.transcription`` with ``isFinal``.
    ``VoiceConnection`` is a transparent forwarder: it hands every frame to the
    ``on_message`` handlers untouched and never dispatches on ``type``, so an
    unknown/eager frame is delivered as-is and can never raise. These tests lock
    that forward-compat guarantee — the receive path must not regress into a
    type switch that drops or fails on frames it does not recognize.
    """

    def _connection(self) -> VoiceConnection:
        """Build a VoiceConnection without opening a socket or starting a thread."""
        pytest.importorskip("websocket")  # VoiceConnection.__init__ requires it
        with patch.object(VoiceConnection, "_connect", lambda self: None):
            return VoiceConnection("wss://api.useanima.sh/v1/ws/voice?token=sk-test")

    def test_eager_transcription_frame_is_forwarded_not_raised(self) -> None:
        conn = self._connection()
        received: list[dict[str, Any]] = []
        conn.on_message(received.append)

        eager = {
            "type": "call.transcription.eager",
            "callId": "call_001",
            "turnId": "turn_007",
            "text": "I need to check my",
            "confidence": 0.9,
            "timestamp": 1234567890,
        }
        # Simulate the frame arriving off the socket. It must not raise, and is
        # forwarded verbatim — the SDK does not interpret it as a turn; callers
        # key on the later isFinal=True call.transcription for the real turn.
        conn._on_message(None, json.dumps(eager))

        assert received == [eager]

    def test_unknown_frame_type_is_ignored_gracefully(self) -> None:
        conn = self._connection()
        received: list[dict[str, Any]] = []
        conn.on_message(received.append)

        # A frame type the SDK has never seen must not crash the receive path,
        # and a normal frame after it must still be delivered.
        conn._on_message(None, json.dumps({"type": "call.some.future.frame", "x": 1}))
        conn._on_message(
            None,
            json.dumps({"type": "call.transcription", "text": "done", "isFinal": True}),
        )

        assert [m["type"] for m in received] == [
            "call.some.future.frame",
            "call.transcription",
        ]


def wire_fields(model: type[BaseModel]) -> set[str]:
    """The JSON names a model serializes — its alias where it has one."""
    return {info.alias or name for name, info in model.model_fields.items()}


class TestFixturesMatchTheContract:
    """The fixtures AND the models must be what the API sends.

    `tier` survived in `CallOutput` and `CreateCallOutput` as a REQUIRED field
    the API has never returned, and every test here passed the whole time —
    because `CALL_RAW` was written to satisfy the model rather than to mirror
    the contract. A fixture derived from the type it feeds cannot fail. Once the
    fixtures told the truth, eight tests broke at once with
    `ValidationError: tier Field required`, which is what a Python caller got on
    every `calls.list()`, `calls.get()` and `calls.create()`.

    The field lists are spelled out on purpose, from
    `packages/contracts/src/schemas/voice.ts`. Deriving the EXPECTED list from
    the models is what would rebuild the circle; checking the models AGAINST a
    spelled-out list is the opposite, and is what the node and Go SDKs do
    (`Equals<keyof Call, ...>` and a reflect-over-json-tags check). Without the
    model half, only a REQUIRED phantom field is caught — the fixture stops
    parsing. An OPTIONAL one the API never sends would sit there indefinitely:
    fixture unchanged, every test green, callers reading `None` and believing
    it means the API said nothing.
    """

    LIVE_CALL_FIELDS = {
        "id",
        "agentId",
        "phoneIdentityId",
        "direction",
        "state",
        "from",
        "to",
        "startedAt",
        "answeredAt",
        "endedAt",
        "endReason",
        "durationSeconds",
        "createdAt",
    }

    LIVE_CREATE_CALL_FIELDS = {"callId", "state", "from", "to", "direction"}

    def test_call_fixture_is_the_contract_shape(self) -> None:
        assert set(CALL_RAW) == self.LIVE_CALL_FIELDS

    def test_create_call_fixture_is_the_contract_shape(self) -> None:
        assert set(CREATE_CALL_RAW) == self.LIVE_CREATE_CALL_FIELDS

    def test_call_model_is_the_contract_shape(self) -> None:
        assert wire_fields(CallOutput) == self.LIVE_CALL_FIELDS

    def test_create_call_model_is_the_contract_shape(self) -> None:
        assert wire_fields(CreateCallOutput) == self.LIVE_CREATE_CALL_FIELDS
