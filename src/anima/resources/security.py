from __future__ import annotations

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import PaginatedResponse, ScannerStatusOutput, SecurityEventOutput


class SecurityResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    # No scan_content. It POSTed to /security/scan, which the API has never
    # served -- scanning runs inside the send paths, not as a callable route.

    def get_scanner_status(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ScannerStatusOutput:
        return ScannerStatusOutput.model_validate(
            self._client.request("GET", f"/orgs/{org_id}/security/scanner-status", options=options)
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
        options: RequestOptions | None = None,
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
        raw = self._client.request(
            "GET", f"/orgs/{org_id}/security/events", query=query, options=options
        )
        return PaginatedResponse[SecurityEventOutput].model_validate(raw)


class AsyncSecurityResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    # No scan_content -- see the sync resource above.

    async def get_scanner_status(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ScannerStatusOutput:
        return ScannerStatusOutput.model_validate(
            await self._client.request(
                "GET", f"/orgs/{org_id}/security/scanner-status", options=options
            )
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
        options: RequestOptions | None = None,
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
        raw = await self._client.request(
            "GET", f"/orgs/{org_id}/security/events", query=query, options=options
        )
        return PaginatedResponse[SecurityEventOutput].model_validate(raw)
