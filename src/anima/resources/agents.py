from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import AgentOutput, PaginatedResponse


def _to_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    org_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if org_id is not None:
        params["orgId"] = org_id
    if status is not None:
        params["status"] = status
    if query is not None:
        params["query"] = query
    return params or None


class AgentsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        org_id: str,
        name: str,
        slug: str,
        email: str | None = None,
        provision_phone: bool | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> AgentOutput:
        body: dict[str, Any] = {"orgId": org_id, "name": name, "slug": slug}
        if email is not None:
            body["email"] = email
        if provision_phone is not None:
            body["provisionPhone"] = provision_phone
        if metadata is not None:
            body["metadata"] = metadata
        return AgentOutput.model_validate(
            self._client.request("POST", "/agents", body, options=options)
        )

    def get(self, agent_id: str, *, options: RequestOptions | None = None) -> AgentOutput:
        return AgentOutput.model_validate(
            self._client.request("GET", f"/agents/{agent_id}", options=options)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        org_id: str | None = None,
        status: str | None = None,
        query: str | None = None,
    ) -> SyncPageIterator[AgentOutput]:
        def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            org_id: str | None = org_id,
            status: str | None = status,
            query: str | None = query,
        ) -> PaginatedResponse[AgentOutput]:
            raw = self._client.request(
                "GET",
                "/agents",
                query=_to_query(
                    cursor=cursor, limit=limit, org_id=org_id, status=status, query=query
                ),
            )
            return PaginatedResponse[AgentOutput].model_validate(raw)

        return SyncPageIterator(
            _fetch, cursor=cursor, limit=limit, org_id=org_id, status=status, query=query
        )

    def update(
        self,
        agent_id: str,
        *,
        name: str | None = None,
        slug: str | None = None,
        status: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> AgentOutput:
        body: dict[str, Any] = {"id": agent_id}
        if name is not None:
            body["name"] = name
        if slug is not None:
            body["slug"] = slug
        if status is not None:
            body["status"] = status
        if metadata is not None:
            body["metadata"] = metadata
        return AgentOutput.model_validate(
            self._client.request("PATCH", f"/agents/{agent_id}", body, options=options)
        )

    def delete(self, agent_id: str, *, options: RequestOptions | None = None) -> None:
        self._client.request("DELETE", f"/agents/{agent_id}", options=options)

    def rotate_key(self, agent_id: str, *, options: RequestOptions | None = None) -> dict[str, str]:
        raw = self._client.request(
            "POST", f"/agents/{agent_id}/rotate-key", {"id": agent_id}, options=options
        )
        return {"api_key": raw["apiKey"], "api_key_prefix": raw["apiKeyPrefix"]}


class AsyncAgentsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        org_id: str,
        name: str,
        slug: str,
        email: str | None = None,
        provision_phone: bool | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> AgentOutput:
        body: dict[str, Any] = {"orgId": org_id, "name": name, "slug": slug}
        if email is not None:
            body["email"] = email
        if provision_phone is not None:
            body["provisionPhone"] = provision_phone
        if metadata is not None:
            body["metadata"] = metadata
        return AgentOutput.model_validate(
            await self._client.request("POST", "/agents", body, options=options)
        )

    async def get(self, agent_id: str, *, options: RequestOptions | None = None) -> AgentOutput:
        return AgentOutput.model_validate(
            await self._client.request("GET", f"/agents/{agent_id}", options=options)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        org_id: str | None = None,
        status: str | None = None,
        query: str | None = None,
    ) -> AsyncPageIterator[AgentOutput]:
        async def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            org_id: str | None = org_id,
            status: str | None = status,
            query: str | None = query,
        ) -> PaginatedResponse[AgentOutput]:
            raw = await self._client.request(
                "GET",
                "/agents",
                query=_to_query(
                    cursor=cursor, limit=limit, org_id=org_id, status=status, query=query
                ),
            )
            return PaginatedResponse[AgentOutput].model_validate(raw)

        return AsyncPageIterator(
            _fetch, cursor=cursor, limit=limit, org_id=org_id, status=status, query=query
        )

    async def update(
        self,
        agent_id: str,
        *,
        name: str | None = None,
        slug: str | None = None,
        status: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> AgentOutput:
        body: dict[str, Any] = {"id": agent_id}
        if name is not None:
            body["name"] = name
        if slug is not None:
            body["slug"] = slug
        if status is not None:
            body["status"] = status
        if metadata is not None:
            body["metadata"] = metadata
        return AgentOutput.model_validate(
            await self._client.request("PATCH", f"/agents/{agent_id}", body, options=options)
        )

    async def delete(self, agent_id: str, *, options: RequestOptions | None = None) -> None:
        await self._client.request("DELETE", f"/agents/{agent_id}", options=options)

    async def rotate_key(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> dict[str, str]:
        raw = await self._client.request(
            "POST", f"/agents/{agent_id}/rotate-key", {"id": agent_id}, options=options
        )
        return {"api_key": raw["apiKey"], "api_key_prefix": raw["apiKeyPrefix"]}
