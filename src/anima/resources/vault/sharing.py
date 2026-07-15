from __future__ import annotations

from typing import Any

from ..._http import RequestOptions
from ..._types import VaultShare
from ._base import _AsyncVaultBase, _SyncVaultBase


class _SyncSharingMixin(_SyncVaultBase):
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


class _AsyncSharingMixin(_AsyncVaultBase):
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
