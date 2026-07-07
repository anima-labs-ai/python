from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import ConnectExtensionResult


class ExtensionResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def connect(
        self,
        *,
        agent_id: str | None = None,
        ttl: str | None = None,
        options: RequestOptions | None = None,
    ) -> ConnectExtensionResult:
        """Create a headless connect handoff for a browser extension worker.

        Auth: with a master key, pass ``agent_id`` to target an agent; with an
        agent key, omit it (the agent is inferred from the key).
        """
        body: dict[str, Any] = {}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl is not None:
            body["ttl"] = ttl
        return ConnectExtensionResult.model_validate(
            self._client.request("POST", "/extension/connect", body or None, options=options)
        )


class AsyncExtensionResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def connect(
        self,
        *,
        agent_id: str | None = None,
        ttl: str | None = None,
        options: RequestOptions | None = None,
    ) -> ConnectExtensionResult:
        """Create a headless connect handoff for a browser extension worker.

        Auth: with a master key, pass ``agent_id`` to target an agent; with an
        agent key, omit it (the agent is inferred from the key).
        """
        body: dict[str, Any] = {}
        if agent_id is not None:
            body["agentId"] = agent_id
        if ttl is not None:
            body["ttl"] = ttl
        return ConnectExtensionResult.model_validate(
            await self._client.request("POST", "/extension/connect", body or None, options=options)
        )
