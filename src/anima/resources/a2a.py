from __future__ import annotations

from typing import Any

import httpx

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import A2ATaskOutput, PaginatedResponse


def _to_query(
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


class A2AResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def discover(self, agent_url: str) -> dict[str, Any]:
        """Fetch an agent's Agent Card from its well-known URL.

        This makes a direct HTTP request to the agent's public URL,
        not through the Anima API.
        """
        url = f"{agent_url.rstrip('/')}/.well-known/agent.json"
        resp = httpx.get(url, timeout=30.0)
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    def submit_task(
        self,
        agent_id: str,
        *,
        type: str,
        input: dict[str, Any],
        from_did: str | None = None,
        options: RequestOptions | None = None,
    ) -> A2ATaskOutput:
        body: dict[str, Any] = {"type": type, "input": input}
        if from_did is not None:
            body["fromDid"] = from_did
        return A2ATaskOutput.model_validate(
            self._client.request("POST", f"/agents/{agent_id}/a2a/tasks", body, options=options)
        )

    def get_task(
        self, agent_id: str, task_id: str, *, options: RequestOptions | None = None
    ) -> A2ATaskOutput:
        return A2ATaskOutput.model_validate(
            self._client.request("GET", f"/agents/{agent_id}/a2a/tasks/{task_id}", options=options)
        )

    def list_tasks(
        self,
        agent_id: str,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[A2ATaskOutput]:
        raw = self._client.request(
            "GET",
            f"/agents/{agent_id}/a2a/tasks",
            query=_to_query(status=status, cursor=cursor, limit=limit),
            options=options,
        )
        return PaginatedResponse[A2ATaskOutput].model_validate(raw)

    def cancel_task(
        self, agent_id: str, task_id: str, *, options: RequestOptions | None = None
    ) -> A2ATaskOutput:
        return A2ATaskOutput.model_validate(
            self._client.request(
                "POST", f"/agents/{agent_id}/a2a/tasks/{task_id}/cancel", options=options
            )
        )


class AsyncA2AResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def discover(self, agent_url: str) -> dict[str, Any]:
        """Fetch an agent's Agent Card from its well-known URL.

        This makes a direct HTTP request to the agent's public URL,
        not through the Anima API.
        """
        url = f"{agent_url.rstrip('/')}/.well-known/agent.json"
        async with httpx.AsyncClient() as http:
            resp = await http.get(url, timeout=30.0)
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]

    async def submit_task(
        self,
        agent_id: str,
        *,
        type: str,
        input: dict[str, Any],
        from_did: str | None = None,
        options: RequestOptions | None = None,
    ) -> A2ATaskOutput:
        body: dict[str, Any] = {"type": type, "input": input}
        if from_did is not None:
            body["fromDid"] = from_did
        return A2ATaskOutput.model_validate(
            await self._client.request(
                "POST", f"/agents/{agent_id}/a2a/tasks", body, options=options
            )
        )

    async def get_task(
        self, agent_id: str, task_id: str, *, options: RequestOptions | None = None
    ) -> A2ATaskOutput:
        return A2ATaskOutput.model_validate(
            await self._client.request(
                "GET", f"/agents/{agent_id}/a2a/tasks/{task_id}", options=options
            )
        )

    async def list_tasks(
        self,
        agent_id: str,
        *,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[A2ATaskOutput]:
        raw = await self._client.request(
            "GET",
            f"/agents/{agent_id}/a2a/tasks",
            query=_to_query(status=status, cursor=cursor, limit=limit),
            options=options,
        )
        return PaginatedResponse[A2ATaskOutput].model_validate(raw)

    async def cancel_task(
        self, agent_id: str, task_id: str, *, options: RequestOptions | None = None
    ) -> A2ATaskOutput:
        return A2ATaskOutput.model_validate(
            await self._client.request(
                "POST", f"/agents/{agent_id}/a2a/tasks/{task_id}/cancel", options=options
            )
        )
