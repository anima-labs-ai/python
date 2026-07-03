"""Tests for webhook signature verification and event construction."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from unittest.mock import MagicMock

import pytest

from anima._exceptions import ValidationError
from anima._types import (
    WebhookAuthBasic,
    WebhookAuthBearer,
    WebhookAuthCustomHeader,
    WebhookAuthNone,
    WebhookEvent,
    WebhookOutput,
)
from anima._webhooks import (
    _parse_signature_header,
    construct_webhook_event,
    verify_webhook_signature,
)
from anima.resources.webhooks import WebhooksResource, _serialize_auth_config

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
        assert verify_webhook_signature(payload.encode("utf-8"), header, SECRET, now=now_ms) is True

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
        assert (
            verify_webhook_signature(payload, header, SECRET, tolerance_seconds=300, now=now_ms)
            is False
        )

    def test_wrong_secret(self) -> None:
        payload = '{"type":"agent.created","data":{"id":"agent_001"}}'
        ts = int(time.time())
        header = _sign(payload, ts)
        now_ms = ts * 1000.0
        assert verify_webhook_signature(payload, header, "wrong_secret", now=now_ms) is False

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


WEBHOOK_RAW: dict = {
    "id": "wh_001",
    "orgId": "org_001",
    "url": "https://example.com/hook",
    "events": ["message.received"],
    "active": True,
    "description": None,
    "consecutiveFailures": 0,
    "disabledReason": None,
    "disabledAt": None,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
    "authType": "BEARER",
    "authHeaderName": None,
    "rateLimitPerMinute": 120,
    "maxAttempts": 5,
}


class TestWebhookAuthConfigSerialization:
    """The auth config's wire keys must match the API exactly."""

    def test_none(self) -> None:
        assert _serialize_auth_config(WebhookAuthNone()) == {"type": "none"}

    def test_bearer(self) -> None:
        assert _serialize_auth_config(WebhookAuthBearer(token="tok")) == {
            "type": "bearer",
            "token": "tok",
        }

    def test_basic(self) -> None:
        assert _serialize_auth_config(WebhookAuthBasic(username="u", password="p")) == {
            "type": "basic",
            "username": "u",
            "password": "p",
        }

    def test_custom_header_serializes_camelcase_wire_key(self) -> None:
        # header_name (Python snake_case) must reach the wire as headerName.
        assert _serialize_auth_config(WebhookAuthCustomHeader(header_name="X-Key", value="v")) == {
            "type": "custom_header",
            "headerName": "X-Key",
            "value": "v",
        }


class TestWebhooksCreateAdvanced:
    def test_create_sends_auth_and_throttle(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = WEBHOOK_RAW
        WebhooksResource(mock_http).create(
            url="https://example.com/hook",
            events=["message.received"],
            auth_config=WebhookAuthBearer(token="tok"),
            rate_limit_per_minute=120,
            max_attempts=5,
        )
        body = mock_http.request.call_args[0][2]
        assert body["authConfig"] == {"type": "bearer", "token": "tok"}
        assert body["rateLimitPerMinute"] == 120
        assert body["maxAttempts"] == 5

    def test_create_omits_advanced_when_unset(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = WEBHOOK_RAW
        WebhooksResource(mock_http).create(
            url="https://example.com/hook", events=["message.received"]
        )
        body = mock_http.request.call_args[0][2]
        assert "authConfig" not in body
        assert "rateLimitPerMinute" not in body
        assert "maxAttempts" not in body


class TestWebhooksUpdateAdvanced:
    def test_update_can_clear_auth_with_none(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = WEBHOOK_RAW
        WebhooksResource(mock_http).update("wh_001", auth_config=WebhookAuthNone(), max_attempts=3)
        body = mock_http.request.call_args[0][2]
        assert body["id"] == "wh_001"
        assert body["authConfig"] == {"type": "none"}
        assert body["maxAttempts"] == 3


class TestWebhookOutputAdvancedFields:
    def test_parses_auth_and_throttle(self) -> None:
        wh = WebhookOutput.model_validate(WEBHOOK_RAW)
        assert wh.auth_type == "BEARER"
        assert wh.auth_header_name is None
        assert wh.rate_limit_per_minute == 120
        assert wh.max_attempts == 5

    def test_defaults_when_server_omits_advanced_fields(self) -> None:
        raw = {
            k: v
            for k, v in WEBHOOK_RAW.items()
            if k not in {"authType", "authHeaderName", "rateLimitPerMinute", "maxAttempts"}
        }
        wh = WebhookOutput.model_validate(raw)
        assert wh.auth_type == "NONE"
        assert wh.auth_header_name is None
        assert wh.rate_limit_per_minute is None
        assert wh.max_attempts is None
