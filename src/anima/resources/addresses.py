from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import AddressOutput, ValidateAddressOutput


def _to_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    agent_id: str | None = None,
    type: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if agent_id is not None:
        params["agentId"] = agent_id
    if type is not None:
        params["type"] = type
    return params or None


def _build_create_body(
    *,
    agent_id: str,
    type: str,
    label: str | None = None,
    street1: str,
    street2: str | None = None,
    city: str,
    state: str,
    postal_code: str,
    country: str,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "agentId": agent_id,
        "type": type,
        "street1": street1,
        "city": city,
        "state": state,
        "postalCode": postal_code,
        "country": country,
    }
    if label is not None:
        body["label"] = label
    if street2 is not None:
        body["street2"] = street2
    return body


def _build_update_body(
    *,
    agent_id: str,
    type: str | None = None,
    label: str | None = None,
    street1: str | None = None,
    street2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postal_code: str | None = None,
    country: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"agentId": agent_id}
    if type is not None:
        body["type"] = type
    if label is not None:
        body["label"] = label
    if street1 is not None:
        body["street1"] = street1
    if street2 is not None:
        body["street2"] = street2
    if city is not None:
        body["city"] = city
    if state is not None:
        body["state"] = state
    if postal_code is not None:
        body["postalCode"] = postal_code
    if country is not None:
        body["country"] = country
    return body


class AddressesResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        agent_id: str,
        type: str,
        label: str | None = None,
        street1: str,
        street2: str | None = None,
        city: str,
        state: str,
        postal_code: str,
        country: str,
        options: RequestOptions | None = None,
    ) -> AddressOutput:
        body = _build_create_body(
            agent_id=agent_id,
            type=type,
            label=label,
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        return AddressOutput.model_validate(self._client.request("POST", "/addresses", body, options=options))

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
        type: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[AddressOutput]:
        raw = self._client.request(
            "GET",
            "/addresses",
            query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id, type=type),
            options=options,
        )
        return [AddressOutput.model_validate(item) for item in raw["items"]]

    def get(self, address_id: str, *, agent_id: str, options: RequestOptions | None = None) -> AddressOutput:
        return AddressOutput.model_validate(
            self._client.request(
                "GET",
                f"/addresses/{address_id}",
                query={"agentId": agent_id},
                options=options,
            )
        )

    def update(
        self,
        address_id: str,
        *,
        agent_id: str,
        type: str | None = None,
        label: str | None = None,
        street1: str | None = None,
        street2: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        country: str | None = None,
        options: RequestOptions | None = None,
    ) -> AddressOutput:
        body = _build_update_body(
            agent_id=agent_id,
            type=type,
            label=label,
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        return AddressOutput.model_validate(
            self._client.request("PUT", f"/addresses/{address_id}", body, options=options)
        )

    def delete(self, address_id: str, *, agent_id: str, options: RequestOptions | None = None) -> None:
        self._client.request("DELETE", f"/addresses/{address_id}", {"agentId": agent_id}, options=options)

    def validate(self, address_id: str, *, agent_id: str, options: RequestOptions | None = None) -> ValidateAddressOutput:
        return ValidateAddressOutput.model_validate(
            self._client.request("POST", f"/addresses/{address_id}/validate", {"agentId": agent_id}, options=options)
        )


class AsyncAddressesResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        agent_id: str,
        type: str,
        label: str | None = None,
        street1: str,
        street2: str | None = None,
        city: str,
        state: str,
        postal_code: str,
        country: str,
        options: RequestOptions | None = None,
    ) -> AddressOutput:
        body = _build_create_body(
            agent_id=agent_id,
            type=type,
            label=label,
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        return AddressOutput.model_validate(await self._client.request("POST", "/addresses", body, options=options))

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
        type: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[AddressOutput]:
        raw = await self._client.request(
            "GET",
            "/addresses",
            query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id, type=type),
            options=options,
        )
        return [AddressOutput.model_validate(item) for item in raw["items"]]

    async def get(self, address_id: str, *, agent_id: str, options: RequestOptions | None = None) -> AddressOutput:
        return AddressOutput.model_validate(
            await self._client.request(
                "GET",
                f"/addresses/{address_id}",
                query={"agentId": agent_id},
                options=options,
            )
        )

    async def update(
        self,
        address_id: str,
        *,
        agent_id: str,
        type: str | None = None,
        label: str | None = None,
        street1: str | None = None,
        street2: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        country: str | None = None,
        options: RequestOptions | None = None,
    ) -> AddressOutput:
        body = _build_update_body(
            agent_id=agent_id,
            type=type,
            label=label,
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        return AddressOutput.model_validate(
            await self._client.request("PUT", f"/addresses/{address_id}", body, options=options)
        )

    async def delete(self, address_id: str, *, agent_id: str, options: RequestOptions | None = None) -> None:
        await self._client.request("DELETE", f"/addresses/{address_id}", {"agentId": agent_id}, options=options)

    async def validate(self, address_id: str, *, agent_id: str, options: RequestOptions | None = None) -> ValidateAddressOutput:
        return ValidateAddressOutput.model_validate(
            await self._client.request(
                "POST", f"/addresses/{address_id}/validate", {"agentId": agent_id}, options=options
            )
        )
