from __future__ import annotations

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
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

    def get_did(self, agent_id: str, *, options: RequestOptions | None = None) -> DidDocument:
        return DidDocument.model_validate(
            self._client.request("GET", f"/agents/{agent_id}/did", options=options)
        )

    def resolve_did(self, did: str, *, options: RequestOptions | None = None) -> DidDocument:
        return DidDocument.model_validate(
            self._client.request("GET", f"/identity/did/{did}", options=options)
        )

    def rotate_keys(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> DidRotateOutput:
        return DidRotateOutput.model_validate(
            self._client.request("POST", f"/agents/{agent_id}/did/rotate", options=options)
        )

    def list_credentials(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> list[VerifiableCredential]:
        raw = self._client.request("GET", f"/agents/{agent_id}/credentials", options=options)
        return [VerifiableCredential.model_validate(item) for item in raw["items"]]

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

    async def resolve_did(self, did: str, *, options: RequestOptions | None = None) -> DidDocument:
        return DidDocument.model_validate(
            await self._client.request("GET", f"/identity/did/{did}", options=options)
        )

    async def rotate_keys(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> DidRotateOutput:
        return DidRotateOutput.model_validate(
            await self._client.request("POST", f"/agents/{agent_id}/did/rotate", options=options)
        )

    async def list_credentials(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> list[VerifiableCredential]:
        raw = await self._client.request("GET", f"/agents/{agent_id}/credentials", options=options)
        return [VerifiableCredential.model_validate(item) for item in raw["items"]]

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
