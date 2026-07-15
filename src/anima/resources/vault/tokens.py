from __future__ import annotations

from typing import Any, cast

from ..._http import RequestOptions
from ..._types import VaultCredential, VaultRevokeTokensResult, VaultTokenOutput
from ._base import _AsyncVaultBase, _SyncVaultBase


class _SyncTokensMixin(_SyncVaultBase):
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
        credential_id: str,
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
            dict[str, Any],
            self._client.request(
                "POST", f"/vault/credentials/{credential_id}/use", payload, options=options
            ),
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


class _AsyncTokensMixin(_AsyncVaultBase):
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
        credential_id: str,
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
            dict[str, Any],
            await self._client.request(
                "POST", f"/vault/credentials/{credential_id}/use", payload, options=options
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
