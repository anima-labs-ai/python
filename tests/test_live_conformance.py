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
    export ANIMA_LIVE_AGENT_ID=...          # required for agent-scoped vault probes
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
AGENT_ID = os.environ.get("ANIMA_LIVE_AGENT_ID")
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


# How many probes got a real 2xx back. A 401 is a pass for each probe on its
# own -- it proves the route exists -- but that does not compose: a key scoped
# for nothing 401s everywhere and turns the whole module green having checked
# no path, no query param and no response shape. See the canary at the bottom.
_reached = 0


def probe(call: Callable[[], Any]) -> None:
    """Run one read-only call and apply the verdict table in this module's docs.

    Returning normally means the probe passed. Anything that reaches the
    ``pytest.fail`` calls below is a real conformance defect.
    """
    global _reached
    try:
        result = call()
        # PageIterator is lazy — force the first page so the request happens
        # and the response is validated.
        if hasattr(result, "items"):
            _ = result.items
        _reached += 1
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
        # A vault route that reaches `bw serve` and finds nothing listening has
        # already proved everything conformance cares about: the route exists,
        # auth passed, and the API accepted the request the SDK built. The
        # missing piece is the deployment's storage backend. Narrow on purpose
        # -- only this connectivity message; every other 5xx still fails.
        if "bw-serve: Unable to connect" in str(err):
            return
        pytest.fail(f"5xx from the live API (likely not the SDK's fault): {err}")


org_scoped = pytest.mark.skipif(not ORG_ID, reason="set ANIMA_LIVE_ORG_ID for org-scoped probes")
# Several vault routes are agent-scoped and REJECT a master key that does not
# name an agent ("agentId is required when using a master key"). Without one
# they skip rather than fail for a reason unrelated to conformance.
agent_scoped = pytest.mark.skipif(
    not AGENT_ID, reason="set ANIMA_LIVE_AGENT_ID for agent-scoped vault probes"
)


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

    @agent_scoped
    def test_vault_status(self, client: Anima) -> None:
        probe(lambda: client.vault.status(agent_id=AGENT_ID))

    @agent_scoped
    def test_vault_list_shares(self, client: Anima) -> None:
        probe(lambda: client.vault.list_shares(agent_id=AGENT_ID, direction="granted"))


class TestProvisioningRequests:
    """An agent asking its owner for a vault or a phone number.

    The status and resource filters are server-side enums: sending the wrong
    casing earns a 400, and no fixture ever would.
    """

    def test_list(self, client: Anima) -> None:
        probe(lambda: client.provisioning_requests.list(limit=1))

    def test_list_status_filter(self, client: Anima) -> None:
        probe(lambda: client.provisioning_requests.list(status="PENDING", limit=1))

    def test_list_resource_filter(self, client: Anima) -> None:
        probe(lambda: client.provisioning_requests.list(resource="VAULT", limit=1))


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

    @org_scoped
    def test_audit_actor_type_enum(self, client: Anima) -> None:
        """UPPERCASE in the contract; this SDK had it lowercase until 2026-08-04.

        Sent as a FILTER, so a wrong casing is a 400 rather than an empty list
        -- a response-shape assertion would pass on an org with no audit rows.
        """
        from anima._types import AuditActorType

        for actor_type in AuditActorType:
            probe(
                lambda a=actor_type: client.audit.list(
                    org_id=ORG_ID or "", actor_type=a.value, limit=1
                )
            )

    @org_scoped
    def test_audit_result_enum(self, client: Anima) -> None:
        from anima._types import AuditResult

        for result in AuditResult:
            probe(
                lambda r=result: client.audit.list(
                    org_id=ORG_ID or "", result=r.value, limit=1
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


def test_the_run_reached_the_api() -> None:
    """Fail a run in which no probe ever got a 2xx.

    Every verdict above is sound on its own, but "401 is a pass" does not
    compose: a key with no scopes is rejected everywhere, each probe passes
    because the route demonstrably exists, and the module goes green having
    verified nothing at all -- the same hollow tick the mocks were giving us,
    which is the entire reason this file exists.

    Deliberately the last test in the module: pytest runs tests in file order,
    so every probe above has already run and settled ``_reached``.
    """
    assert _reached > 0, (
        "no probe reached the API: every call was rejected (401/403), rate "
        "limited, or skipped, so this run verified no path, no query param "
        "and no response shape. Check that ANIMA_LIVE_API_KEY is valid and "
        "scoped -- a green run in this state would prove nothing."
    )
