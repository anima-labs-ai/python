"""Every path this SDK can call must exist on the API.

The per-resource tests assert paths against a mock, so they pass whether or
not the server serves the route. That is how ``POST /security/scan`` and
``GET /identity/did/{did}`` stayed green for the whole life of those methods,
and how two entire resources (wallet, pods) shipped against products the API
had removed. Twenty-nine of this SDK's calls went nowhere.

This test reads the resource sources and checks each path literal against the
allowlist below, generated from the monorepo's
``packages/contracts/src/contracts/*.ts`` at the commit in ``.anima-ref``. A
new method reaching for a route that does not exist fails here.

Regenerate when ``.anima-ref`` moves::

    grep -rhoE 'method: "[A-Z]+", path: "[^"]+"' \
      packages/contracts/src/contracts/*.ts |
      sed -E 's/method: "([A-Z]+)", path: "([^"]+)"/\1 \2/' | sort -u

plus the three routes registered directly on fastify rather than through
oRPC, which that grep does not see: ``GET /audit/events``,
``GET /events/stream``, ``POST /a2a/inbound``.
"""

from __future__ import annotations

import re
from pathlib import Path

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "src" / "anima" / "resources"

#: ``METHOD /path`` for every route the API serves, path params as ``*``.
API_ROUTES: frozenset[str] = frozenset(
    [
        "POST /a2a/inbound",
        "GET /addresses",
        "POST /addresses",
        "DELETE /addresses/*",
        "GET /addresses/*",
        "PUT /addresses/*",
        "POST /addresses/*/validate",
        "POST /agent/elevate",
        "POST /agent/elevate/request",
        "POST /agent/sign-up",
        "GET /agent/status",
        "POST /agent/verify",
        "GET /agents",
        "POST /agents",
        "DELETE /agents/*",
        "GET /agents/*",
        "PATCH /agents/*",
        "POST /agents/*/a2a/dispatch",
        "GET /agents/*/a2a/tasks",
        "POST /agents/*/a2a/tasks",
        "GET /agents/*/a2a/tasks/*",
        "POST /agents/*/a2a/tasks/*/cancel",
        "POST /agents/*/a2a/tasks/*/update",
        "GET /agents/*/card",
        "GET /agents/*/credentials",
        "POST /agents/*/credentials",
        "POST /agents/*/credentials/*/revoke",
        "GET /agents/*/did",
        "POST /agents/*/did/rotate",
        "GET /agents/*/email-identities",
        "POST /agents/*/email-identities",
        "DELETE /agents/*/email-identities/*",
        "POST /agents/*/email-identities/*/set-primary",
        "POST /agents/*/email-identities/*/verify",
        "GET /agents/*/policy",
        "PUT /agents/*/policy",
        "POST /agents/*/rotate-key",
        "GET /api-keys",
        "POST /api-keys",
        "DELETE /api-keys/*",
        "PATCH /api-keys/*",
        "POST /api-keys/*/rotate",
        "GET /api-keys/scopes",
        "GET /attachments/*/download",
        "GET /attachments/*/text",
        "GET /audit/events",
        "POST /billing/change-plan",
        "POST /billing/checkout",
        "POST /billing/contact-enterprise",
        "GET /billing/features/*",
        "GET /billing/invoices",
        "GET /billing/overage",
        "PUT /billing/overage",
        "GET /billing/plans",
        "POST /billing/portal",
        "GET /billing/tier",
        "GET /billing/usage",
        "POST /demo/inbox",
        "GET /demo/inbox/*/messages",
        "POST /demo/inbox/*/self-test",
        "GET /domains",
        "POST /domains",
        "DELETE /domains/*",
        "GET /domains/*",
        "PATCH /domains/*",
        "GET /domains/*/deliverability",
        "GET /domains/*/dns-records",
        "POST /domains/*/verify",
        "GET /domains/*/zone-file",
        "GET /email",
        "GET /email-rules",
        "POST /email-rules",
        "DELETE /email-rules/*",
        "POST /email-rules/evaluate",
        "GET /email/*",
        "POST /email/*/forward",
        "POST /email/*/reply",
        "GET /email/drafts",
        "POST /email/drafts",
        "DELETE /email/drafts/*",
        "GET /email/drafts/*",
        "POST /email/drafts/*/send",
        "POST /email/send",
        "GET /email/suppressions",
        "POST /email/unsuppress",
        "GET /events/stream",
        "POST /extension/connect",
        "POST /extension/exchange",
        "POST /extension/revoke",
        "GET /extension/settings",
        "PATCH /extension/settings",
        "POST /extension/token",
        "PATCH /extension/token/*",
        "GET /feedback",
        "POST /feedback",
        "POST /identities",
        "POST /identity/verify",
        "GET /inboxes",
        "POST /inboxes",
        "DELETE /inboxes/*",
        "GET /inboxes/*",
        "PATCH /inboxes/*",
        "GET /invoices",
        "GET /invoices/*",
        "PATCH /invoices/*",
        "GET /invoices/export",
        "POST /invoices/match-receipts",
        "GET /invoices/reconciliation-summary",
        "POST /mcp-auth/sessions",
        "POST /mcp-auth/sessions/*/complete",
        "POST /mcp-auth/sessions/*/deny",
        "POST /mcp-auth/sessions/poll",
        "GET /me/agents",
        "GET /me/orgs",
        "GET /messages",
        "GET /messages/*",
        "POST /messages/*/attachments",
        "PATCH /messages/*/labels",
        "POST /messages/email",
        "POST /messages/search",
        "POST /messages/search/semantic",
        "POST /messages/sms",
        "POST /oauth/apps",
        "GET /oauth/apps/*",
        "PATCH /oauth/apps/*",
        "POST /oauth/auth-codes/mint",
        "POST /oauth/register",
        "POST /oauth/revoke",
        "POST /oauth/token",
        "GET /oauth/userinfo",
        "GET /openclaw/agents",
        "GET /openclaw/authorize",
        "GET /openclaw/callback",
        "POST /openclaw/signup",
        "GET /orgs",
        "POST /orgs",
        "DELETE /orgs/*",
        "GET /orgs/*",
        "PATCH /orgs/*",
        "GET /orgs/*/access-reviews",
        "POST /orgs/*/access-reviews",
        "POST /orgs/*/access-reviews/*/complete",
        "GET /orgs/*/agents/*/baselines",
        "DELETE /orgs/*/agents/*/quarantine",
        "GET /orgs/*/agents/*/quarantine",
        "POST /orgs/*/agents/*/quarantine",
        "GET /orgs/*/anomaly-alerts",
        "GET /orgs/*/anomaly-alerts/*",
        "POST /orgs/*/anomaly-alerts/*/acknowledge",
        "POST /orgs/*/anomaly-alerts/*/false-positive",
        "POST /orgs/*/anomaly-alerts/*/resolve",
        "GET /orgs/*/anomaly-rules",
        "POST /orgs/*/anomaly-rules",
        "DELETE /orgs/*/anomaly-rules/*",
        "PATCH /orgs/*/anomaly-rules/*",
        "GET /orgs/*/audit-logs",
        "GET /orgs/*/audit-logs/*",
        "POST /orgs/*/audit-logs/export",
        "POST /orgs/*/claim",
        "GET /orgs/*/compliance/controls",
        "GET /orgs/*/compliance/controls/*",
        "PATCH /orgs/*/compliance/controls/*",
        "POST /orgs/*/compliance/controls/*/collect",
        "GET /orgs/*/compliance/controls/*/evidence",
        "POST /orgs/*/compliance/controls/*/evidence",
        "GET /orgs/*/compliance/dashboard",
        "GET /orgs/*/compliance/dsars",
        "POST /orgs/*/compliance/dsars",
        "GET /orgs/*/compliance/dsars/*",
        "PATCH /orgs/*/compliance/dsars/*",
        "GET /orgs/*/compliance/reports",
        "POST /orgs/*/compliance/reports",
        "DELETE /orgs/*/compliance/reports/*",
        "GET /orgs/*/compliance/reports/*",
        "POST /orgs/*/compliance/reports/*/export",
        "POST /orgs/*/compliance/seed",
        "GET /orgs/*/compliance/summary",
        "GET /orgs/*/compliance/templates",
        "GET /orgs/*/members",
        "POST /orgs/*/messages/*/approve",
        "POST /orgs/*/rotate-key",
        "GET /orgs/*/security/events",
        "GET /orgs/*/security/scanner-status",
        "GET /orgs/claimable",
        "POST /orgs/feature-interest",
        "GET /orgs/me",
        "GET /orgs/me/usage",
        "GET /orgs/me/workspace-health",
        "GET /phone/numbers",
        "POST /phone/provision",
        "POST /phone/release",
        "GET /phone/requirements",
        "GET /phone/search",
        "POST /phone/send-sms",
        "GET /phone/sms-suppressions",
        "POST /phone/sms-unsuppress",
        "GET /phone/sms/threads",
        "GET /phone/sms/threads/*",
        "POST /registry/agents",
        "DELETE /registry/agents/*",
        "GET /registry/agents/*",
        "PUT /registry/agents/*",
        "GET /registry/agents/search",
        "GET /scoped-tokens",
        "POST /scoped-tokens",
        "POST /scoped-tokens/revoke",
        "GET /threads",
        "GET /vault/audit",
        "GET /vault/credential-requests",
        "POST /vault/credential-requests",
        "GET /vault/credential-requests/*",
        "POST /vault/credential-requests/*/cancel",
        "GET /vault/credentials",
        "POST /vault/credentials",
        "DELETE /vault/credentials/*",
        "GET /vault/credentials/*",
        "PUT /vault/credentials/*",
        "POST /vault/credentials/*/use",
        "POST /vault/deprovision",
        "POST /vault/generate-password",
        "GET /vault/identities",
        "GET /vault/oauth/accounts",
        "DELETE /vault/oauth/accounts/*",
        "GET /vault/oauth/apps",
        "GET /vault/oauth/apps/*",
        "POST /vault/oauth/apps/*/custom",
        "DELETE /vault/oauth/apps/*/custom/*",
        "POST /vault/oauth/link",
        "GET /vault/oauth/link/*",
        "POST /vault/oauth/require-auth",
        "POST /vault/provision",
        "GET /vault/search",
        "POST /vault/share",
        "POST /vault/share/revoke",
        "GET /vault/shares",
        "GET /vault/status",
        "POST /vault/sync",
        "POST /vault/token",
        "POST /vault/token/exchange",
        "POST /vault/token/revoke",
        "GET /vault/totp/*",
        "GET /voice/analytics",
        "GET /voice/calls",
        "POST /voice/calls",
        "GET /voice/calls/*",
        "GET /voice/calls/*/recording",
        "GET /voice/calls/*/score",
        "GET /voice/calls/*/security",
        "GET /voice/calls/*/summary",
        "GET /voice/calls/*/transcript",
        "GET /voice/catalog",
        "POST /voice/search",
        "POST /voice/search/cross-channel",
        "GET /webhooks",
        "POST /webhooks",
        "DELETE /webhooks/*",
        "GET /webhooks/*",
        "PUT /webhooks/*",
        "GET /webhooks/*/dead-letters",
        "GET /webhooks/*/deliveries",
        "POST /webhooks/*/reenable",
        "POST /webhooks/*/rotate-secret",
        "GET /webhooks/*/stats",
        "POST /webhooks/*/test",
        "POST /webhooks/deliveries/*/replay",
        "GET /webhooks/event-types",
    ]
)

