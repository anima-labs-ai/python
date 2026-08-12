"""Cross-repo conformance: does this SDK verify what the platform actually signs?

``test_webhooks.py`` reproduces the platform's signing scheme by hand, which is
an improvement on what came before but still a copy — and a copy can drift back.
This one runs the monorepo's *own* signer and feeds its output to the SDK, so
the two cannot disagree without something here going red.

That is the check that was missing. This SDK shipped a Stripe-style
``t=<unix>,v1=<hex>`` header and a ``{"type": ..., "data": {...}}`` envelope;
the platform has always sent ``X-Anima-Signature: v1=<hex>`` with a separate
ISO-8601 ``X-Anima-Timestamp``, over a flat payload. Both sides had passing
tests. Only something spanning them could have caught it.

``webhook-signature.ts`` is a pure module — no database, no server boot — so
this needs only the monorepo on disk and a JS runtime to execute it.

Skips when either is absent, which is the case in CI. Deliberately loud about
it: a silent skip here would restore the exact blind spot.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from anima._webhooks import construct_webhook_event, verify_webhook_signature

SECRET = "whsec_conformance"
TIMESTAMP = "2026-07-28T12:00:00.000Z"
TIMESTAMP_MS = datetime(2026, 7, 28, 12, 0, 0, tzinfo=timezone.utc).timestamp() * 1000

BODY = json.dumps(
    {
        "event": "message.received",
        "occurredAt": TIMESTAMP,
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

#: The SDK ships as its own repo but in dev sits next to the monorepo.
_DEFAULT_SIGNER = (
    Path(__file__).resolve().parents[2] / "anima/apps/api/src/services/webhook-signature.ts"
)
SIGNER_PATH = Path(os.environ.get("ANIMA_WEBHOOK_SIGNER_PATH", _DEFAULT_SIGNER))
RUNTIME = shutil.which("bun")


def _skip_reason() -> str | None:
    if RUNTIME is None:
        return "no `bun` on PATH to execute the monorepo's TypeScript signer"
    if not SIGNER_PATH.exists():
        return f"monorepo signer not found at {SIGNER_PATH}"
    return None


SKIP = _skip_reason()

if SKIP:
    print(
        f"\n[webhook conformance] SKIPPED — {SKIP}. This is the only cross-repo check "
        "that the SDK verifies what the platform signs. Set ANIMA_WEBHOOK_SIGNER_PATH "
        "to run it."
    )


def _platform_headers() -> dict[str, str]:
    """Run the monorepo's buildWebhookSignatureHeaders and return its output."""
    script = (
        f"const m = await import({str(SIGNER_PATH)!r});"
        f"console.log(JSON.stringify("
        f"m.buildWebhookSignatureHeaders({SECRET!r}, {BODY!r}, {TIMESTAMP!r})));"
    )
    completed = subprocess.run(
        [RUNTIME, "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    return json.loads(completed.stdout.strip())


@pytest.mark.skipif(SKIP is not None, reason=SKIP or "")
class TestConformanceWithPlatformSigner:
    def test_the_sdk_verifies_headers_the_platform_produced(self) -> None:
        headers = _platform_headers()

        assert (
            verify_webhook_signature(
                BODY,
                headers["X-Anima-Signature"],
                headers["X-Anima-Timestamp"],
                SECRET,
                now=TIMESTAMP_MS,
            )
            is True
        )

    def test_the_platform_emits_exactly_the_two_headers_the_sdk_reads(self) -> None:
        headers = _platform_headers()

        assert sorted(headers) == ["X-Anima-Signature", "X-Anima-Timestamp"]
        assert headers["X-Anima-Signature"].startswith("v1=")
        assert len(headers["X-Anima-Signature"]) == len("v1=") + 64
        assert headers["X-Anima-Timestamp"] == TIMESTAMP

    def test_construct_parses_a_platform_signed_delivery(self) -> None:
        headers = _platform_headers()

        event = construct_webhook_event(
            BODY,
            headers["X-Anima-Signature"],
            headers["X-Anima-Timestamp"],
            SECRET,
            now=TIMESTAMP_MS,
        )

        assert event.event == "message.received"
        assert event.model_extra is not None
        assert event.model_extra["messageId"] == "cme9x2k1p0001s601abcdefgh"
        assert "data" not in event.model_extra
