from __future__ import annotations

from typing import Any, cast

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import (
    PaginatedResponse,
    VaultAuditLogEntry,
    VaultCredential,
    VaultCredentialRequest,
    VaultCredentialRequestCancelResult,
    VaultCredentialRequestStatusOutput,
    VaultIdentityListItem,
    VaultIdentityOutput,
    VaultRevokeTokensResult,
    VaultShare,
    VaultStatusOutput,
    VaultTokenOutput,
    VaultTotpOutput,
)


def _identities_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    status: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if status is not None:
        params["status"] = status
    return params or None


def _audit_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    credential_id: str | None = None,
    agent_id: str | None = None,
    action: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if credential_id is not None:
        params["credentialId"] = credential_id
    if agent_id is not None:
        params["agentId"] = agent_id
    if action is not None:
        params["action"] = action
    if since is not None:
        params["since"] = since
    if until is not None:
        params["until"] = until
    return params or None


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


class VaultResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    @property
    def oauth(self) -> VaultOAuthResource:
        return VaultOAuthResource(self._client)

    def list_identities(
        self,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[VaultIdentityListItem]:
        def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            status: str | None = status,
        ) -> PaginatedResponse[VaultIdentityListItem]:
            raw = self._client.request(
                "GET",
                "/vault/identities",
                query=_identities_query(cursor=cursor, limit=limit, status=status),
                options=options,
            )
            return PaginatedResponse[VaultIdentityListItem].model_validate(raw)

        return SyncPageIterator(_fetch, cursor=cursor, limit=limit, status=status)

    def audit(
        self,
        *,
        credential_id: str | None = None,
        agent_id: str | None = None,
        action: str | None = None,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[VaultAuditLogEntry]:
        """Query the credential audit trail.

        Every access, share, broker use, and denied egress is recorded here —
        never with any secret material.
        """

        def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            credential_id: str | None = credential_id,
            agent_id: str | None = agent_id,
            action: str | None = action,
            since: str | None = since,
            until: str | None = until,
        ) -> PaginatedResponse[VaultAuditLogEntry]:
            raw = self._client.request(
                "GET",
                "/vault/audit",
                query=_audit_query(
                    cursor=cursor,
                    limit=limit,
                    credential_id=credential_id,
                    agent_id=agent_id,
                    action=action,
                    since=since,
                    until=until,
                ),
                options=options,
            )
            return PaginatedResponse[VaultAuditLogEntry].model_validate(raw)

        return SyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            credential_id=credential_id,
            agent_id=agent_id,
            action=action,
            since=since,
            until=until,
        )

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
            # For broker use, include allowedHosts (fail-closed) and optionally
            # authHeader/authScheme — see use_credential.
            body["apiKey"] = api_key
        if certificate is not None:
            body["certificate"] = certificate
        if fields is not None:
            body["fields"] = fields
        if generate_password is not None:
            body["generatePassword"] = generate_password
        if reveal_policy is not None:
            body["revealPolicy"] = reveal_policy
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
        if oauth_token is not None:
            body["oauthToken"] = oauth_token
        if api_key is not None:
            # Changing apiKey.allowedHosts requires a master key.
            body["apiKey"] = api_key
        if certificate is not None:
            body["certificate"] = certificate
        if fields is not None:
            body["fields"] = fields
        if favorite is not None:
            body["favorite"] = favorite
        if reveal_policy is not None:
            # Upgrading standard -> brokered needs UPDATE access; downgrading
            # brokered -> standard is master-key-only and audited.
            body["revealPolicy"] = reveal_policy
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

    # --- Credential requests (human-in-the-loop) ---

    def credential_request_create(
        self,
        *,
        type: str,
        name: str,
        reason: str,
        agent_id: str | None = None,
        ttl_seconds: int | None = None,
        notify_owner: bool | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredentialRequest:
        """Ask a human for a credential the agent must never see.

        Returns a token-gated fill URL the owner completes out-of-band; poll
        ``credential_request_status`` until FULFILLED, then use the credential
        by reference (``use_credential``) — the plaintext is never returned.
        """
        body: dict[str, Any] = {"type": type, "name": name, "reason": reason}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl_seconds is not None:
            body["ttlSeconds"] = ttl_seconds
        if notify_owner is not None:
            body["notifyOwner"] = notify_owner
        return VaultCredentialRequest.model_validate(
            self._client.request("POST", "/vault/credential-requests", body, options=options)
        )

    def credential_request_status(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestStatusOutput:
        return VaultCredentialRequestStatusOutput.model_validate(
            self._client.request("GET", f"/vault/credential-requests/{request_id}", options=options)
        )

    def credential_request_cancel(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestCancelResult:
        return VaultCredentialRequestCancelResult.model_validate(
            self._client.request(
                "POST", f"/vault/credential-requests/{request_id}/cancel", None, options=options
            )
        )

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

    def exchange_token_for_injection(
        self, token: str, *, options: RequestOptions | None = None
    ) -> VaultCredential:
        """Exchange a vault token for the PLAINTEXT credential, to inject into a
        trusted client process (CLI/extension) — never to read into an LLM.

        The API gates this to injector credentials (a master key or a key with
        the ``vault:inject`` scope); a plain agent key gets 403. To *use* a
        secret without seeing it, call ``use_credential`` (the broker).
        """
        return VaultCredential.model_validate(
            self._client.request("POST", "/vault/token/exchange", {"token": token}, options=options)
        )

    def use_credential(
        self,
        id: str,
        *,
        method: str,
        url: str,
        agent_id: str | None = None,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """Make an outbound HTTPS call with the credential attached server-side.

        Returns the upstream response (status/headers/body); the plaintext
        secret is never returned. Works for brokered credentials.
        """
        payload: dict[str, Any] = {"method": method, "url": url}
        if agent_id is not None:
            payload["agentId"] = agent_id
        if headers is not None:
            payload["headers"] = headers
        if body is not None:
            payload["body"] = body
        return cast(
            "dict[str, Any]",
            self._client.request("POST", f"/vault/credentials/{id}/use", payload, options=options),
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

    def list_identities(
        self,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[VaultIdentityListItem]:
        async def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            status: str | None = status,
        ) -> PaginatedResponse[VaultIdentityListItem]:
            raw = await self._client.request(
                "GET",
                "/vault/identities",
                query=_identities_query(cursor=cursor, limit=limit, status=status),
                options=options,
            )
            return PaginatedResponse[VaultIdentityListItem].model_validate(raw)

        return AsyncPageIterator(_fetch, cursor=cursor, limit=limit, status=status)

    def audit(
        self,
        *,
        credential_id: str | None = None,
        agent_id: str | None = None,
        action: str | None = None,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[VaultAuditLogEntry]:
        """Query the credential audit trail.

        Every access, share, broker use, and denied egress is recorded here —
        never with any secret material.
        """

        async def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            credential_id: str | None = credential_id,
            agent_id: str | None = agent_id,
            action: str | None = action,
            since: str | None = since,
            until: str | None = until,
        ) -> PaginatedResponse[VaultAuditLogEntry]:
            raw = await self._client.request(
                "GET",
                "/vault/audit",
                query=_audit_query(
                    cursor=cursor,
                    limit=limit,
                    credential_id=credential_id,
                    agent_id=agent_id,
                    action=action,
                    since=since,
                    until=until,
                ),
                options=options,
            )
            return PaginatedResponse[VaultAuditLogEntry].model_validate(raw)

        return AsyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            credential_id=credential_id,
            agent_id=agent_id,
            action=action,
            since=since,
            until=until,
        )

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
            # For broker use, include allowedHosts (fail-closed) and optionally
            # authHeader/authScheme — see use_credential.
            body["apiKey"] = api_key
        if certificate is not None:
            body["certificate"] = certificate
        if fields is not None:
            body["fields"] = fields
        if generate_password is not None:
            body["generatePassword"] = generate_password
        if reveal_policy is not None:
            body["revealPolicy"] = reveal_policy
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
        if oauth_token is not None:
            body["oauthToken"] = oauth_token
        if api_key is not None:
            # Changing apiKey.allowedHosts requires a master key.
            body["apiKey"] = api_key
        if certificate is not None:
            body["certificate"] = certificate
        if fields is not None:
            body["fields"] = fields
        if favorite is not None:
            body["favorite"] = favorite
        if reveal_policy is not None:
            # Upgrading standard -> brokered needs UPDATE access; downgrading
            # brokered -> standard is master-key-only and audited.
            body["revealPolicy"] = reveal_policy
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

    # --- Credential requests (human-in-the-loop) ---

    async def credential_request_create(
        self,
        *,
        type: str,
        name: str,
        reason: str,
        agent_id: str | None = None,
        ttl_seconds: int | None = None,
        notify_owner: bool | None = None,
        options: RequestOptions | None = None,
    ) -> VaultCredentialRequest:
        """Ask a human for a credential the agent must never see.

        Returns a token-gated fill URL the owner completes out-of-band; poll
        ``credential_request_status`` until FULFILLED, then use the credential
        by reference (``use_credential``) — the plaintext is never returned.
        """
        body: dict[str, Any] = {"type": type, "name": name, "reason": reason}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl_seconds is not None:
            body["ttlSeconds"] = ttl_seconds
        if notify_owner is not None:
            body["notifyOwner"] = notify_owner
        return VaultCredentialRequest.model_validate(
            await self._client.request("POST", "/vault/credential-requests", body, options=options)
        )

    async def credential_request_status(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestStatusOutput:
        return VaultCredentialRequestStatusOutput.model_validate(
            await self._client.request(
                "GET", f"/vault/credential-requests/{request_id}", options=options
            )
        )

    async def credential_request_cancel(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> VaultCredentialRequestCancelResult:
        return VaultCredentialRequestCancelResult.model_validate(
            await self._client.request(
                "POST", f"/vault/credential-requests/{request_id}/cancel", None, options=options
            )
        )

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

    async def exchange_token_for_injection(
        self, token: str, *, options: RequestOptions | None = None
    ) -> VaultCredential:
        """Exchange a vault token for the PLAINTEXT credential, to inject into a
        trusted client process (CLI/extension) — never to read into an LLM.

        Gated to injector credentials (master key or a key with ``vault:inject``);
        a plain agent key gets 403. Use ``use_credential`` (the broker) to use a
        secret without seeing it.
        """
        return VaultCredential.model_validate(
            await self._client.request(
                "POST", "/vault/token/exchange", {"token": token}, options=options
            )
        )

    async def use_credential(
        self,
        id: str,
        *,
        method: str,
        url: str,
        agent_id: str | None = None,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """Make an outbound HTTPS call with the credential attached server-side.

        Returns the upstream response; the plaintext secret is never returned.
        """
        payload: dict[str, Any] = {"method": method, "url": url}
        if agent_id is not None:
            payload["agentId"] = agent_id
        if headers is not None:
            payload["headers"] = headers
        if body is not None:
            payload["body"] = body
        return cast(
            "dict[str, Any]",
            await self._client.request(
                "POST", f"/vault/credentials/{id}/use", payload, options=options
            ),
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
