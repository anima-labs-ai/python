from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import (
    VaultCredential,
    VaultIdentityOutput,
    VaultStatusOutput,
    VaultTotpOutput,
)


class VaultResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

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


class AsyncVaultResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

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
