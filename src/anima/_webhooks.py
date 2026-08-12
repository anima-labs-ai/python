"""Webhook verification, matching what the platform actually sends.

Scheme ``v1``: HMAC-SHA256, hex-encoded, over ``f"{timestamp}.{raw_body}"``,
where ``timestamp`` is the ISO-8601 string from ``X-Anima-Timestamp``. Two
headers travel with every delivery::

    X-Anima-Signature:  v1=<hex>
    X-Anima-Timestamp:  <ISO-8601>

The timestamp is inside the signed content rather than merely alongside it,
which is what makes replay rejection possible: a captured delivery fails the
freshness window, and editing the timestamp to get past it invalidates the MAC.

This module previously implemented a Stripe-style single header
(``t=<unix>,v1=<hex>``) and MAC'd over a unix-seconds timestamp, then required a
``{"type": ..., "data": {...}}`` envelope. Nothing the platform sends has ever
matched either, so both public functions raised on every real delivery. The
tests did not catch it because they built their own fixture from the same wrong
assumptions. See ``tests/test_webhooks.py``, which now derives its fixture from
the platform's published scheme, and ``tests/test_webhook_conformance.py``,
which checks this SDK against the monorepo's own signer.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from typing import Any

from ._exceptions import ValidationError
from ._types import WebhookEvent

DEFAULT_TOLERANCE_SECONDS = 300
_SIGNATURE_VERSION = "v1"


def _to_payload_string(payload: str | bytes) -> str:
    if isinstance(payload, bytes):
        return payload.decode("utf-8")
    return payload


def _digest_from_header(signature: str) -> str:
    """Strip the ``v1=`` prefix. A bare hex digest passes through unchanged."""
    prefix = f"{_SIGNATURE_VERSION}="
    return signature[len(prefix) :] if signature.startswith(prefix) else signature


def _parse_iso_ms(timestamp: str) -> float | None:
    """Milliseconds since the epoch for an ISO-8601 string, or None if unparseable."""
    try:
        # Python < 3.11 does not accept a trailing "Z" in fromisoformat.
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp() * 1000


def _compute_signature(secret: str, timestamp: str, body: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.{body}".encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_webhook_signature(
    payload: str | bytes,
    signature: str,
    timestamp: str,
    secret: str,
    tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
    now: float | None = None,
) -> bool:
    """Verify a delivery's signature and freshness.

    Args:
        payload: The **raw** request body. Verifying a re-serialised body fails
            even for a genuine delivery — re-encoding can reorder keys or change
            whitespace, and the MAC covers bytes.
        signature: The ``X-Anima-Signature`` header, ``v1=<hex>``.
        timestamp: The ``X-Anima-Timestamp`` header, ISO-8601.
        secret: The webhook's signing secret.
        tolerance_seconds: Freshness window. Defaults to 300.
        now: Current time in **milliseconds** since the epoch, for tests.
    """
    signed_at = _parse_iso_ms(timestamp)
    if signed_at is None:
        return False

    current = now if now is not None else time.time() * 1000
    if abs(current - signed_at) > tolerance_seconds * 1000:
        return False

    expected = _compute_signature(secret, timestamp, _to_payload_string(payload))

    try:
        provided_bytes = bytes.fromhex(_digest_from_header(signature))
    except ValueError:
        return False

    return hmac.compare_digest(bytes.fromhex(expected), provided_bytes)


def construct_webhook_event(
    payload: str | bytes,
    signature: str,
    timestamp: str,
    secret: str,
    tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
    now: float | None = None,
) -> WebhookEvent:
    """Verify a delivery and parse it.

    The payload is flat, so the returned model *is* the delivery: ``event`` and
    ``occurred_at`` alongside that event's own fields.

    Raises:
        ValidationError: If the signature does not verify, or the body is not a
            webhook payload.
    """
    if not verify_webhook_signature(payload, signature, timestamp, secret, tolerance_seconds, now):
        raise ValidationError("Invalid webhook signature")

    parsed: Any = json.loads(_to_payload_string(payload))

    if not isinstance(parsed, dict):
        raise ValidationError("Invalid webhook payload format")

    if not isinstance(parsed.get("event"), str):
        raise ValidationError("Webhook payload missing event name")

    if not isinstance(parsed.get("occurredAt"), str):
        raise ValidationError("Webhook payload missing occurredAt")

    return WebhookEvent.model_validate(parsed)
