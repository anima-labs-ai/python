from __future__ import annotations

from typing import Any

from ..._http import RequestOptions
from ..._types import (
    VaultCredentialRequest,
    VaultCredentialRequestCancelResult,
    VaultCredentialRequestStatusOutput,
)
from ._base import _AsyncVaultBase, _SyncVaultBase


class _SyncCredentialRequestsMixin(_SyncVaultBase):
    def credential_request_create(
        self,
        *,
        type: str,
        name: str,
        reason: str,
        agent_id: str | None = None,
        ttl_seconds: int | None = None,
        notify_owner: bool | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredentialRequest:
        """Ask a human for a credential the agent must never see.

        Returns a token-gated fill URL the owner completes out-of-band; poll
        ``credential_request_status`` until FULFILLED, then use the credential
        by reference (``use_credential``) — the plaintext is never returned.
        """
        body: dict[str, Any] = {"type": type, "name": name, "reason": reason}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl_seconds is not None:
            body["ttlSeconds"] = ttl_seconds
        if notify_owner is not None:
            body["notifyOwner"] = notify_owner
        return VaultCredentialRequest.model_validate(
            self._client.request("POST", "/vault/credential-requests", body, options=options)
        )

    def credential_request_status(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestStatusOutput:
        return VaultCredentialRequestStatusOutput.model_validate(
            self._client.request("GET", f"/vault/credential-requests/{request_id}", options=options)
        )

    def credential_request_cancel(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestCancelResult:
        return VaultCredentialRequestCancelResult.model_validate(
            self._client.request(
                "POST", f"/vault/credential-requests/{request_id}/cancel", None, options=options
            )
        )


class _AsyncCredentialRequestsMixin(_AsyncVaultBase):
    async def credential_request_create(
        self,
        *,
        type: str,
        name: str,
        reason: str,
        agent_id: str | None = None,
        ttl_seconds: int | None = None,
        notify_owner: bool | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredentialRequest:
        """Ask a human for a credential the agent must never see.

        Returns a token-gated fill URL the owner completes out-of-band; poll
        ``credential_request_status`` until FULFILLED, then use the credential
        by reference (``use_credential``) — the plaintext is never returned.
        """
        body: dict[str, Any] = {"type": type, "name": name, "reason": reason}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl_seconds is not None:
            body["ttlSeconds"] = ttl_seconds
        if notify_owner is not None:
            body["notifyOwner"] = notify_owner
        return VaultCredentialRequest.model_validate(
            await self._client.request("POST", "/vault/credential-requests", body, options=options)
        )

    async def credential_request_status(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestStatusOutput:
        return VaultCredentialRequestStatusOutput.model_validate(
            await self._client.request(
                "GET", f"/vault/credential-requests/{request_id}", options=options
            )
        )

    async def credential_request_cancel(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestCancelResult:
        return VaultCredentialRequestCancelResult.model_validate(
            await self._client.request(
                "POST", f"/vault/credential-requests/{request_id}/cancel", None, options=options
            )
        )
