from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import AuditLogExportOutput, AuditLogOutput, CursorPage


class AuditResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list(
        self,
        *,
        org_id: str,
        actor_id: str | None = None,
        actor_type: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        result: str | None = None,
        query: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[AuditLogOutput]:
        params: dict[str, str] = {}
        if actor_id is not None:
            params["actorId"] = actor_id
        if actor_type is not None:
            params["actorType"] = actor_type
        if action is not None:
            params["action"] = action
        if resource_type is not None:
            params["resourceType"] = resource_type
        if resource_id is not None:
            params["resourceId"] = resource_id
        if result is not None:
            params["result"] = result
        # Free text across action, actor id, resource type and resource id. It
        # narrows *with* the exact-match filters above rather than replacing
        # them.
        if query is not None:
            params["query"] = query
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/orgs/{org_id}/audit-logs", query=params, options=options
        )
        return CursorPage[AuditLogOutput].model_validate(raw)

    def get(
        self, *, org_id: str, log_id: str, options: RequestOptions | None = None
    ) -> AuditLogOutput:
        return AuditLogOutput.model_validate(
            self._client.request("GET", f"/orgs/{org_id}/audit-logs/{log_id}", options=options)
        )

    def export(
        self,
        *,
        org_id: str,
        format: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        query: str | None = None,
        options: RequestOptions | None = None,
    ) -> AuditLogExportOutput:
        payload: dict[str, Any] = {}
        if format is not None:
            payload["format"] = format
        if from_ is not None:
            payload["from"] = from_
        if to is not None:
            payload["to"] = to
        if actor_id is not None:
            payload["actorId"] = actor_id
        if action is not None:
            payload["action"] = action
        if resource_type is not None:
            payload["resourceType"] = resource_type
        # Mirrors the list filter. An export that ignored the active search
        # would hand back rows the screen had just filtered away.
        if query is not None:
            payload["query"] = query
        return AuditLogExportOutput.model_validate(
            self._client.request(
                "POST", f"/orgs/{org_id}/audit-logs/export", payload, options=options
            )
        )


class AsyncAuditResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        org_id: str,
        actor_id: str | None = None,
        actor_type: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        result: str | None = None,
        query: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[AuditLogOutput]:
        params: dict[str, str] = {}
        if actor_id is not None:
            params["actorId"] = actor_id
        if actor_type is not None:
            params["actorType"] = actor_type
        if action is not None:
            params["action"] = action
        if resource_type is not None:
            params["resourceType"] = resource_type
        if resource_id is not None:
            params["resourceId"] = resource_id
        if result is not None:
            params["result"] = result
        # Free text across action, actor id, resource type and resource id. It
        # narrows *with* the exact-match filters above rather than replacing
        # them.
        if query is not None:
            params["query"] = query
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/orgs/{org_id}/audit-logs", query=params, options=options
        )
        return CursorPage[AuditLogOutput].model_validate(raw)

    async def get(
        self, *, org_id: str, log_id: str, options: RequestOptions | None = None
    ) -> AuditLogOutput:
        return AuditLogOutput.model_validate(
            await self._client.request(
                "GET", f"/orgs/{org_id}/audit-logs/{log_id}", options=options
            )
        )

    async def export(
        self,
        *,
        org_id: str,
        format: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        query: str | None = None,
        options: RequestOptions | None = None,
    ) -> AuditLogExportOutput:
        payload: dict[str, Any] = {}
        if format is not None:
            payload["format"] = format
        if from_ is not None:
            payload["from"] = from_
        if to is not None:
            payload["to"] = to
        if actor_id is not None:
            payload["actorId"] = actor_id
        if action is not None:
            payload["action"] = action
        if resource_type is not None:
            payload["resourceType"] = resource_type
        # Mirrors the list filter. An export that ignored the active search
        # would hand back rows the screen had just filtered away.
        if query is not None:
            payload["query"] = query
        return AuditLogExportOutput.model_validate(
            await self._client.request(
                "POST", f"/orgs/{org_id}/audit-logs/export", payload, options=options
            )
        )
