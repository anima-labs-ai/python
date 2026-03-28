from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import OrganizationOutput, PaginatedResponse


def _to_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    query: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if query is not None:
        params["query"] = query
    return params or None


class OrganizationsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        name: str,
        slug: str,
        clerk_org_id: str | None = None,
        tier: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> OrganizationOutput:
        body: dict[str, Any] = {"name": name, "slug": slug}
        if clerk_org_id is not None:
            body["clerkOrgId"] = clerk_org_id
        if tier is not None:
            body["tier"] = tier
        if settings is not None:
            body["settings"] = settings
        return OrganizationOutput.model_validate(
            self._client.request("POST", "/orgs", body)
        )

    def get(self, org_id: str) -> OrganizationOutput:
        return OrganizationOutput.model_validate(
            self._client.request("GET", f"/orgs/{org_id}")
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        query: str | None = None,
    ) -> PaginatedResponse[OrganizationOutput]:
        raw = self._client.request(
            "GET", "/orgs", query=_to_query(cursor=cursor, limit=limit, query=query)
        )
        return PaginatedResponse[OrganizationOutput].model_validate(raw)

    def update(
        self,
        org_id: str,
        *,
        name: str | None = None,
        slug: str | None = None,
        clerk_org_id: str | None = None,
        tier: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> OrganizationOutput:
        body: dict[str, Any] = {"id": org_id}
        if name is not None:
            body["name"] = name
        if slug is not None:
            body["slug"] = slug
        if clerk_org_id is not None:
            body["clerkOrgId"] = clerk_org_id
        if tier is not None:
            body["tier"] = tier
        if settings is not None:
            body["settings"] = settings
        return OrganizationOutput.model_validate(
            self._client.request("PATCH", f"/orgs/{org_id}", body)
        )

    def delete(self, org_id: str) -> None:
        self._client.request("DELETE", f"/orgs/{org_id}")

    def rotate_key(self, org_id: str) -> dict[str, str]:
        raw = self._client.request(
            "POST", f"/orgs/{org_id}/rotate-key", {"id": org_id}
        )
        return {"master_key": raw["masterKey"]}


class AsyncOrganizationsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        name: str,
        slug: str,
        clerk_org_id: str | None = None,
        tier: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> OrganizationOutput:
        body: dict[str, Any] = {"name": name, "slug": slug}
        if clerk_org_id is not None:
            body["clerkOrgId"] = clerk_org_id
        if tier is not None:
            body["tier"] = tier
        if settings is not None:
            body["settings"] = settings
        return OrganizationOutput.model_validate(
            await self._client.request("POST", "/orgs", body)
        )

    async def get(self, org_id: str) -> OrganizationOutput:
        return OrganizationOutput.model_validate(
            await self._client.request("GET", f"/orgs/{org_id}")
        )

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        query: str | None = None,
    ) -> PaginatedResponse[OrganizationOutput]:
        raw = await self._client.request(
            "GET", "/orgs", query=_to_query(cursor=cursor, limit=limit, query=query)
        )
        return PaginatedResponse[OrganizationOutput].model_validate(raw)

    async def update(
        self,
        org_id: str,
        *,
        name: str | None = None,
        slug: str | None = None,
        clerk_org_id: str | None = None,
        tier: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> OrganizationOutput:
        body: dict[str, Any] = {"id": org_id}
        if name is not None:
            body["name"] = name
        if slug is not None:
            body["slug"] = slug
        if clerk_org_id is not None:
            body["clerkOrgId"] = clerk_org_id
        if tier is not None:
            body["tier"] = tier
        if settings is not None:
            body["settings"] = settings
        return OrganizationOutput.model_validate(
            await self._client.request("PATCH", f"/orgs/{org_id}", body)
        )

    async def delete(self, org_id: str) -> None:
        await self._client.request("DELETE", f"/orgs/{org_id}")

    async def rotate_key(self, org_id: str) -> dict[str, str]:
        raw = await self._client.request(
            "POST", f"/orgs/{org_id}/rotate-key", {"id": org_id}
        )
        return {"master_key": raw["masterKey"]}