_CALL = re.compile(r'request\(\s*"([A-Z]+)",\s*f?"([^"]+)"')

# Catches a path built by concatenation instead of an f-string. _CALL stops at
# the closing quote of the first literal, so ``"GET", "/voice/calls/" + call_id
# + "/transcript"`` would be checked as GET /voice/calls -- a real route, so it
# passes while everything after the id goes unverified. The go SDK shipped
# exactly that. Use an f-string.
_CONCAT = re.compile(r'request\(\s*"[A-Z]+",\s*"(/[^"]*)"\s*\+')


def _normalise(path: str) -> str:
    """Path params differ per call site; compare shapes, not ids."""
    return re.sub(r"/+", "/", re.sub(r"\{[^}]*\}", "*", path)).rstrip("/") or "/"


def _sdk_calls() -> list[tuple[str, str]]:
    """``(file, "METHOD /path")`` for every request the SDK issues."""
    found: list[tuple[str, str]] = []
    for path in sorted(RESOURCES_DIR.rglob("*.py")):
        if "__pycache__" in str(path):
            continue
        for method, raw in _CALL.findall(path.read_text()):
            if not raw.startswith("/"):
                continue
            found.append((path.name, f"{method} {_normalise(raw)}"))
    return found


def test_scan_actually_found_the_resource_calls() -> None:
    # If the regex above ever stops matching, the check below would pass
    # vacuously.
    assert len(_sdk_calls()) > 120


def test_no_resource_calls_a_route_the_api_does_not_serve() -> None:
    unknown = sorted(f"{name}: {route}" for name, route in _sdk_calls() if route not in API_ROUTES)
    assert unknown == []


def test_no_resource_builds_a_path_by_concatenation() -> None:
    concatenated: list[str] = []
    for path in sorted(RESOURCES_DIR.rglob("*.py")):
        if "__pycache__" in str(path):
            continue
        concatenated += [
            f'{path.name}: "{prefix}" + ... -- the scan cannot see past the +, use an f-string'
            for prefix in _CONCAT.findall(path.read_text())
        ]
    assert concatenated == []
