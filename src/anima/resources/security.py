from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import PaginatedResponse, SecurityEventOutput, SecurityScanOutput


class SecurityResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def scan_content(
        self,
        *,
        org_id: str,
        channel: str,
        body: str,
        agent_id: str | None = None,
        subject: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityScanOutput:
        payload: dict[str, Any] = {"orgId": org_id, "channel": channel, "body": body}
        if agent_id is not None:
            payload["agentId"] = agent_id
        if subject is not None:
            payload["subject"] = subject
        if metadata is not None:
            payload["metadata"] = metadata
        return SecurityScanOutput.model_validate(
            self._client.request("POST", "/security/scan", payload)
        )

    def list_events(
        self,
        *,
        org_id: str,
        agent_id: str | None = None,
        type: str | None = None,
        severity: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[SecurityEventOutput]:
        query: dict[str, str] = {"orgId": org_id}
        if agent_id is not None:
            query["agentId"] = agent_id
        if type is not None:
            query["type"] = type
        if severity is not None:
            query["severity"] = severity
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request("GET", f"/v1/orgs/{org_id}/security/events", query=query)
        return PaginatedResponse[SecurityEventOutput].model_validate(raw)


class AsyncSecurityResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def scan_content(
        self,
        *,
        org_id: str,
        channel: str,
        body: str,
        agent_id: str | None = None,
        subject: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityScanOutput:
        payload: dict[str, Any] = {"orgId": org_id, "channel": channel, "body": body}
        if agent_id is not None:
            payload["agentId"] = agent_id
        if subject is not None:
            payload["subject"] = subject
        if metadata is not None:
            payload["metadata"] = metadata
        return SecurityScanOutput.model_validate(
            await self._client.request("POST", "/security/scan", payload)
        )

    async def list_events(
        self,
        *,
        org_id: str,
        agent_id: str | None = None,
        type: str | None = None,
        severity: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[SecurityEventOutput]:
        query: dict[str, str] = {"orgId": org_id}
        if agent_id is not None:
            query["agentId"] = agent_id
        if type is not None:
            query["type"] = type
        if severity is not None:
            query["severity"] = severity
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request("GET", f"/v1/orgs/{org_id}/security/events", query=query)
        return PaginatedResponse[SecurityEventOutput].model_validate(raw)
