"""Tests for webhook signature verification and event construction."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from anima._exceptions import ValidationError
from anima._types import WebhookEvent
from anima._webhooks import (
    _parse_signature_header,
    construct_webhook_event,
    verify_webhook_signature,
)


SECRET = "whsec_test_secret_123"


def _sign(payload: str, timestamp: int) -> str:
    """Create a valid signature header for testing."""
    signed_payload = f"{timestamp}.{payload}"
    sig = hmac.new(
        SECRET.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={sig}"


class TestParseSignatureHeader:
    def test_valid_header(self) -> None:
        ts, sig = _parse_signature_header("t=1234567890,v1=abcdef0123456789")
        assert ts == 1234567890
        assert sig == "abcdef0123456789"

    def test_missing_timestamp(self) -> None:
        with pytest.raises(ValidationError, match="Invalid webhook signature header"):
            _parse_signature_header("v1=abcdef")

    def test_missing_signature(self) -> None:
        with pytest.raises(ValidationError, match="Invalid webhook signature header"):
            _parse_signature_header("t=1234567890")

    def test_empty_header(self) -> None:
        with pytest.raises(ValidationError):
            _parse_signature_header("")

    def test_extra_fields_ignored(self) -> None:
        ts, sig = _parse_signature_header("t=123,v1=abc,v2=xyz,extra=yes")
        assert ts == 123
        assert sig == "abc"


class TestVerifyWebhookSignature:
    def test_valid_signature(self) -> None:
        payload = '{"type":"agent.created","data":{"id":"agent_001"}}'
        ts = int(time.time())
        header = _sign(payload, ts)
        # Use now= to set the "current" time in ms
        now_ms = ts * 1000.0
        assert verify_webhook_signature(payload, header, SECRET, now=now_ms) is True

    def test_valid_signature_bytes_payload(self) -> None:
        payload = '{"type":"agent.created","data":{"id":"agent_001"}}'
        ts = int(time.time())
        header = _sign(payload, ts)
        now_ms = ts * 1000.0
        assert verify_webhook_signature(
            payload.encode("utf-8"), header, SECRET, now=now_ms
        ) is True

    def test_invalid_signature(self) -> None:
        payload = '{"type":"agent.created","data":{"id":"agent_001"}}'
        ts = int(time.time())
        header = f"t={ts},v1=00000000000000000000000000000000"
        now_ms = ts * 1000.0
        assert verify_webhook_signature(payload, header, SECRET, now=now_ms) is False

    def test_expired_timestamp(self) -> None:
        payload = '{"type":"agent.created","data":{"id":"agent_001"}}'
        ts = int(time.time()) - 600  # 10 minutes ago
        header = _sign(payload, ts)
        now_ms = int(time.time()) * 1000.0
        assert verify_webhook_signature(
            payload, header, SECRET, tolerance_seconds=300, now=now_ms
        ) is False

    def test_wrong_secret(self) -> None:
        payload = '{"type":"agent.created","data":{"id":"agent_001"}}'
        ts = int(time.time())
        header = _sign(payload, ts)
        now_ms = ts * 1000.0
        assert verify_webhook_signature(
            payload, header, "wrong_secret", now=now_ms
        ) is False

    def test_tampered_payload(self) -> None:
        payload = '{"type":"agent.created","data":{"id":"agent_001"}}'
        ts = int(time.time())
        header = _sign(payload, ts)
        tampered = '{"type":"agent.created","data":{"id":"agent_002"}}'
        now_ms = ts * 1000.0
        assert verify_webhook_signature(tampered, header, SECRET, now=now_ms) is False


class TestConstructWebhookEvent:
    def _make_signed_event(
        self, event_type: str = "agent.created", data: dict | None = None
    ) -> tuple[str, str, float]:
        """Return (payload_str, signature_header, now_ms)."""
        if data is None:
            data = {"id": "agent_001"}
        payload = json.dumps(
            {
                "id": "evt_001",
                "type": event_type,
                "createdAt": "2025-01-01T00:00:00Z",
                "data": data,
            }
        )
        ts = int(time.time())
        header = _sign(payload, ts)
        return payload, header, ts * 1000.0

    def test_valid_event(self) -> None:
        payload, header, now_ms = self._make_signed_event()
        event = construct_webhook_event(payload, header, SECRET, now=now_ms)

        assert isinstance(event, WebhookEvent)
        assert event.type.value == "agent.created"
        assert event.data == {"id": "agent_001"}
        assert event.id == "evt_001"
        assert event.created_at == "2025-01-01T00:00:00Z"

    def test_invalid_signature_raises(self) -> None:
        payload = json.dumps({"type": "agent.created", "data": {"id": "1"}})
        header = "t=0,v1=0000000000000000000000000000000000000000000000000000000000000000"
        with pytest.raises(ValidationError, match="Invalid webhook signature"):
            construct_webhook_event(payload, header, SECRET, now=0.0)

    def test_missing_type_raises(self) -> None:
        payload_dict = {"data": {"id": "1"}}
        payload = json.dumps(payload_dict)
        ts = int(time.time())
        header = _sign(payload, ts)
        with pytest.raises(ValidationError, match="missing event type"):
            construct_webhook_event(payload, header, SECRET, now=ts * 1000.0)

    def test_missing_data_raises(self) -> None:
        payload_dict = {"type": "agent.created"}
        payload = json.dumps(payload_dict)
        ts = int(time.time())
        header = _sign(payload, ts)
        with pytest.raises(ValidationError, match="missing data"):
            construct_webhook_event(payload, header, SECRET, now=ts * 1000.0)

    def test_non_dict_payload_raises(self) -> None:
        payload = json.dumps([1, 2, 3])
        ts = int(time.time())
        header = _sign(payload, ts)
        with pytest.raises(ValidationError, match="Invalid webhook payload format"):
            construct_webhook_event(payload, header, SECRET, now=ts * 1000.0)
