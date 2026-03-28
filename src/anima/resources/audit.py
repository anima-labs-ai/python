from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import AuditLogExportOutput, AuditLogOutput, PaginatedResponse


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
        from_: str | None = None,
        to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[AuditLogOutput]:
        query: dict[str, str] = {}
        if actor_id is not None:
            query["actorId"] = actor_id
        if actor_type is not None:
            query["actorType"] = actor_type
        if action is not None:
            query["action"] = action
        if resource_type is not None:
            query["resourceType"] = resource_type
        if resource_id is not None:
            query["resourceId"] = resource_id
        if result is not None:
            query["result"] = result
        if from_ is not None:
            query["from"] = from_
        if to is not None:
            query["to"] = to
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/v1/orgs/{org_id}/audit/logs", query=query
        )
        return PaginatedResponse[AuditLogOutput].model_validate(raw)

    def get(self, *, org_id: str, log_id: str) -> AuditLogOutput:
        return AuditLogOutput.model_validate(
            self._client.request("GET", f"/v1/orgs/{org_id}/audit/logs/{log_id}")
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
        return AuditLogExportOutput.model_validate(
            self._client.request("POST", f"/v1/orgs/{org_id}/audit/export", payload)
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
        from_: str | None = None,
        to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[AuditLogOutput]:
        query: dict[str, str] = {}
        if actor_id is not None:
            query["actorId"] = actor_id
        if actor_type is not None:
            query["actorType"] = actor_type
        if action is not None:
            query["action"] = action
        if resource_type is not None:
            query["resourceType"] = resource_type
        if resource_id is not None:
            query["resourceId"] = resource_id
        if result is not None:
            query["result"] = result
        if from_ is not None:
            query["from"] = from_
        if to is not None:
            query["to"] = to
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/v1/orgs/{org_id}/audit/logs", query=query
        )
        return PaginatedResponse[AuditLogOutput].model_validate(raw)

    async def get(self, *, org_id: str, log_id: str) -> AuditLogOutput:
        return AuditLogOutput.model_validate(
            await self._client.request("GET", f"/v1/orgs/{org_id}/audit/logs/{log_id}")
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
        return AuditLogExportOutput.model_validate(
            await self._client.request(
                "POST", f"/v1/orgs/{org_id}/audit/export", payload
            )
        )
