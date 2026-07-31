"""Tests for IdentityResource, pinning it to the API contract.

This resource had no test file, and two things were wrong because of it.

``list_credentials`` read ``raw["items"]``, but GET
``/agents/{agentId}/credentials`` returns a bare JSON array -- the contract
output is ``z.array(VerifiableCredentialOutput)``, not a paginated envelope.
Every call raised ``TypeError: list indices must be integers``. It then parsed
each item as the W3C credential *document* (issuer/subject/credentialSubject/
proof) when the endpoint returns the platform *record* (id/agentId/orgId/
jwtVc/revoked), so even an envelope would not have parsed.

``issue_credential`` and ``revoke_credential`` did not exist at all, though
node and go both had them.

Source of truth, at the commit pinned in .anima-ref:
  packages/contracts/src/schemas/identity.ts
  packages/contracts/src/contracts/identity.ts
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import VerifiableCredentialRecord, VerifiableCredentialType
from anima.resources.identity import AsyncIdentityResource, IdentityResource

VC_RECORD_RAW: dict[str, Any] = {
    "id": "vc_001",
    "agentId": "agent_001",
    "orgId": "org_001",
    "type": "AnimaAddressVerified",
    "jwtVc": "eyJhbGciOiJFZERTQSJ9.eyJzdWIiOiJkaWQ6d2ViOmEifQ.sig",
    "issuerDid": "did:web:useanima.sh",
    "subjectDid": "did:web:useanima.sh:agents:agent_001",
    "issuedAt": "2026-07-31T00:00:00Z",
    "expiresAt": None,
    "revoked": False,
    "revokedAt": None,
    "revocationIndex": 7,
    "metadata": {"source": "api"},
    "createdAt": "2026-07-31T00:00:00Z",
    "updatedAt": "2026-07-31T00:00:00Z",
}


class TestListCredentials:
    def test_parses_a_bare_array(self, mock_http: MagicMock) -> None:
        """The endpoint is not paginated. Indexing ``["items"]`` here raises."""
        mock_http.request.return_value = [VC_RECORD_RAW]
        result = IdentityResource(mock_http).list_credentials("agent_001")

        mock_http.request.assert_called_once_with(
            "GET", "/agents/agent_001/credentials", options=None
        )
        assert len(result) == 1
        assert isinstance(result[0], VerifiableCredentialRecord)

    def test_parses_the_platform_record_not_the_w3c_document(self, mock_http: MagicMock) -> None:
        """These fields exist only on the record; the document has none of them."""
        mock_http.request.return_value = [VC_RECORD_RAW]
        [record] = IdentityResource(mock_http).list_credentials("agent_001")

        assert record.jwt_vc.startswith("eyJ")
        assert record.org_id == "org_001"
        assert record.revoked is False
        assert record.revocation_index == 7

    def test_empty_list(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = []
        assert IdentityResource(mock_http).list_credentials("agent_001") == []

    @pytest.mark.asyncio()
    async def test_async_parses_a_bare_array(self) -> None:
        client = AsyncMock(spec=AsyncHTTPClient)
        client.request.return_value = [VC_RECORD_RAW]
        result = await AsyncIdentityResource(client).list_credentials("agent_001")

        assert len(result) == 1
        assert result[0].jwt_vc.startswith("eyJ")


class TestIssueCredential:
    def test_sends_the_enum_wire_value(self, mock_http: MagicMock) -> None:
        """The API validates the PascalCase strings, not the member names."""
        mock_http.request.return_value = VC_RECORD_RAW
        IdentityResource(mock_http).issue_credential(
            "agent_001", VerifiableCredentialType.ADDRESS_VERIFIED
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/agents/agent_001/credentials",
            {"agentId": "agent_001", "type": "AnimaAddressVerified"},
            options=None,
        )

    def test_accepts_a_plain_string(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VC_RECORD_RAW
        IdentityResource(mock_http).issue_credential("agent_001", "AnimaTrustScore")

        assert mock_http.request.call_args[0][2]["type"] == "AnimaTrustScore"

    def test_omits_unset_optionals(self, mock_http: MagicMock) -> None:
        """A null claims/expiry must not be sent -- the contract omits them."""
        mock_http.request.return_value = VC_RECORD_RAW
        IdentityResource(mock_http).issue_credential("agent_001", "AnimaTrustScore")

        assert mock_http.request.call_args[0][2] == {
            "agentId": "agent_001",
            "type": "AnimaTrustScore",
        }

    def test_sends_claims_and_expiry(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VC_RECORD_RAW
        IdentityResource(mock_http).issue_credential(
            "agent_001",
            VerifiableCredentialType.TRUST_SCORE,
            claims={"score": 92},
            expires_in_seconds=3600,
        )

        assert mock_http.request.call_args[0][2] == {
            "agentId": "agent_001",
            "type": "AnimaTrustScore",
            "claims": {"score": 92},
            "expiresInSeconds": 3600,
        }

    @pytest.mark.asyncio()
    async def test_async(self) -> None:
        client = AsyncMock(spec=AsyncHTTPClient)
        client.request.return_value = VC_RECORD_RAW
        result = await AsyncIdentityResource(client).issue_credential(
            "agent_001", VerifiableCredentialType.ADDRESS_VERIFIED
        )

        assert client.request.call_args[0][1] == "/agents/agent_001/credentials"
        assert result.type == "AnimaAddressVerified"


class TestRevokeCredential:
    def test_posts_to_the_revoke_path(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {**VC_RECORD_RAW, "revoked": True}
        result = IdentityResource(mock_http).revoke_credential("agent_001", "vc_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/agents/agent_001/credentials/vc_001/revoke",
            {"agentId": "agent_001", "vcId": "vc_001"},
            options=None,
        )
        assert result.revoked is True

    @pytest.mark.asyncio()
    async def test_async(self) -> None:
        client = AsyncMock(spec=AsyncHTTPClient)
        client.request.return_value = {**VC_RECORD_RAW, "revoked": True}
        result = await AsyncIdentityResource(client).revoke_credential("agent_001", "vc_001")

        assert client.request.call_args[0][1] == "/agents/agent_001/credentials/vc_001/revoke"
        assert result.revoked is True
