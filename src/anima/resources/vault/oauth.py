from __future__ import annotations

from enum import Enum
from typing import Any

from ..._http import AsyncHTTPClient, HTTPClient, RequestOptions
from ..._types import (
    ConnectedAccount,
    ConnectedAccountStatus,
    ConnectLinkOutput,
    ConnectLinkStatusOutput,
    OAuthAppDefinition,
)


def _accounts_query(
    agent_id: str | None,
    user_id: str | None,
    app_slug: str | None,
    status: ConnectedAccountStatus | str | None,
) -> dict[str, str] | None:
    query: dict[str, str] = {}
    if agent_id is not None:
        query["agentId"] = agent_id
    if user_id is not None:
        query["userId"] = user_id
    if app_slug is not None:
        query["appSlug"] = app_slug
    if status is not None:
        query["status"] = status.value if isinstance(status, Enum) else status
    return query or None


def _link_body(
    app_slug: str,
    agent_id: str | None,
    user_id: str | None,
    scopes: list[str] | None,
    callback_url: str | None,
    custom_app_id: str | None,
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
    if custom_app_id is not None:
        body["customAppId"] = custom_app_id
    return body


class VaultOAuthResource:
    """OAuth sub-resource for managing service connections."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list_apps(
        self, *, category: str | None = None, options: RequestOptions | None = None
    ) -> list[OAuthAppDefinition]:
        """List the services an agent can connect to."""
        query = {"category": category} if category is not None else None
        raw = self._client.request("GET", "/vault/oauth/apps", query=query, options=options)
        return [OAuthAppDefinition.model_validate(item) for item in raw["items"]]

    def get_app(self, slug: str, *, options: RequestOptions | None = None) -> OAuthAppDefinition:
        """Look up a single service by slug (e.g. ``google``, ``github``)."""
        return OAuthAppDefinition.model_validate(
            self._client.request("GET", f"/vault/oauth/apps/{slug}", options=options)
        )

    def create_link(
        self,
        *,
        app_slug: str,
        agent_id: str | None = None,
        user_id: str | None = None,
        scopes: list[str] | None = None,
        callback_url: str | None = None,
        custom_app_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> ConnectLinkOutput:
        """Create a Connect Link -- a hosted auth URL for the user to open."""
        return ConnectLinkOutput.model_validate(
            self._client.request(
                "POST",
                "/vault/oauth/link",
                _link_body(app_slug, agent_id, user_id, scopes, callback_url, custom_app_id),
                options=options,
            )
        )

    def get_link_status(
        self, token: str, *, options: RequestOptions | None = None
    ) -> ConnectLinkStatusOutput:
        """Poll a Connect Link until it reports COMPLETED."""
        return ConnectLinkStatusOutput.model_validate(
            self._client.request("GET", f"/vault/oauth/link/{token}", options=options)
        )

    def list_accounts(
        self,
        *,
        agent_id: str | None = None,
        user_id: str | None = None,
        app_slug: str | None = None,
        status: ConnectedAccountStatus | str | None = None,
        options: RequestOptions | None = None,
    ) -> list[ConnectedAccount]:
        """List established service connections."""
        raw = self._client.request(
            "GET",
            "/vault/oauth/accounts",
            query=_accounts_query(agent_id, user_id, app_slug, status),
            options=options,
        )
        return [ConnectedAccount.model_validate(item) for item in raw["items"]]

    def disconnect(
        self,
        account_id: str,
        *,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> None:
        """Revoke a service connection."""
        query = {"agentId": agent_id} if agent_id is not None else None
        self._client.request(
            "DELETE",
            f"/vault/oauth/accounts/{account_id}",
            query=query,
            options=options,
        )


class AsyncVaultOAuthResource:
    """Async OAuth sub-resource for managing service connections."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_apps(
        self, *, category: str | None = None, options: RequestOptions | None = None
    ) -> list[OAuthAppDefinition]:
        """List the services an agent can connect to."""
        query = {"category": category} if category is not None else None
        raw = await self._client.request("GET", "/vault/oauth/apps", query=query, options=options)
        return [OAuthAppDefinition.model_validate(item) for item in raw["items"]]

    async def get_app(
        self, slug: str, *, options: RequestOptions | None = None
    ) -> OAuthAppDefinition:
        """Look up a single service by slug (e.g. ``google``, ``github``)."""
        return OAuthAppDefinition.model_validate(
            await self._client.request("GET", f"/vault/oauth/apps/{slug}", options=options)
        )

    async def create_link(
        self,
        *,
        app_slug: str,
        agent_id: str | None = None,
        user_id: str | None = None,
        scopes: list[str] | None = None,
        callback_url: str | None = None,
        custom_app_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> ConnectLinkOutput:
        """Create a Connect Link -- a hosted auth URL for the user to open."""
        return ConnectLinkOutput.model_validate(
            await self._client.request(
                "POST",
                "/vault/oauth/link",
                _link_body(app_slug, agent_id, user_id, scopes, callback_url, custom_app_id),
                options=options,
            )
        )

    async def get_link_status(
        self, token: str, *, options: RequestOptions | None = None
    ) -> ConnectLinkStatusOutput:
        """Poll a Connect Link until it reports COMPLETED."""
        return ConnectLinkStatusOutput.model_validate(
            await self._client.request("GET", f"/vault/oauth/link/{token}", options=options)
        )

    async def list_accounts(
        self,
        *,
        agent_id: str | None = None,
        user_id: str | None = None,
        app_slug: str | None = None,
        status: ConnectedAccountStatus | str | None = None,
        options: RequestOptions | None = None,
    ) -> list[ConnectedAccount]:
        """List established service connections."""
        raw = await self._client.request(
            "GET",
            "/vault/oauth/accounts",
            query=_accounts_query(agent_id, user_id, app_slug, status),
            options=options,
        )
        return [ConnectedAccount.model_validate(item) for item in raw["items"]]

    async def disconnect(
        self,
        account_id: str,
        *,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> None:
        """Revoke a service connection."""
        query = {"agentId": agent_id} if agent_id is not None else None
        await self._client.request(
            "DELETE",
            f"/vault/oauth/accounts/{account_id}",
            query=query,
            options=options,
        )
