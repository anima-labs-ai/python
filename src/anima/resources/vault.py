from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import (
    VaultCredential,
    VaultIdentityOutput,
    VaultRevokeTokensResult,
    VaultShare,
    VaultStatusOutput,
    VaultTokenOutput,
    VaultTotpOutput,
)


class VaultOAuthResource:
    """OAuth sub-resource for managing service connections."""

    def __init__(self, client: "HTTPClient") -> None:
        self._client = client

    def list_apps(
        self, *, category: str | None = None, options: "RequestOptions | None" = None
    ) -> list[dict[str, Any]]:
        query: dict[str, str] = {}
        if category is not None:
            query["category"] = category
        raw = self._client.request("GET", "/vault/oauth/apps", query=query or None, options=options)
        return raw["items"]

    def create_link(
        self,
        *,
        app_slug: str,
        agent_id: str | None = None,
        user_id: str | None = None,
        scopes: list[str] | None = None,
        callback_url: str | None = None,
        options: "RequestOptions | None" = None,
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
        return self._client.request("POST", "/vault/oauth/link", body, options=options)

    def get_link_status(
        self, token: str, *, options: "RequestOptions | None" = None
    ) -> dict[str, Any]:
        return self._client.request("GET", f"/vault/oauth/link/{token}", options=options)

    def list_accounts(
        self,
        *,
        agent_id: str | None = None,
        user_id: str | None = None,
        app_slug: str | None = None,
        status: str | None = None,
        options: "RequestOptions | None" = None,
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
        raw = self._client.request("GET", "/vault/oauth/accounts", query=query or None, options=options)
        return raw["items"]

    def disconnect(
        self, account_id: str, *, agent_id: str | None = None, options: "RequestOptions | None" = None
    ) -> None:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        self._client.request("DELETE", f"/vault/oauth/accounts/{account_id}", query=query or None, options=options)


class AsyncVaultOAuthResource:
    """Async OAuth sub-resource for managing service connections."""

    def __init__(self, client: "AsyncHTTPClient") -> None:
        self._client = client

    async def list_apps(
        self, *, category: str | None = None, options: "RequestOptions | None" = None
    ) -> list[dict[str, Any]]:
        query: dict[str, str] = {}
        if category is not None:
            query["category"] = category
        raw = await self._client.request("GET", "/vault/oauth/apps", query=query or None, options=options)
        return raw["items"]

    async def create_link(
        self,
        *,
        app_slug: str,
        agent_id: str | None = None,
        user_id: str | None = None,
        scopes: list[str] | None = None,
        callback_url: str | None = None,
        options: "RequestOptions | None" = None,
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
        return await self._client.request("POST", "/vault/oauth/link", body, options=options)

    async def get_link_status(
        self, token: str, *, options: "RequestOptions | None" = None
    ) -> dict[str, Any]:
        return await self._client.request("GET", f"/vault/oauth/link/{token}", options=options)

    async def list_accounts(
        self,
        *,
        agent_id: str | None = None,
        user_id: str | None = None,
        app_slug: str | None = None,
        status: str | None = None,
        options: "RequestOptions | None" = None,
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
        raw = await self._client.request("GET", "/vault/oauth/accounts", query=query or None, options=options)
        return raw["items"]

    async def disconnect(
        self, account_id: str, *, agent_id: str | None = None, options: "RequestOptions | None" = None
    ) -> None:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        await self._client.request("DELETE", f"/vault/oauth/accounts/{account_id}", query=query or None, options=options)


class VaultResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    @property
    def oauth(self) -> VaultOAuthResource:
        return VaultOAuthResource(self._client)

    def provision(
        self, *, agent_id: str, options: RequestOptions | None = None
    ) -> VaultIdentityOutput:
        return VaultIdentityOutput.model_validate(
            self._client.request("POST", "/vault/provision", {"agentId": agent_id}, options=options)
        )

    def deprovision(self, *, agent_id: str, options: RequestOptions | None = None) -> None:
        self._client.request("POST", "/vault/deprovision", {"agentId": agent_id}, options=options)

    def list_credentials(
        self,
        *,
        agent_id: str,
        type: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[VaultCredential]:
        query: dict[str, str] = {"agentId": agent_id}
        if type is not None:
            query["type"] = type
        raw = self._client.request("GET", "/vault/credentials", query=query, options=options)
        return [VaultCredential.model_validate(item) for item in raw["items"]]

    def get_credential(
        self, credential_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredential:
        return VaultCredential.model_validate(
            self._client.request("GET", f"/vault/credentials/{credential_id}", options=options)
        )

    def create_credential(
        self,
        *,
        agent_id: str,
        type: str,
        name: str,
        notes: str | None = None,
        login: dict[str, Any] | None = None,
        card: dict[str, Any] | None = None,
        identity: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool = False,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        body: dict[str, Any] = {
            "agentId": agent_id,
            "type": type,
            "name": name,
            "favorite": favorite,
        }
        if notes is not None:
            body["notes"] = notes
        if login is not None:
            body["login"] = login
        if card is not None:
            body["card"] = card
        if identity is not None:
            body["identity"] = identity
        if fields is not None:
            body["fields"] = fields
        return VaultCredential.model_validate(
            self._client.request("POST", "/vault/credentials", body, options=options)
        )

    def update_credential(
        self,
        credential_id: str,
        *,
        name: str | None = None,
        notes: str | None = None,
        login: dict[str, Any] | None = None,
        card: dict[str, Any] | None = None,
        identity: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if notes is not None:
            body["notes"] = notes
        if login is not None:
            body["login"] = login
        if card is not None:
            body["card"] = card
        if identity is not None:
            body["identity"] = identity
        if fields is not None:
            body["fields"] = fields
        if favorite is not None:
            body["favorite"] = favorite
        return VaultCredential.model_validate(
            self._client.request(
                "PUT", f"/vault/credentials/{credential_id}", body, options=options
            )
        )

    def delete_credential(
        self, credential_id: str, *, options: RequestOptions | None = None
    ) -> None:
        self._client.request("DELETE", f"/vault/credentials/{credential_id}", options=options)

    def search(
        self,
        *,
        agent_id: str,
        search: str,
        type: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[VaultCredential]:
        query: dict[str, str] = {"agentId": agent_id, "search": search}
        if type is not None:
            query["type"] = type
        raw = self._client.request("GET", "/vault/search", query=query, options=options)
        return [VaultCredential.model_validate(item) for item in raw["items"]]

    def generate_password(
        self,
        *,
        length: int | None = None,
        uppercase: bool | None = None,
        lowercase: bool | None = None,
        numbers: bool | None = None,
        symbols: bool | None = None,
        options: RequestOptions | None = None,
    ) -> str:
        body: dict[str, Any] = {}
        if length is not None:
            body["length"] = length
        if uppercase is not None:
            body["uppercase"] = uppercase
        if lowercase is not None:
            body["lowercase"] = lowercase
        if numbers is not None:
            body["numbers"] = numbers
        if symbols is not None:
            body["symbols"] = symbols
        raw = self._client.request(
            "POST", "/vault/generate-password", body or None, options=options
        )
        return raw["password"]

    def get_totp(
        self, credential_id: str, *, options: RequestOptions | None = None
    ) -> VaultTotpOutput:
        return VaultTotpOutput.model_validate(
            self._client.request("GET", f"/vault/totp/{credential_id}", options=options)
        )

    def status(self, agent_id: str, *, options: RequestOptions | None = None) -> VaultStatusOutput:
        return VaultStatusOutput.model_validate(
            self._client.request(
                "GET", "/vault/status", query={"agentId": agent_id}, options=options
            )
        )

    def sync(self, agent_id: str, *, options: RequestOptions | None = None) -> None:
        self._client.request("POST", "/vault/sync", {"agentId": agent_id}, options=options)

    # --- Sharing ---

    def share_credential(
        self,
        *,
        agent_id: str,
        credential_id: str,
        target_agent_id: str,
        permission: str,
        expires_in_seconds: int | None = None,
        options: RequestOptions | None = None,
    ) -> VaultShare:
        body: dict[str, Any] = {
            "agentId": agent_id,
            "credentialId": credential_id,
            "targetAgentId": target_agent_id,
            "permission": permission,
        }
        if expires_in_seconds is not None:
            body["expiresInSeconds"] = expires_in_seconds
        return VaultShare.model_validate(
            self._client.request("POST", "/vault/share", body, options=options)
        )

    def list_shares(
        self,
        *,
        direction: str,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[VaultShare]:
        query: dict[str, str] = {"direction": direction}
        if agent_id is not None:
            query["agentId"] = agent_id
        raw = self._client.request("GET", "/vault/shares", query=query, options=options)
        return [VaultShare.model_validate(item) for item in raw["items"]]

    def revoke_share(
        self,
        *,
        share_id: str,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> None:
        body: dict[str, Any] = {"shareId": share_id}
        if agent_id is not None:
            body["agentId"] = agent_id
        self._client.request("POST", "/vault/share/revoke", body, options=options)

    # --- Ephemeral Tokens ---

    def create_token(
        self,
        *,
        credential_id: str,
        scope: str,
        agent_id: str | None = None,
        ttl_seconds: int | None = None,
        options: RequestOptions | None = None,
    ) -> VaultTokenOutput:
        body: dict[str, Any] = {"credentialId": credential_id, "scope": scope}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl_seconds is not None:
            body["ttlSeconds"] = ttl_seconds
        return VaultTokenOutput.model_validate(
            self._client.request("POST", "/vault/token", body, options=options)
        )

    def exchange_token(
        self, token: str, *, options: RequestOptions | None = None
    ) -> VaultCredential:
        return VaultCredential.model_validate(
            self._client.request("POST", "/vault/token/exchange", {"token": token}, options=options)
        )

    def revoke_tokens(
        self,
        *,
        credential_id: str,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> VaultRevokeTokensResult:
        body: dict[str, Any] = {"credentialId": credential_id}
        if agent_id is not None:
            body["agentId"] = agent_id
        return VaultRevokeTokensResult.model_validate(
            self._client.request("POST", "/vault/token/revoke", body, options=options)
        )


class AsyncVaultResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    @property
    def oauth(self) -> AsyncVaultOAuthResource:
        return AsyncVaultOAuthResource(self._client)

    async def provision(
        self, *, agent_id: str, options: RequestOptions | None = None
    ) -> VaultIdentityOutput:
        return VaultIdentityOutput.model_validate(
            await self._client.request(
                "POST", "/vault/provision", {"agentId": agent_id}, options=options
            )
        )

    async def deprovision(self, *, agent_id: str, options: RequestOptions | None = None) -> None:
        await self._client.request(
            "POST", "/vault/deprovision", {"agentId": agent_id}, options=options
        )

    async def list_credentials(
        self,
        *,
        agent_id: str,
        type: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[VaultCredential]:
        query: dict[str, str] = {"agentId": agent_id}
        if type is not None:
            query["type"] = type
        raw = await self._client.request("GET", "/vault/credentials", query=query, options=options)
        return [VaultCredential.model_validate(item) for item in raw["items"]]

    async def get_credential(
        self, credential_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredential:
        return VaultCredential.model_validate(
            await self._client.request(
                "GET", f"/vault/credentials/{credential_id}", options=options
            )
        )

    async def create_credential(
        self,
        *,
        agent_id: str,
        type: str,
        name: str,
        notes: str | None = None,
        login: dict[str, Any] | None = None,
        card: dict[str, Any] | None = None,
        identity: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool = False,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        body: dict[str, Any] = {
            "agentId": agent_id,
            "type": type,
            "name": name,
            "favorite": favorite,
        }
        if notes is not None:
            body["notes"] = notes
        if login is not None:
            body["login"] = login
        if card is not None:
            body["card"] = card
        if identity is not None:
            body["identity"] = identity
        if fields is not None:
            body["fields"] = fields
        return VaultCredential.model_validate(
            await self._client.request("POST", "/vault/credentials", body, options=options)
        )

    async def update_credential(
        self,
        credential_id: str,
        *,
        name: str | None = None,
        notes: str | None = None,
        login: dict[str, Any] | None = None,
        card: dict[str, Any] | None = None,
        identity: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if notes is not None:
            body["notes"] = notes
        if login is not None:
            body["login"] = login
        if card is not None:
            body["card"] = card
        if identity is not None:
            body["identity"] = identity
        if fields is not None:
            body["fields"] = fields
        if favorite is not None:
            body["favorite"] = favorite
        return VaultCredential.model_validate(
            await self._client.request(
                "PUT", f"/vault/credentials/{credential_id}", body, options=options
            )
        )

    async def delete_credential(
        self, credential_id: str, *, options: RequestOptions | None = None
    ) -> None:
        await self._client.request("DELETE", f"/vault/credentials/{credential_id}", options=options)

    async def search(
        self,
        *,
        agent_id: str,
        search: str,
        type: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[VaultCredential]:
        query: dict[str, str] = {"agentId": agent_id, "search": search}
        if type is not None:
            query["type"] = type
        raw = await self._client.request("GET", "/vault/search", query=query, options=options)
        return [VaultCredential.model_validate(item) for item in raw["items"]]

    async def generate_password(
        self,
        *,
        length: int | None = None,
        uppercase: bool | None = None,
        lowercase: bool | None = None,
        numbers: bool | None = None,
        symbols: bool | None = None,
        options: RequestOptions | None = None,
    ) -> str:
        body: dict[str, Any] = {}
        if length is not None:
            body["length"] = length
        if uppercase is not None:
            body["uppercase"] = uppercase
        if lowercase is not None:
            body["lowercase"] = lowercase
        if numbers is not None:
            body["numbers"] = numbers
        if symbols is not None:
            body["symbols"] = symbols
        raw = await self._client.request(
            "POST", "/vault/generate-password", body or None, options=options
        )
        return raw["password"]

    async def get_totp(
        self, credential_id: str, *, options: RequestOptions | None = None
    ) -> VaultTotpOutput:
        return VaultTotpOutput.model_validate(
            await self._client.request("GET", f"/vault/totp/{credential_id}", options=options)
        )

    async def status(
        self, agent_id: str, *, options: RequestOptions | None = None
    ) -> VaultStatusOutput:
        return VaultStatusOutput.model_validate(
            await self._client.request(
                "GET", "/vault/status", query={"agentId": agent_id}, options=options
            )
        )

    async def sync(self, agent_id: str, *, options: RequestOptions | None = None) -> None:
        await self._client.request("POST", "/vault/sync", {"agentId": agent_id}, options=options)

    # --- Sharing ---

    async def share_credential(
        self,
        *,
        agent_id: str,
        credential_id: str,
        target_agent_id: str,
        permission: str,
        expires_in_seconds: int | None = None,
        options: RequestOptions | None = None,
    ) -> VaultShare:
        body: dict[str, Any] = {
            "agentId": agent_id,
            "credentialId": credential_id,
            "targetAgentId": target_agent_id,
            "permission": permission,
        }
        if expires_in_seconds is not None:
            body["expiresInSeconds"] = expires_in_seconds
        return VaultShare.model_validate(
            await self._client.request("POST", "/vault/share", body, options=options)
        )

    async def list_shares(
        self,
        *,
        direction: str,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> list[VaultShare]:
        query: dict[str, str] = {"direction": direction}
        if agent_id is not None:
            query["agentId"] = agent_id
        raw = await self._client.request("GET", "/vault/shares", query=query, options=options)
        return [VaultShare.model_validate(item) for item in raw["items"]]

    async def revoke_share(
        self,
        *,
        share_id: str,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> None:
        body: dict[str, Any] = {"shareId": share_id}
        if agent_id is not None:
            body["agentId"] = agent_id
        await self._client.request("POST", "/vault/share/revoke", body, options=options)

    # --- Ephemeral Tokens ---

    async def create_token(
        self,
        *,
        credential_id: str,
        scope: str,
        agent_id: str | None = None,
        ttl_seconds: int | None = None,
        options: RequestOptions | None = None,
    ) -> VaultTokenOutput:
        body: dict[str, Any] = {"credentialId": credential_id, "scope": scope}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl_seconds is not None:
            body["ttlSeconds"] = ttl_seconds
        return VaultTokenOutput.model_validate(
            await self._client.request("POST", "/vault/token", body, options=options)
        )

    async def exchange_token(
        self, token: str, *, options: RequestOptions | None = None
    ) -> VaultCredential:
        return VaultCredential.model_validate(
            await self._client.request(
                "POST", "/vault/token/exchange", {"token": token}, options=options
            )
        )

    async def revoke_tokens(
        self,
        *,
        credential_id: str,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> VaultRevokeTokensResult:
        body: dict[str, Any] = {"credentialId": credential_id}
        if agent_id is not None:
            body["agentId"] = agent_id
        return VaultRevokeTokensResult.model_validate(
            await self._client.request("POST", "/vault/token/revoke", body, options=options)
        )
