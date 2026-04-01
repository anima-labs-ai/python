from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import PhoneIdentityOutput, PhoneProvisionOutput


def _to_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    agent_id: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if agent_id is not None:
        params["agentId"] = agent_id
    return params or None


def _to_search_query(
    *,
    country_code: str | None = None,
    area_code: str | None = None,
    capabilities: list[str] | None = None,
    limit: int | None = None,
) -> dict[str, Any] | None:
    params: dict[str, Any] = {}
    if country_code is not None:
        params["countryCode"] = country_code
    if area_code is not None:
        params["areaCode"] = area_code
    if capabilities is not None:
        params["capabilities[]"] = capabilities
    if limit is not None:
        params["limit"] = str(limit)
    return params or None


class PhonesResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def search(
        self,
        *,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._client.request(
            "GET",
            "/phone/search",
            query=_to_search_query(
                country_code=country_code,
                area_code=area_code,
                capabilities=capabilities,
                limit=limit,
            ),
        )

    def provision(
        self,
        *,
        agent_id: str,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
    ) -> PhoneProvisionOutput:
        body: dict[str, Any] = {"agentId": agent_id}
        if country_code is not None:
            body["countryCode"] = country_code
        if area_code is not None:
            body["areaCode"] = area_code
        if capabilities is not None:
            body["capabilities"] = capabilities
        return PhoneProvisionOutput.model_validate(
            self._client.request("POST", "/phone/provision", body)
        )

    def list(
        self,
        *,
        agent_id: str,
    ) -> list[PhoneIdentityOutput]:
        raw = self._client.request("GET", "/phone/numbers", query={"agentId": agent_id})
        return [PhoneIdentityOutput.model_validate(item) for item in raw["items"]]

    def release(
        self,
        *,
        agent_id: str,
        phone_number: str,
    ) -> dict[str, Any]:
        return self._client.request(
            "POST",
            "/phone/release",
            {"agentId": agent_id, "phoneNumber": phone_number},
        )



class AsyncPhonesResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def search(
        self,
        *,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._client.request(
            "GET",
            "/phone/search",
            query=_to_search_query(
                country_code=country_code,
                area_code=area_code,
                capabilities=capabilities,
                limit=limit,
            ),
        )

    async def provision(
        self,
        *,
        agent_id: str,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
    ) -> PhoneProvisionOutput:
        body: dict[str, Any] = {"agentId": agent_id}
        if country_code is not None:
            body["countryCode"] = country_code
        if area_code is not None:
            body["areaCode"] = area_code
        if capabilities is not None:
            body["capabilities"] = capabilities
        return PhoneProvisionOutput.model_validate(
            await self._client.request("POST", "/phone/provision", body)
        )

    async def list(
        self,
        *,
        agent_id: str,
    ) -> list[PhoneIdentityOutput]:
        raw = await self._client.request("GET", "/phone/numbers", query={"agentId": agent_id})
        return [PhoneIdentityOutput.model_validate(item) for item in raw["items"]]

    async def release(
        self,
        *,
        agent_id: str,
        phone_number: str,
    ) -> dict[str, Any]:
        return await self._client.request(
            "POST",
            "/phone/release",
            {"agentId": agent_id, "phoneNumber": phone_number},
        )

