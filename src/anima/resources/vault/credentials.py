from __future__ import annotations

from typing import Any, cast

from ..._http import RequestOptions
from ..._types import (
    VaultCredential,
    VaultIdentityOutput,
    VaultStatusOutput,
    VaultTotpOutput,
)
from ._base import _AsyncVaultBase, _SyncVaultBase


def _build_credential_body(
    *,
    notes: str | None = None,
    login: dict[str, Any] | None = None,
    card: dict[str, Any] | None = None,
    identity: dict[str, Any] | None = None,
    oauth_token: dict[str, Any] | None = None,
    api_key: dict[str, Any] | None = None,
    certificate: dict[str, Any] | None = None,
    fields: list[dict[str, Any]] | None = None,
    reveal_policy: str | None = None,
) -> dict[str, Any]:
    """Build the fields shared by credential create and update payloads.

    Only non-``None`` values are included. ``api_key`` carries the broker
    config (``allowedHosts`` fail-closed, optionally ``authHeader``/``authScheme``);
    changing ``allowedHosts`` on update requires a master key. ``reveal_policy``
    upgrades (standard -> brokered) need UPDATE access, downgrades are
    master-key-only and audited.
    """
    body: dict[str, Any] = {}
    if notes is not None:
        body["notes"] = notes
    if login is not None:
        body["login"] = login
    if card is not None:
        body["card"] = card
    if identity is not None:
        body["identity"] = identity
    if oauth_token is not None:
        body["oauthToken"] = oauth_token
    if api_key is not None:
        body["apiKey"] = api_key
    if certificate is not None:
        body["certificate"] = certificate
    if fields is not None:
        body["fields"] = fields
    if reveal_policy is not None:
        body["revealPolicy"] = reveal_policy
    return body


class _SyncCredentialsMixin(_SyncVaultBase):
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
        oauth_token: dict[str, Any] | None = None,
        api_key: dict[str, Any] | None = None,
        certificate: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool = False,
        generate_password: dict[str, Any] | None = None,
        reveal_policy: str | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        """Create a credential.

        Pass ``generate_password`` (e.g. ``{}`` or ``{"length": 32}``) to have
        the vault generate the login password server-side: it is stored with
        the credential and never returned — the response carries only the
        masked credential ref. Login type only; mutually exclusive with
        ``login["password"]``. Server defaults: 24 chars, all character
        classes (``uppercase``/``lowercase``/``number``/``special``).
        """
        body: dict[str, Any] = {
            "agentId": agent_id,
            "type": type,
            "name": name,
            "favorite": favorite,
        }
        body.update(
            _build_credential_body(
                notes=notes,
                login=login,
                card=card,
                identity=identity,
                oauth_token=oauth_token,
                api_key=api_key,
                certificate=certificate,
                fields=fields,
                reveal_policy=reveal_policy,
            )
        )
        if generate_password is not None:
            body["generatePassword"] = generate_password
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
        oauth_token: dict[str, Any] | None = None,
        api_key: dict[str, Any] | None = None,
        certificate: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool | None = None,
        reveal_policy: str | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        body = _build_credential_body(
            notes=notes,
            login=login,
            card=card,
            identity=identity,
            oauth_token=oauth_token,
            api_key=api_key,
            certificate=certificate,
            fields=fields,
            reveal_policy=reveal_policy,
        )
        if name is not None:
            body["name"] = name
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
        return cast(str, raw["password"])

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


class _AsyncCredentialsMixin(_AsyncVaultBase):
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
        oauth_token: dict[str, Any] | None = None,
        api_key: dict[str, Any] | None = None,
        certificate: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool = False,
        generate_password: dict[str, Any] | None = None,
        reveal_policy: str | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        """Create a credential.

        Pass ``generate_password`` (e.g. ``{}`` or ``{"length": 32}``) to have
        the vault generate the login password server-side: it is stored with
        the credential and never returned — the response carries only the
        masked credential ref. Login type only; mutually exclusive with
        ``login["password"]``. Server defaults: 24 chars, all character
        classes (``uppercase``/``lowercase``/``number``/``special``).
        """
        body: dict[str, Any] = {
            "agentId": agent_id,
            "type": type,
            "name": name,
            "favorite": favorite,
        }
        body.update(
            _build_credential_body(
                notes=notes,
                login=login,
                card=card,
                identity=identity,
                oauth_token=oauth_token,
                api_key=api_key,
                certificate=certificate,
                fields=fields,
                reveal_policy=reveal_policy,
            )
        )
        if generate_password is not None:
            body["generatePassword"] = generate_password
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
        oauth_token: dict[str, Any] | None = None,
        api_key: dict[str, Any] | None = None,
        certificate: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        favorite: bool | None = None,
        reveal_policy: str | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredential:
        body = _build_credential_body(
            notes=notes,
            login=login,
            card=card,
            identity=identity,
            oauth_token=oauth_token,
            api_key=api_key,
            certificate=certificate,
            fields=fields,
            reveal_policy=reveal_policy,
        )
        if name is not None:
            body["name"] = name
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
        return cast(str, raw["password"])

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
