from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

from ._exceptions import ValidationError
from ._types import WebhookEvent

DEFAULT_TOLERANCE_SECONDS = 300


def _parse_signature_header(header: str) -> tuple[int, str]:
    timestamp: int | None = None
    signature: str | None = None

    for piece in header.split(","):
        piece = piece.strip()
        parts = piece.split("=", 1)
        if len(parts) != 2:
            continue
        key, value = parts
        if key == "t":
            timestamp = int(value)
        elif key == "v1":
            signature = value

    if timestamp is None or signature is None:
        raise ValidationError("Invalid webhook signature header format")

    return timestamp, signature


def _to_payload_string(payload: str | bytes) -> str:
    if isinstance(payload, bytes):
        return payload.decode("utf-8")
    return payload


def verify_webhook_signature(
    payload: str | bytes,
    signature_header: str,
    secret: str,
    tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
    now: float | None = None,
) -> bool:
    ts, sig = _parse_signature_header(signature_header)
    current = now if now is not None else time.time() * 1000

    age_seconds = abs(current - ts * 1000) / 1000
    if age_seconds > tolerance_seconds:
        return False

    payload_str = _to_payload_string(payload)
    signed_payload = f"{ts}.{payload_str}"

    expected = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        bytes.fromhex(expected),
        bytes.fromhex(sig),
    )


def construct_webhook_event(
    payload: str | bytes,
    signature_header: str,
    secret: str,
    tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
    now: float | None = None,
) -> WebhookEvent:
    if not verify_webhook_signature(
        payload, signature_header, secret, tolerance_seconds, now
    ):
        raise ValidationError("Invalid webhook signature")

    payload_str = _to_payload_string(payload)
    parsed: Any = json.loads(payload_str)

    if not isinstance(parsed, dict):
        raise ValidationError("Invalid webhook payload format")

    if not isinstance(parsed.get("type"), str):
        raise ValidationError("Webhook payload missing event type")

    data = parsed.get("data")
    if not isinstance(data, dict):
        raise ValidationError("Webhook payload missing data object")

    event_data: dict[str, Any] = {
        "type": parsed["type"],
        "data": data,
    }

    if isinstance(parsed.get("id"), str):
        event_data["id"] = parsed["id"]
    if isinstance(parsed.get("createdAt"), str):
        event_data["createdAt"] = parsed["createdAt"]

    return WebhookEvent.model_validate(event_data)
