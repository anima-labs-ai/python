from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions, unwrap_enum
from .._types import (
    AgentCardOutput,
    DidDocument,
    DidRotateOutput,
    VerifiableCredentialRecord,
    VerifiableCredentialType,
    VerifyCredentialOutput,
)


def _issue_body(
    agent_id: str,
    credential_type: VerifiableCredentialType | str,
    claims: dict[str, Any] | None,
    expires_in_seconds: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "agentId": agent_id,
        "type": unwrap_enum(credential_type),
    }
    if claims is not None:
        body["claims"] = claims
    if expires_in_seconds is not None:
        body["expiresInSeconds"] = expires_in_seconds
    return body


class IdentityResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def get_did(self, agent_id: str, *, options: RequestOptions | None = None) -> DidDocument:
        return DidDocument.model_validate(
            self._client.request("GET", f"/agents/{agent_id}/did", options=options)
        )

    # No resolve_did. It called GET /identity/did/{did}, which the API has
    # never served, and resolving a DID to its owning agent is what
    # registry.lookup(did) does -- GET /registry/agents/{did}.

    def rotate_keys(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> DidRotateOutput:
        return DidRotateOutput.model_validate(
            self._client.request("POST", f"/agents/{agent_id}/did/rotate", options=options)
        )

    def list_credentials(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> list[VerifiableCredentialRecord]:
        """List an agent's credential records, newest first.

        The endpoint is not paginated -- it returns a bare JSON array, not an
        ``items`` envelope.
        """
        raw = self._client.request("GET", f"/agents/{agent_id}/credentials", options=options)
        return [VerifiableCredentialRecord.model_validate(item) for item in raw]

    def issue_credential(
        self,
        agent_id: str,
        credential_type: VerifiableCredentialType | str,
        *,
        claims: dict[str, Any] | None = None,
        expires_in_seconds: int | None = None,
        options: RequestOptions | None = None,
    ) -> VerifiableCredentialRecord:
        """Issue a verifiable credential to an agent. Master key only.

        Only the org-attestation types are issuable here; the platform-reserved
        types return 403. See :class:`VerifiableCredentialType`.
        """
        return VerifiableCredentialRecord.model_validate(
            self._client.request(
                "POST",
                f"/agents/{agent_id}/credentials",
                _issue_body(agent_id, credential_type, claims, expires_in_seconds),
                options=options,
            )
        )

    def revoke_credential(
        self, agent_id: str, vc_id: str, *, options: RequestOptions | None = None
    ) -> VerifiableCredentialRecord:
        """Revoke an issued credential. Master key only.

        Returns the updated record with ``revoked=True``; verifying its
        ``jwt_vc`` fails from then on.
        """
        return VerifiableCredentialRecord.model_validate(
            self._client.request(
                "POST",
                f"/agents/{agent_id}/credentials/{vc_id}/revoke",
                {"agentId": agent_id, "vcId": vc_id},
                options=options,
            )
        )

    def verify_credential(
        self, jwt_vc: str, *, options: RequestOptions | None = None
    ) -> VerifyCredentialOutput:
        return VerifyCredentialOutput.model_validate(
            self._client.request("POST", "/identity/verify", {"jwtVc": jwt_vc}, options=options)
        )

    def get_agent_card(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> AgentCardOutput:
        return AgentCardOutput.model_validate(
            self._client.request("GET", f"/agents/{agent_id}/card", options=options)
        )


class AsyncIdentityResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get_did(self, agent_id: str, *, options: RequestOptions | None = None) -> DidDocument:
        return DidDocument.model_validate(
            await self._client.request("GET", f"/agents/{agent_id}/did", options=options)
        )

    async def rotate_keys(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> DidRotateOutput:
        return DidRotateOutput.model_validate(
            await self._client.request("POST", f"/agents/{agent_id}/did/rotate", options=options)
        )

    async def list_credentials(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> list[VerifiableCredentialRecord]:
        """List an agent's credential records, newest first.

        The endpoint is not paginated -- it returns a bare JSON array, not an
        ``items`` envelope.
        """
        raw = await self._client.request("GET", f"/agents/{agent_id}/credentials", options=options)
        return [VerifiableCredentialRecord.model_validate(item) for item in raw]

    async def issue_credential(
        self,
        agent_id: str,
        credential_type: VerifiableCredentialType | str,
        *,
        claims: dict[str, Any] | None = None,
        expires_in_seconds: int | None = None,
        options: RequestOptions | None = None,
    ) -> VerifiableCredentialRecord:
        """Issue a verifiable credential to an agent. Master key only.

        Only the org-attestation types are issuable here; the platform-reserved
        types return 403. See :class:`VerifiableCredentialType`.
        """
        return VerifiableCredentialRecord.model_validate(
            await self._client.request(
                "POST",
                f"/agents/{agent_id}/credentials",
                _issue_body(agent_id, credential_type, claims, expires_in_seconds),
                options=options,
            )
        )

    async def revoke_credential(
        self, agent_id: str, vc_id: str, *, options: RequestOptions | None = None
    ) -> VerifiableCredentialRecord:
        """Revoke an issued credential. Master key only.

        Returns the updated record with ``revoked=True``; verifying its
        ``jwt_vc`` fails from then on.
        """
        return VerifiableCredentialRecord.model_validate(
            await self._client.request(
                "POST",
                f"/agents/{agent_id}/credentials/{vc_id}/revoke",
                {"agentId": agent_id, "vcId": vc_id},
                options=options,
            )
        )

    async def verify_credential(
        self, jwt_vc: str, *, options: RequestOptions | None = None
    ) -> VerifyCredentialOutput:
        return VerifyCredentialOutput.model_validate(
            await self._client.request(
                "POST", "/identity/verify", {"jwtVc": jwt_vc}, options=options
            )
        )

    async def get_agent_card(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> AgentCardOutput:
        return AgentCardOutput.model_validate(
            await self._client.request("GET", f"/agents/{agent_id}/card", options=options)
        )
