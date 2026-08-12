"""Tests for webhook signature verification and event construction.

These exist because the previous ones passed while the code could not process a
single real delivery.

The old fixture built a Stripe-style ``t=<unix>,v1=<hex>`` header and a
``{"type": ..., "data": {...}}`` payload — both invented to match the
implementation. Nothing compared either against what the platform sends, so the
suite agreed with the bug and stayed green.

So ``_sign`` below is written from the platform's published scheme rather than
from this SDK's parser, and the payload is the real ``message.received`` shape.
Sources, all of which agree with each other:

  - apps/api/src/services/webhook-signature.ts — buildWebhookSignatureHeaders
  - apps/api/src/workers/inbound-email.ts      — the emitted payload
  - docs.useanima.sh/webhooks                  — the customer-facing contract

``TestPreFixSchemeRejected`` at the bottom holds the regression guards: if
someone reintroduces the old header or the old envelope, those fail.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from anima._exceptions import ValidationError
from anima._types import (
    WebhookAuthBasic,
    WebhookAuthBearer,
    WebhookAuthCustomHeader,
    WebhookAuthNone,
    WebhookEvent,
    WebhookEventType,
    WebhookOutput,
)
from anima._webhooks import construct_webhook_event, verify_webhook_signature
from anima.resources.webhooks import WebhooksResource, _serialize_auth_config

SECRET = "whsec_test_secret_123"
SIGNED_AT = "2026-07-28T12:00:00.000Z"
SIGNED_AT_MS = datetime(2026, 7, 28, 12, 0, 0, tzinfo=timezone.utc).timestamp() * 1000

#: A real ``message.received`` delivery: flat, no ``data`` envelope.
PAYLOAD = json.dumps(
    {
        "event": "message.received",
        "occurredAt": SIGNED_AT,
        "messageId": "cme9x2k1p0001s601abcdefgh",
        "agentId": "cme9x2k1p0000s601ijklmnop",
        "channel": "email",
        "direction": "INBOUND",
        "fromAddress": "user@example.com",
        "toAddress": "support-agent@agents.useanima.sh",
        "threadId": "cme9x2k1p0002s601qrstuvwx",
        "subject": "Hello",
        "spam": False,
    }
)


def _sign(body: str, timestamp: str = SIGNED_AT, secret: str = SECRET) -> str:
    """Reproduce the platform's signer: HMAC-SHA256 over ``{iso}.{body}``, hex."""
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.{body}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"v1={digest}"


class TestVerifyWebhookSignature:
    def test_accepts_a_genuine_delivery(self) -> None:
        assert (
            verify_webhook_signature(PAYLOAD, _sign(PAYLOAD), SIGNED_AT, SECRET, now=SIGNED_AT_MS)
            is True
        )

    def test_accepts_a_bare_hex_digest(self) -> None:
        bare = _sign(PAYLOAD).removeprefix("v1=")
        assert verify_webhook_signature(PAYLOAD, bare, SIGNED_AT, SECRET, now=SIGNED_AT_MS) is True

    def test_accepts_a_bytes_body(self) -> None:
        assert (
            verify_webhook_signature(
                PAYLOAD.encode("utf-8"), _sign(PAYLOAD), SIGNED_AT, SECRET, now=SIGNED_AT_MS
            )
            is True
        )

    def test_rejects_a_tampered_body(self) -> None:
        tampered = PAYLOAD.replace("user@example.com", "attacker@evil.com")
        assert (
            verify_webhook_signature(tampered, _sign(PAYLOAD), SIGNED_AT, SECRET, now=SIGNED_AT_MS)
            is False
        )

    def test_rejects_the_wrong_secret(self) -> None:
        assert (
            verify_webhook_signature(
                PAYLOAD, _sign(PAYLOAD), SIGNED_AT, "whsec_other", now=SIGNED_AT_MS
            )
            is False
        )

    def test_rejects_outside_the_freshness_window(self) -> None:
        assert (
            verify_webhook_signature(
                PAYLOAD,
                _sign(PAYLOAD),
                SIGNED_AT,
                SECRET,
                tolerance_seconds=300,
                now=SIGNED_AT_MS + 301_000,
            )
            is False
        )

    def test_rejects_a_replay_whose_timestamp_was_edited(self) -> None:
        # The captured signature is valid only for the timestamp it signed, so
        # moving the clock forward breaks the MAC, not just the freshness check.
        replayed_at = "2026-07-28T13:00:00.000Z"
        assert (
            verify_webhook_signature(
                PAYLOAD,
                _sign(PAYLOAD),
                replayed_at,
                SECRET,
                now=SIGNED_AT_MS + 3_600_000,
            )
            is False
        )

    def test_rejects_an_unparseable_timestamp(self) -> None:
        assert (
            verify_webhook_signature(
                PAYLOAD, _sign(PAYLOAD, "not-a-date"), "not-a-date", SECRET, now=SIGNED_AT_MS
            )
            is False
        )

    def test_rejects_a_non_hex_signature(self) -> None:
        assert (
            verify_webhook_signature(PAYLOAD, "v1=not-hex", SIGNED_AT, SECRET, now=SIGNED_AT_MS)
            is False
        )


