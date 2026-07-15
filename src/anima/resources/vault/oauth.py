from __future__ import annotations

from typing import Any, cast

from ..._http import AsyncHTTPClient, HTTPClient, RequestOptions


class VaultOAuthResource:
    """OAuth sub-resource for managing service connections."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list_apps(
        self, *, category: str | None = None, options: RequestOptions | None = None
    ) -> list[dict[str, Any]]:
        query: dict[str, str] = {}
        if category is not None:
            query["category"] = category
        raw = self._client.request("GET", "/vault/oauth/apps", query=query or None, options=options)
        return cast(list[dict[str, Any]], raw["items"])

    def create_link(
        self,
        *,
        app_slug: str,
        agent_id: str | None = None,
        user_id: str | None = None,
        scopes: list[str] | None = None,
        callback_url: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"appSlug": app_slug}
        if agent_id is not None:
            body["agentId"] = agent_id
        if user_id is not None:
            body["userId"] = user_id
        if scopes is not None:
            body["scopes"] = scopes
        if callback_url is not None:
            body["callbackUrl"] = callback_url
        return cast(
            dict[str, Any],
            self._client.request("POST", "/vault/oauth/link", body, options=options),
        )

    def get_link_status(
        self, token: str, *, options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self._client.request("GET", f"/vault/oauth/link/{token}", options=options),
        )

    def list_accounts(
        self,
        *,
        agent_id: str | None = None,
        user_id: str | None = None,
        app_slug: str | None = None,
        status: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        if user_id is not None:
            query["userId"] = user_id
        if app_slug is not None:
            query["appSlug"] = app_slug
        if status is not None:
            query["status"] = status
        raw = self._client.request(
            "GET", "/vault/oauth/accounts", query=query or None, options=options
        )
        return cast(list[dict[str, Any]], raw["items"])

    def disconnect(
        self,
        account_id: str,
        *,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> None:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        self._client.request(
            "DELETE",
            f"/vault/oauth/accounts/{account_id}",
            query=query or None,
            options=options,
        )


class AsyncVaultOAuthResource:
    """Async OAuth sub-resource for managing service connections."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_apps(
        self, *, category: str | None = None, options: RequestOptions | None = None
    ) -> list[dict[str, Any]]:
        query: dict[str, str] = {}
        if category is not None:
            query["category"] = category
        raw = await self._client.request(
            "GET", "/vault/oauth/apps", query=query or None, options=options
        )
        return cast(list[dict[str, Any]], raw["items"])

    async def create_link(
        self,
        *,
        app_slug: str,
        agent_id: str | None = None,
        user_id: str | None = None,
        scopes: list[str] | None = None,
        callback_url: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"appSlug": app_slug}
        if agent_id is not None:
            body["agentId"] = agent_id
        if user_id is not None:
            body["userId"] = user_id
        if scopes is not None:
            body["scopes"] = scopes
        if callback_url is not None:
            body["callbackUrl"] = callback_url
        return cast(
            dict[str, Any],
            await self._client.request("POST", "/vault/oauth/link", body, options=options),
        )

    async def get_link_status(
        self, token: str, *, options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client.request("GET", f"/vault/oauth/link/{token}", options=options),
        )

    async def list_accounts(
        self,
        *,
        agent_id: str | None = None,
        user_id: str | None = None,
        app_slug: str | None = None,
        status: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        if user_id is not None:
            query["userId"] = user_id
        if app_slug is not None:
            query["appSlug"] = app_slug
        if status is not None:
            query["status"] = status
        raw = await self._client.request(
            "GET", "/vault/oauth/accounts", query=query or None, options=options
        )
        return cast(list[dict[str, Any]], raw["items"])

    async def disconnect(
        self,
        account_id: str,
        *,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> None:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        await self._client.request(
            "DELETE",
            f"/vault/oauth/accounts/{account_id}",
            query=query or None,
            options=options,
        )
