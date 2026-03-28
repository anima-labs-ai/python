from __future__ import annotations

from .._http import AsyncHTTPClient, HTTPClient
from .._types import (
    AgentCardOutput,
    DidDocument,
    DidRotateOutput,
    VerifiableCredential,
    VerifyCredentialOutput,
)


class IdentityResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def get_did(self, agent_id: str) -> DidDocument:
        return DidDocument.model_validate(
            self._client.request("GET", f"/agents/{agent_id}/did")
        )

    def resolve_did(self, did: str) -> DidDocument:
        return DidDocument.model_validate(
            self._client.request("GET", f"/identity/did/{did}")
        )

    def rotate_keys(self, agent_id: str) -> DidRotateOutput:
        return DidRotateOutput.model_validate(
            self._client.request("POST", f"/agents/{agent_id}/did/rotate")
        )

    def list_credentials(self, agent_id: str) -> list[VerifiableCredential]:
        raw = self._client.request("GET", f"/agents/{agent_id}/credentials")
        return [VerifiableCredential.model_validate(item) for item in raw["items"]]

    def verify_credential(self, jwt_vc: str) -> VerifyCredentialOutput:
        return VerifyCredentialOutput.model_validate(
            self._client.request("POST", "/identity/verify", {"jwtVc": jwt_vc})
        )

    def get_agent_card(self, agent_id: str) -> AgentCardOutput:
        return AgentCardOutput.model_validate(
            self._client.request("GET", f"/agents/{agent_id}/card")
        )


class AsyncIdentityResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get_did(self, agent_id: str) -> DidDocument:
        return DidDocument.model_validate(
            await self._client.request("GET", f"/agents/{agent_id}/did")
        )

    async def resolve_did(self, did: str) -> DidDocument:
        return DidDocument.model_validate(
            await self._client.request("GET", f"/identity/did/{did}")
        )

    async def rotate_keys(self, agent_id: str) -> DidRotateOutput:
        return DidRotateOutput.model_validate(
            await self._client.request("POST", f"/agents/{agent_id}/did/rotate")
        )

    async def list_credentials(self, agent_id: str) -> list[VerifiableCredential]:
        raw = await self._client.request("GET", f"/agents/{agent_id}/credentials")
        return [VerifiableCredential.model_validate(item) for item in raw["items"]]

    async def verify_credential(self, jwt_vc: str) -> VerifyCredentialOutput:
        return VerifyCredentialOutput.model_validate(
            await self._client.request("POST", "/identity/verify", {"jwtVc": jwt_vc})
        )

    async def get_agent_card(self, agent_id: str) -> AgentCardOutput:
        return AgentCardOutput.model_validate(
            await self._client.request("GET", f"/agents/{agent_id}/card")
        )
