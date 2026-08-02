from __future__ import annotations

from typing import Any

from ..._http import RequestOptions
from ..._pagination import AsyncPageIterator, SyncPageIterator
from ..._types import (
    CredentialRequestStatus,
    PaginatedResponse,
    VaultCredentialRequest,
    VaultCredentialRequestCancelResult,
    VaultCredentialRequestListItem,
    VaultCredentialRequestStatusOutput,
)
from ._base import _AsyncVaultBase, _SyncVaultBase


def _requests_query(
    cursor: str | None,
    limit: int | None,
    agent_id: str | None,
    status: CredentialRequestStatus | str | None,
) -> dict[str, Any] | None:
    query: dict[str, Any] = {}
    if cursor is not None:
        query["cursor"] = cursor
    if limit is not None:
        query["limit"] = limit
    if agent_id is not None:
        query["agentId"] = agent_id
    if status is not None:
        # Enum unwrapping happens in _http._encode_query.
        query["status"] = status
    return query or None


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

    def list_credential_requests(
        self,
        *,
        agent_id: str | None = None,
        status: CredentialRequestStatus | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[VaultCredentialRequestListItem]:
        """List credential requests across the organization, newest first.

        Statuses are lazily expired, so a request whose TTL has elapsed reads
        as EXPIRED here even though nothing wrote that transition.
        """

        def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            agent_id: str | None = agent_id,
            status: CredentialRequestStatus | str | None = status,
        ) -> PaginatedResponse[VaultCredentialRequestListItem]:
            raw = self._client.request(
                "GET",
                "/vault/credential-requests",
                query=_requests_query(cursor, limit, agent_id, status),
                options=options,
            )
            return PaginatedResponse[VaultCredentialRequestListItem].model_validate(raw)

        return SyncPageIterator(
            _fetch, cursor=cursor, limit=limit, agent_id=agent_id, status=status
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

    def list_credential_requests(
        self,
        *,
        agent_id: str | None = None,
        status: CredentialRequestStatus | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[VaultCredentialRequestListItem]:
        """List credential requests across the organization, newest first."""

        async def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            agent_id: str | None = agent_id,
            status: CredentialRequestStatus | str | None = status,
        ) -> PaginatedResponse[VaultCredentialRequestListItem]:
            raw = await self._client.request(
                "GET",
                "/vault/credential-requests",
                query=_requests_query(cursor, limit, agent_id, status),
                options=options,
            )
            return PaginatedResponse[VaultCredentialRequestListItem].model_validate(raw)

        return AsyncPageIterator(
            _fetch, cursor=cursor, limit=limit, agent_id=agent_id, status=status
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
