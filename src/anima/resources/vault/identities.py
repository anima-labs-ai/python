from __future__ import annotations

from ..._http import RequestOptions
from ..._pagination import AsyncPageIterator, SyncPageIterator
from ..._types import PaginatedResponse, VaultAuditLogEntry, VaultIdentityListItem
from ._base import _AsyncVaultBase, _SyncVaultBase


def _identities_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    status: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if status is not None:
        params["status"] = status
    return params or None


def _audit_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    credential_id: str | None = None,
    agent_id: str | None = None,
    action: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if credential_id is not None:
        params["credentialId"] = credential_id
    if agent_id is not None:
        params["agentId"] = agent_id
    if action is not None:
        params["action"] = action
    if since is not None:
        params["since"] = since
    if until is not None:
        params["until"] = until
    return params or None


class _SyncIdentitiesMixin(_SyncVaultBase):
    def list_identities(
        self,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[VaultIdentityListItem]:
        def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            status: str | None = status,
        ) -> PaginatedResponse[VaultIdentityListItem]:
            raw = self._client.request(
                "GET",
                "/vault/identities",
                query=_identities_query(cursor=cursor, limit=limit, status=status),
                options=options,
            )
            return PaginatedResponse[VaultIdentityListItem].model_validate(raw)

        return SyncPageIterator(_fetch, cursor=cursor, limit=limit, status=status)

    def audit(
        self,
        *,
        credential_id: str | None = None,
        agent_id: str | None = None,
        action: str | None = None,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[VaultAuditLogEntry]:
        """Query the credential audit trail.

        Every access, share, broker use, and denied egress is recorded here —
        never with any secret material.
        """

        def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            credential_id: str | None = credential_id,
            agent_id: str | None = agent_id,
            action: str | None = action,
            since: str | None = since,
            until: str | None = until,
        ) -> PaginatedResponse[VaultAuditLogEntry]:
            raw = self._client.request(
                "GET",
                "/vault/audit",
                query=_audit_query(
                    cursor=cursor,
                    limit=limit,
                    credential_id=credential_id,
                    agent_id=agent_id,
                    action=action,
                    since=since,
                    until=until,
                ),
                options=options,
            )
            return PaginatedResponse[VaultAuditLogEntry].model_validate(raw)

        return SyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            credential_id=credential_id,
            agent_id=agent_id,
            action=action,
            since=since,
            until=until,
        )


class _AsyncIdentitiesMixin(_AsyncVaultBase):
    def list_identities(
        self,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[VaultIdentityListItem]:
        async def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            status: str | None = status,
        ) -> PaginatedResponse[VaultIdentityListItem]:
            raw = await self._client.request(
                "GET",
                "/vault/identities",
                query=_identities_query(cursor=cursor, limit=limit, status=status),
                options=options,
            )
            return PaginatedResponse[VaultIdentityListItem].model_validate(raw)

        return AsyncPageIterator(_fetch, cursor=cursor, limit=limit, status=status)

    def audit(
        self,
        *,
        credential_id: str | None = None,
        agent_id: str | None = None,
        action: str | None = None,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[VaultAuditLogEntry]:
        """Query the credential audit trail.

        Every access, share, broker use, and denied egress is recorded here —
        never with any secret material.
        """

        async def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            credential_id: str | None = credential_id,
            agent_id: str | None = agent_id,
            action: str | None = action,
            since: str | None = since,
            until: str | None = until,
        ) -> PaginatedResponse[VaultAuditLogEntry]:
            raw = await self._client.request(
                "GET",
                "/vault/audit",
                query=_audit_query(
                    cursor=cursor,
                    limit=limit,
                    credential_id=credential_id,
                    agent_id=agent_id,
                    action=action,
                    since=since,
                    until=until,
                ),
                options=options,
            )
            return PaginatedResponse[VaultAuditLogEntry].model_validate(raw)

        return AsyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            credential_id=credential_id,
            agent_id=agent_id,
            action=action,
            since=since,
            until=until,
        )
