from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import (
    PaginatedResponse,
    WebhookDeliveryOutput,
    WebhookOutput,
    WebhookTestOutput,
)


def _to_list_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    return params or None


def _to_delivery_query(
    webhook_id: str,
    *,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, str]:
    query: dict[str, str] = {"webhookId": webhook_id}
    if cursor is not None:
        query["cursor"] = cursor
    if limit is not None:
        query["limit"] = str(limit)
    return query


class WebhooksResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        url: str,
        events: list[str],
        description: str | None = None,
        active: bool = True,
        options: RequestOptions | None = None,
    ) -> WebhookOutput:
        body: dict[str, Any] = {"url": url, "events": events, "active": active}
        if description is not None:
            body["description"] = description
        return WebhookOutput.model_validate(self._client.request("POST", "/webhooks", body, options=options))

    def get(self, webhook_id: str, *, options: RequestOptions | None = None) -> WebhookOutput:
        return WebhookOutput.model_validate(self._client.request("GET", f"/webhooks/{webhook_id}", options=options))

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[WebhookOutput]:
        raw = self._client.request(
            "GET", "/webhooks", query=_to_list_query(cursor=cursor, limit=limit), options=options
        )
        return PaginatedResponse[WebhookOutput].model_validate(raw)

    def update(
        self,
        webhook_id: str,
        *,
        url: str | None = None,
        events: list[str] | None = None,
        description: str | None = None,
        active: bool | None = None,
        options: RequestOptions | None = None,
    ) -> WebhookOutput:
        body: dict[str, Any] = {"id": webhook_id}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if description is not None:
            body["description"] = description
        if active is not None:
            body["active"] = active
        return WebhookOutput.model_validate(
            self._client.request("PUT", f"/webhooks/{webhook_id}", body, options=options)
        )

    def delete(self, webhook_id: str, *, options: RequestOptions | None = None) -> None:
        self._client.request("DELETE", f"/webhooks/{webhook_id}", options=options)

    def test(
        self,
        webhook_id: str,
        *,
        event: str | None = None,
        options: RequestOptions | None = None,
    ) -> WebhookTestOutput:
        body: dict[str, Any] = {"id": webhook_id}
        if event is not None:
            body["event"] = event
        return WebhookTestOutput.model_validate(
            self._client.request("POST", f"/webhooks/{webhook_id}/test", body, options=options)
        )

    def list_deliveries(
        self,
        webhook_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[WebhookDeliveryOutput]:
        raw = self._client.request(
            "GET",
            f"/webhooks/{webhook_id}/deliveries",
            query=_to_delivery_query(webhook_id, cursor=cursor, limit=limit),
            options=options,
        )
        return PaginatedResponse[WebhookDeliveryOutput].model_validate(raw)


class AsyncWebhooksResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        url: str,
        events: list[str],
        description: str | None = None,
        active: bool = True,
        options: RequestOptions | None = None,
    ) -> WebhookOutput:
        body: dict[str, Any] = {"url": url, "events": events, "active": active}
        if description is not None:
            body["description"] = description
        return WebhookOutput.model_validate(await self._client.request("POST", "/webhooks", body, options=options))

    async def get(self, webhook_id: str, *, options: RequestOptions | None = None) -> WebhookOutput:
        return WebhookOutput.model_validate(
            await self._client.request("GET", f"/webhooks/{webhook_id}", options=options)
        )

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[WebhookOutput]:
        raw = await self._client.request(
            "GET", "/webhooks", query=_to_list_query(cursor=cursor, limit=limit), options=options
        )
        return PaginatedResponse[WebhookOutput].model_validate(raw)

    async def update(
        self,
        webhook_id: str,
        *,
        url: str | None = None,
        events: list[str] | None = None,
        description: str | None = None,
        active: bool | None = None,
        options: RequestOptions | None = None,
    ) -> WebhookOutput:
        body: dict[str, Any] = {"id": webhook_id}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if description is not None:
            body["description"] = description
        if active is not None:
            body["active"] = active
        return WebhookOutput.model_validate(
            await self._client.request("PUT", f"/webhooks/{webhook_id}", body, options=options)
        )

    async def delete(self, webhook_id: str, *, options: RequestOptions | None = None) -> None:
        await self._client.request("DELETE", f"/webhooks/{webhook_id}", options=options)

    async def test(
        self,
        webhook_id: str,
        *,
        event: str | None = None,
        options: RequestOptions | None = None,
    ) -> WebhookTestOutput:
        body: dict[str, Any] = {"id": webhook_id}
        if event is not None:
            body["event"] = event
        return WebhookTestOutput.model_validate(
            await self._client.request("POST", f"/webhooks/{webhook_id}/test", body, options=options)
        )

    async def list_deliveries(
        self,
        webhook_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[WebhookDeliveryOutput]:
        raw = await self._client.request(
            "GET",
            f"/webhooks/{webhook_id}/deliveries",
            query=_to_delivery_query(webhook_id, cursor=cursor, limit=limit),
            options=options,
        )
        return PaginatedResponse[WebhookDeliveryOutput].model_validate(raw)