class TestConstructWebhookEvent:
    def test_returns_the_delivery_flat(self) -> None:
        event = construct_webhook_event(
            PAYLOAD, _sign(PAYLOAD), SIGNED_AT, SECRET, now=SIGNED_AT_MS
        )

        assert isinstance(event, WebhookEvent)
        assert event.event == WebhookEventType.MESSAGE_RECEIVED
        assert event.occurred_at == SIGNED_AT
        # Event-specific fields keep their wire names, alongside `event`.
        assert event.model_extra is not None
        assert event.model_extra["messageId"] == "cme9x2k1p0001s601abcdefgh"
        assert event.model_extra["channel"] == "email"
        assert event.model_extra["spam"] is False
        assert "data" not in event.model_extra

    def test_an_unknown_event_name_parses_as_a_string(self) -> None:
        # A new event on the platform must not break a deployed consumer.
        body = json.dumps({"event": "widget.exploded", "occurredAt": SIGNED_AT})
        event = construct_webhook_event(body, _sign(body), SIGNED_AT, SECRET, now=SIGNED_AT_MS)
        assert event.event == "widget.exploded"

    def test_raises_on_an_invalid_signature(self) -> None:
        with pytest.raises(ValidationError, match="Invalid webhook signature"):
            construct_webhook_event(PAYLOAD, "v1=deadbeef", SIGNED_AT, SECRET, now=SIGNED_AT_MS)

    def test_raises_when_the_event_name_is_missing(self) -> None:
        body = json.dumps({"occurredAt": SIGNED_AT})
        with pytest.raises(ValidationError, match="missing event name"):
            construct_webhook_event(body, _sign(body), SIGNED_AT, SECRET, now=SIGNED_AT_MS)

    def test_raises_when_occurred_at_is_missing(self) -> None:
        body = json.dumps({"event": "message.sent"})
        with pytest.raises(ValidationError, match="missing occurredAt"):
            construct_webhook_event(body, _sign(body), SIGNED_AT, SECRET, now=SIGNED_AT_MS)

    def test_raises_on_a_non_dict_payload(self) -> None:
        body = json.dumps([1, 2, 3])
        with pytest.raises(ValidationError, match="Invalid webhook payload format"):
            construct_webhook_event(body, _sign(body), SIGNED_AT, SECRET, now=SIGNED_AT_MS)


class TestPreFixSchemeRejected:
    """Regression guards. These fail if the old scheme is reintroduced."""

    def test_rejects_the_pre_fix_combined_signature_header(self) -> None:
        # What this SDK used to expect. The platform has never sent it: the
        # timestamp travels in X-Anima-Timestamp and the signature header holds
        # only `v1=<hex>`.
        unix = int(SIGNED_AT_MS // 1000)
        digest = hmac.new(
            SECRET.encode("utf-8"),
            f"{unix}.{PAYLOAD}".encode(),
            hashlib.sha256,
        ).hexdigest()

        assert (
            verify_webhook_signature(
                PAYLOAD, f"t={unix},v1={digest}", SIGNED_AT, SECRET, now=SIGNED_AT_MS
            )
            is False
        )

    def test_rejects_the_pre_fix_type_data_envelope(self) -> None:
        # A correctly signed body in the old envelope shape still has no
        # `event`, so it cannot be mistaken for a delivery.
        body = json.dumps(
            {
                "id": "evt_1",
                "type": "message.sent",
                "createdAt": SIGNED_AT,
                "data": {"messageId": "m1"},
            }
        )
        with pytest.raises(ValidationError, match="missing event name"):
            construct_webhook_event(body, _sign(body), SIGNED_AT, SECRET, now=SIGNED_AT_MS)


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
