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


class PhonesResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

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

    def get(self, phone_id: str) -> PhoneIdentityOutput:
        return PhoneIdentityOutput.model_validate(
            self._client.request("GET", f"/phones/{phone_id}")
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> list[PhoneIdentityOutput]:
        if agent_id is not None:
            raw = self._client.request(
                "GET", "/phone/numbers", query={"agentId": agent_id}
            )
        else:
            raw = self._client.request(
                "GET",
                "/phones",
                query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id),
            )
        return [PhoneIdentityOutput.model_validate(item) for item in raw["items"]]

    def release(self, phone_id: str) -> None:
        self._client.request("DELETE", f"/phones/{phone_id}")

    def update_config(
        self,
        phone_id: str,
        *,
        is_primary: bool | None = None,
        ten_dlc_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PhoneIdentityOutput:
        body: dict[str, Any] = {}
        if is_primary is not None:
            body["isPrimary"] = is_primary
        if ten_dlc_status is not None:
            body["tenDlcStatus"] = ten_dlc_status
        if metadata is not None:
            body["metadata"] = metadata
        return PhoneIdentityOutput.model_validate(
            self._client.request("PATCH", f"/phones/{phone_id}", body)
        )


class AsyncPhonesResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

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

    async def get(self, phone_id: str) -> PhoneIdentityOutput:
        return PhoneIdentityOutput.model_validate(
            await self._client.request("GET", f"/phones/{phone_id}")
        )

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> list[PhoneIdentityOutput]:
        if agent_id is not None:
            raw = await self._client.request(
                "GET", "/phone/numbers", query={"agentId": agent_id}
            )
        else:
            raw = await self._client.request(
                "GET",
                "/phones",
                query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id),
            )
        return [PhoneIdentityOutput.model_validate(item) for item in raw["items"]]

    async def release(self, phone_id: str) -> None:
        await self._client.request("DELETE", f"/phones/{phone_id}")

    async def update_config(
        self,
        phone_id: str,
        *,
        is_primary: bool | None = None,
        ten_dlc_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PhoneIdentityOutput:
        body: dict[str, Any] = {}
        if is_primary is not None:
            body["isPrimary"] = is_primary
        if ten_dlc_status is not None:
            body["tenDlcStatus"] = ten_dlc_status
        if metadata is not None:
            body["metadata"] = metadata
        return PhoneIdentityOutput.model_validate(
            await self._client.request("PATCH", f"/phones/{phone_id}", body)
        )
