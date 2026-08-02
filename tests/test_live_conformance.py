"""Conformance probe against a DEPLOYED Anima API.

Everything else in this suite compares the SDK to a fixture written by whoever
wrote the code. That is why 29 calls to routes the API has never served stayed
green for months, why every compliance enum was lowercase against an uppercase
contract, and why ``list_credentials`` raised ``TypeError`` on every call: the
mock always agreed with the bug.

This is the half a mock cannot cover. Each probe calls a real read-only
endpoint over HTTP and classifies the outcome:

===================  =======  ==================================================
outcome              verdict  why
===================  =======  ==================================================
200 + parses         pass     route exists and the response matches the model
401 / 403            pass     route exists; this key just lacks the scope
404                  FAIL     the route is gone — the phantom-route class
400 / 422            FAIL     the API rejected OUR request: a bad enum value,
                              a mistyped query param, a wrong path param
5xx                  FAIL     reported separately; usually not the SDK's fault
===================  =======  ==================================================

The 400 row is the one that earns its keep. A lowercase ``DsarType`` reaches
the server, gets rejected, and fails here — where the mock happily accepted it.

Pydantic does the shape checking for free: every probe validates into the
SDK's declared model, so a renamed field, a changed envelope, or an enum value
outside the declared set raises ``ValidationError`` and fails the probe.

STRICTLY READ-ONLY. No probe creates, mutates or deletes anything: this runs
against a real organization. Do not add a POST here.

Run it:

    export ANIMA_LIVE_API_KEY=mk_...        # master key sees the most surface
    export ANIMA_LIVE_ORG_ID=org_...        # required for org-scoped probes
    export ANIMA_LIVE_BASE_URL=...          # optional, defaults to production
    pytest tests/test_live_conformance.py -v

Without ``ANIMA_LIVE_API_KEY`` the whole module skips, so normal CI is
unaffected.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from typing import Any

import pytest

from anima import Anima
from anima._exceptions import (
    AuthenticationError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

API_KEY = os.environ.get("ANIMA_LIVE_API_KEY")
ORG_ID = os.environ.get("ANIMA_LIVE_ORG_ID")
BASE_URL = os.environ.get("ANIMA_LIVE_BASE_URL")

pytestmark = pytest.mark.skipif(
    not API_KEY,
    reason="live conformance probe: set ANIMA_LIVE_API_KEY to run",
)


@pytest.fixture(scope="module")
def client() -> Iterator[Anima]:
    kwargs: dict[str, Any] = {"api_key": API_KEY}
    if BASE_URL:
        kwargs["base_url"] = BASE_URL
    yield Anima(**kwargs)


def probe(call: Callable[[], Any]) -> None:
    """Run one read-only call and apply the verdict table in this module's docs.

    Returning normally means the probe passed. Anything that reaches the
    ``pytest.fail`` calls below is a real conformance defect.
    """
    try:
        result = call()
        # PageIterator is lazy — force the first page so the request happens
        # and the response is validated.
        if hasattr(result, "items"):
            _ = result.items
    except NotFoundError as err:
        pytest.fail(
            f"404 — the API does not serve this route. Either the SDK path is "
            f"wrong or the endpoint was removed: {err}"
        )
    except ValidationError as err:
        pytest.fail(
            f"400/422 — the API rejected the request the SDK built. This is the "
            f"class of bug a mock cannot catch (wrong enum casing, wrong query "
            f"param name, wrong path param): {err}"
        )
    except AuthenticationError:
        # 401/403 proves the route exists and is reachable; this key simply is
        # not scoped for it. That is a pass for conformance purposes.
        return
    except RateLimitError:
        pytest.skip("rate limited by the live API")
    except InternalServerError as err:
        pytest.fail(f"5xx from the live API (likely not the SDK's fault): {err}")


org_scoped = pytest.mark.skipif(not ORG_ID, reason="set ANIMA_LIVE_ORG_ID for org-scoped probes")


class TestCoreSurface:
    def test_agents_list(self, client: Anima) -> None:
        probe(lambda: client.agents.list(limit=1))

    def test_domains_list(self, client: Anima) -> None:
        probe(lambda: client.domains.list())

    def test_inboxes_list(self, client: Anima) -> None:
        probe(lambda: client.inboxes.list(limit=1))

    def test_webhooks_list(self, client: Anima) -> None:
        probe(lambda: client.webhooks.list())

    def test_registry_search(self, client: Anima) -> None:
        probe(lambda: client.registry.search("test", limit=1))


class TestVoiceSurface:
    def test_voice_catalog(self, client: Anima) -> None:
        probe(lambda: client.voices.list())

    def test_calls_list(self, client: Anima) -> None:
        probe(lambda: client.calls.list(limit=1))


class TestVaultSurface:
    def test_vault_identities(self, client: Anima) -> None:
        probe(lambda: client.vault.list_identities(limit=1))

    def test_vault_audit(self, client: Anima) -> None:
        probe(lambda: client.vault.audit(limit=1))

    def test_vault_credential_requests(self, client: Anima) -> None:
        """Added 2026-08; nothing had exercised this route from any SDK."""
        probe(lambda: client.vault.list_credential_requests(limit=1))


@org_scoped
class TestOrgScopedSurface:
    """The surface that was most wrong, and is org-scoped so it needs an org id."""

    def test_audit_logs(self, client: Anima) -> None:
        probe(lambda: client.audit.list(org_id=ORG_ID or "", limit=1))

    def test_anomaly_alerts(self, client: Anima) -> None:
        probe(lambda: client.anomaly.list_alerts(org_id=ORG_ID or "", limit=1))

    def test_anomaly_rules(self, client: Anima) -> None:
        probe(lambda: client.anomaly.list_rules(org_id=ORG_ID or ""))

    def test_security_events(self, client: Anima) -> None:
        probe(lambda: client.security.list_events(org_id=ORG_ID or "", limit=1))

    def test_security_scanner_status(self, client: Anima) -> None:
        probe(lambda: client.security.get_scanner_status(org_id=ORG_ID or ""))

    def test_compliance_controls(self, client: Anima) -> None:
        probe(lambda: client.compliance.list_controls(org_id=ORG_ID or "", limit=1))

    def test_compliance_templates(self, client: Anima) -> None:
        probe(lambda: client.compliance.list_templates(org_id=ORG_ID or ""))


@org_scoped
class TestEnumsAreAcceptedByTheApi:
    """Send each enum the SDK declares and confirm the API accepts the value.

    This is the probe that would have caught the compliance bug outright. Every
    enum was lowercase against a contract that validates SCREAMING_SNAKE, so
    each of these would have come back 400 — while the mocked tests passed.
    """

    def test_compliance_framework_enum(self, client: Anima) -> None:
        from anima import ComplianceFramework

        for framework in ComplianceFramework:
            probe(
                lambda f=framework: client.compliance.list_controls(
                    org_id=ORG_ID or "", framework=f, limit=1
                )
            )

    def test_security_severity_enum(self, client: Anima) -> None:
        """Also proves the query encoder: a raw Enum would send its repr."""
        from anima import SecuritySeverity

        for severity in SecuritySeverity:
            probe(
                lambda s=severity: client.security.list_events(
                    org_id=ORG_ID or "", severity=s, limit=1
                )
            )
