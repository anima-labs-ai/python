"""Tests for OrganizationsResource, and for the Tier enum it parses into.

The tier tests exist because a missing enum member is not a cosmetic gap in
this SDK. `OrganizationOutput.tier` is typed `Tier`, pydantic validates enum
fields, and so an organization on a tier this enum does not list cannot be
parsed at all — `organizations.get()` raises ValidationError instead of
returning. STARTER was missing for months while DEVELOPER and SCALE, which the
API cannot return, were listed; every Starter-plan customer hit that.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from anima._types import OrganizationOutput, Tier
from anima.resources.organizations import OrganizationsResource

# ---------------------------------------------------------------------------
# Raw API response fixtures
# ---------------------------------------------------------------------------


def org_raw(tier: str) -> dict[str, Any]:
    return {
        "id": "org_001",
        "name": "Acme",
        "slug": "acme",
        "clerkOrgId": None,
        "tier": tier,
        "masterKey": "sk-test-master",
        "settings": {},
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z",
    }


# The tiers the API can actually assign. Mirrors `TierSchema` in
# packages/contracts/src/schemas/organization.ts and the Prisma `Tier` enum.
# Written out rather than derived from `Tier` — a test that reads the same
# enum it is checking cannot fail when that enum is wrong.
LIVE_TIERS = ("FREE", "STARTER", "GROWTH", "ENTERPRISE")

# Tiers that were listed here but have never existed server-side. Kept as an
# explicit list so re-adding one is a test failure rather than a silent
# widening of what we claim the API returns.
PHANTOM_TIERS = ("DEVELOPER", "SCALE")


class TestTierEnum:
    @pytest.mark.parametrize("tier", LIVE_TIERS)
    def test_every_live_tier_parses(self, tier: str) -> None:
        # The regression itself: Stripe assigns STARTER, so this raised for any
        # customer on the Starter plan.
        org = OrganizationOutput.model_validate(org_raw(tier))
        assert org.tier.value == tier

    @pytest.mark.parametrize("tier", PHANTOM_TIERS)
    def test_phantom_tiers_are_rejected(self, tier: str) -> None:
        # Accepting these is what let the drift hide: the SDK looked tolerant
        # while silently disagreeing with the contract about what a tier is.
        with pytest.raises(ValidationError):
            OrganizationOutput.model_validate(org_raw(tier))

    def test_enum_matches_the_contract_exactly(self) -> None:
        # Guards both directions. Dropping a live tier breaks parsing for real
        # customers; adding a phantom one re-opens the gap above.
        assert tuple(t.value for t in Tier) == LIVE_TIERS


class TestOrganizationsGet:
    def test_get_parses_a_starter_org(self, mock_http: MagicMock) -> None:
        # End-to-end through the resource, not just the model: this is the call
        # that failed in the field.
        mock_http.request.return_value = org_raw("STARTER")
        resource = OrganizationsResource(mock_http)
        org = resource.get("org_001")

        mock_http.request.assert_called_once_with("GET", "/orgs/org_001", options=None)
        assert org.tier is Tier.STARTER
        assert org.id == "org_001"
        assert org.master_key == "sk-test-master"
