"""Tests for VaultOAuthResource.

This resource had no test file. It returned bare ``dict[str, Any]`` for every
call -- no models, no field validation, so a response shape could drift
arbitrarily without anything noticing -- and it was missing ``get_app``
(GET /vault/oauth/apps/{slug}), which the go SDK has had all along.

Note the envelope asymmetry pinned below: these routes DO return an ``items``
envelope, while GET /agents/{id}/credentials returns a bare array. Both live in
this SDK; see tests/test_identity.py.

Source of truth, at the commit pinned in .anima-ref:
  packages/contracts/src/schemas/vault.ts
  packages/contracts/src/contracts/vault.ts
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import (
    ConnectedAccountStatus,
    ConnectLinkStatus,
    OAuthAuthMethod,
)
from anima.resources.vault.oauth import AsyncVaultOAuthResource, VaultOAuthResource

OAUTH_APP_RAW: dict[str, Any] = {
    "id": "app_001",
    "slug": "github",
    "name": "GitHub",
    "description": "Code hosting",
    "iconUrl": "https://cdn.useanima.sh/github.svg",
    "authMethod": "OAUTH2_PKCE",
    "defaultScopes": ["repo", "read:user"],
    "requiresPkce": True,
    "category": "developer",
    "isManaged": True,
    "isActive": True,
}

CONNECTED_ACCOUNT_RAW: dict[str, Any] = {
    "id": "acct_001",
    "agentId": "agent_001",
    "userId": None,
    "appDefinitionId": "app_001",
    "appSlug": "github",
    "appName": "GitHub",
    "appIconUrl": None,
    "customAppId": None,
    "grantedScopes": ["repo"],
    "accountLabel": "work",
    "accountEmail": "dev@example.com",
    "status": "ACTIVE",
    "statusMessage": None,
    "tokenExpiresAt": "2026-08-01T00:00:00Z",
    "lastRefreshedAt": None,
    "createdAt": "2026-07-31T00:00:00Z",
    "updatedAt": "2026-07-31T00:00:00Z",
}


class TestListApps:
    def test_unwraps_the_items_envelope(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"items": [OAUTH_APP_RAW]}
        result = VaultOAuthResource(mock_http).list_apps()

        mock_http.request.assert_called_once_with(
            "GET", "/vault/oauth/apps", query=None, options=None
        )
        assert result[0].slug == "github"
        assert result[0].auth_method is OAuthAuthMethod.OAUTH2_PKCE
        assert result[0].requires_pkce is True

    def test_filters_by_category(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"items": []}
        VaultOAuthResource(mock_http).list_apps(category="developer")

        assert mock_http.request.call_args.kwargs["query"] == {"category": "developer"}


class TestGetApp:
    def test_gets_a_single_app_by_slug(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = OAUTH_APP_RAW
        result = VaultOAuthResource(mock_http).get_app("github")

        mock_http.request.assert_called_once_with("GET", "/vault/oauth/apps/github", options=None)
        assert result.name == "GitHub"
        assert result.default_scopes == ["repo", "read:user"]

    @pytest.mark.asyncio()
    async def test_async(self) -> None:
        client = AsyncMock(spec=AsyncHTTPClient)
        client.request.return_value = OAUTH_APP_RAW
        result = await AsyncVaultOAuthResource(client).get_app("github")

        assert client.request.call_args[0][1] == "/vault/oauth/apps/github"
        assert result.slug == "github"


class TestCreateLink:
    def test_sends_only_what_was_set(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "linkUrl": "https://connect.useanima.sh/l/tok_1",
            "token": "tok_1",
            "expiresAt": "2026-07-31T00:10:00Z",
        }
        result = VaultOAuthResource(mock_http).create_link(app_slug="github")

        mock_http.request.assert_called_once_with(
            "POST", "/vault/oauth/link", {"appSlug": "github"}, options=None
        )
        assert result.token == "tok_1"

    def test_passes_every_optional_through(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "linkUrl": "https://connect.useanima.sh/l/tok_1",
            "token": "tok_1",
            "expiresAt": "2026-07-31T00:10:00Z",
        }
        VaultOAuthResource(mock_http).create_link(
            app_slug="github",
            agent_id="agent_001",
            user_id="user_9",
            scopes=["repo"],
            callback_url="https://example.com/done",
            custom_app_id="custom_1",
        )

        assert mock_http.request.call_args[0][2] == {
            "appSlug": "github",
            "agentId": "agent_001",
            "userId": "user_9",
            "scopes": ["repo"],
            "callbackUrl": "https://example.com/done",
            "customAppId": "custom_1",
        }


class TestGetLinkStatus:
    def test_parses_status(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "status": "COMPLETED",
            "connectedAccountId": "acct_001",
        }
        result = VaultOAuthResource(mock_http).get_link_status("tok_1")

        mock_http.request.assert_called_once_with("GET", "/vault/oauth/link/tok_1", options=None)
        assert result.status is ConnectLinkStatus.COMPLETED
        assert result.connected_account_id == "acct_001"

    def test_pending_has_no_account(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"status": "PENDING", "connectedAccountId": None}
        result = VaultOAuthResource(mock_http).get_link_status("tok_1")

        assert result.connected_account_id is None


class TestListAccounts:
    def test_unwraps_the_items_envelope(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"items": [CONNECTED_ACCOUNT_RAW]}
        result = VaultOAuthResource(mock_http).list_accounts()

        mock_http.request.assert_called_once_with(
            "GET", "/vault/oauth/accounts", query=None, options=None
        )
        assert result[0].status is ConnectedAccountStatus.ACTIVE
        assert result[0].granted_scopes == ["repo"]

    def test_status_enum_is_sent_as_its_wire_value(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"items": []}
        VaultOAuthResource(mock_http).list_accounts(
            agent_id="agent_001", status=ConnectedAccountStatus.EXPIRED
        )

        assert mock_http.request.call_args.kwargs["query"] == {
            "agentId": "agent_001",
            "status": "EXPIRED",
        }


class TestDisconnect:
    def test_deletes_the_account(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"success": True}
        VaultOAuthResource(mock_http).disconnect("acct_001")

        mock_http.request.assert_called_once_with(
            "DELETE", "/vault/oauth/accounts/acct_001", query=None, options=None
        )

    @pytest.mark.asyncio()
    async def test_async_scopes_to_an_agent(self) -> None:
        client = AsyncMock(spec=AsyncHTTPClient)
        client.request.return_value = {"success": True}
        await AsyncVaultOAuthResource(client).disconnect("acct_001", agent_id="agent_001")

        assert client.request.call_args.kwargs["query"] == {"agentId": "agent_001"}
