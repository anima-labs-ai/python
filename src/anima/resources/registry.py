from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import RegistryAgentOutput


def _to_search_query(
    *,
    q: str,
    category: str | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, str]:
    params: dict[str, str] = {"q": q}
    if category is not None:
        params["category"] = category
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    return params


def _build_register_body(
    *,
    did: str,
    name: str,
    description: str | None = None,
    category: str | None = None,
    capabilities: list[str] | None = None,
    endpoints: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"did": did, "name": name}
    if description is not None:
        body["description"] = description
    if category is not None:
        body["category"] = category
    if capabilities is not None:
        body["capabilities"] = capabilities
    if endpoints is not None:
        body["endpoints"] = endpoints
    if metadata is not None:
        body["metadata"] = metadata
    return body


def _build_update_body(
    *,
    name: str | None = None,
    description: str | None = None,
    category: str | None = None,
    capabilities: list[str] | None = None,
    endpoints: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if category is not None:
        body["category"] = category
    if capabilities is not None:
        body["capabilities"] = capabilities
    if endpoints is not None:
        body["endpoints"] = endpoints
    if metadata is not None:
        body["metadata"] = metadata
    return body


class RegistryResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def register(
        self,
        *,
        did: str,
        name: str,
        description: str | None = None,
        category: str | None = None,
        capabilities: list[str] | None = None,
        endpoints: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RegistryAgentOutput:
        body = _build_register_body(
            did=did,
            name=name,
            description=description,
            category=category,
            capabilities=capabilities,
            endpoints=endpoints,
            metadata=metadata,
        )
        return RegistryAgentOutput.model_validate(
            self._client.request("POST", "/registry/agents", body)
        )

    def search(
        self,
        query: str,
        *,
        category: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> list[RegistryAgentOutput]:
        params = _to_search_query(q=query, category=category, cursor=cursor, limit=limit)
        raw = self._client.request("GET", "/registry/agents/search", query=params)
        return [RegistryAgentOutput.model_validate(item) for item in raw["items"]]

    def lookup(self, did: str) -> RegistryAgentOutput:
        return RegistryAgentOutput.model_validate(
            self._client.request("GET", f"/registry/agents/{did}")
        )

    def update(
        self,
        did: str,
        *,
        name: str | None = None,
        description: str | None = None,
        category: str | None = None,
        capabilities: list[str] | None = None,
        endpoints: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RegistryAgentOutput:
        body = _build_update_body(
            name=name,
            description=description,
            category=category,
            capabilities=capabilities,
            endpoints=endpoints,
            metadata=metadata,
        )
        return RegistryAgentOutput.model_validate(
            self._client.request("PUT", f"/registry/agents/{did}", body)
        )

    def unlist(self, did: str) -> None:
        self._client.request("DELETE", f"/registry/agents/{did}")


class AsyncRegistryResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def register(
        self,
        *,
        did: str,
        name: str,
        description: str | None = None,
        category: str | None = None,
        capabilities: list[str] | None = None,
        endpoints: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RegistryAgentOutput:
        body = _build_register_body(
            did=did,
            name=name,
            description=description,
            category=category,
            capabilities=capabilities,
            endpoints=endpoints,
            metadata=metadata,
        )
        return RegistryAgentOutput.model_validate(
            await self._client.request("POST", "/registry/agents", body)
        )

    async def search(
        self,
        query: str,
        *,
        category: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> list[RegistryAgentOutput]:
        params = _to_search_query(q=query, category=category, cursor=cursor, limit=limit)
        raw = await self._client.request("GET", "/registry/agents/search", query=params)
        return [RegistryAgentOutput.model_validate(item) for item in raw["items"]]

    async def lookup(self, did: str) -> RegistryAgentOutput:
        return RegistryAgentOutput.model_validate(
            await self._client.request("GET", f"/registry/agents/{did}")
        )

    async def update(
        self,
        did: str,
        *,
        name: str | None = None,
        description: str | None = None,
        category: str | None = None,
        capabilities: list[str] | None = None,
        endpoints: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RegistryAgentOutput:
        body = _build_update_body(
            name=name,
            description=description,
            category=category,
            capabilities=capabilities,
            endpoints=endpoints,
            metadata=metadata,
        )
        return RegistryAgentOutput.model_validate(
            await self._client.request("PUT", f"/registry/agents/{did}", body)
        )

    async def unlist(self, did: str) -> None:
        await self._client.request("DELETE", f"/registry/agents/{did}")
