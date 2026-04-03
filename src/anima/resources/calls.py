from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions


def _to_query(
    *,
    agent_id: str | None = None,
    direction: str | None = None,
    state: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if agent_id is not None:
        params["agentId"] = agent_id
    if direction is not None:
        params["direction"] = direction
    if state is not None:
        params["state"] = state
    if limit is not None:
        params["limit"] = str(limit)
    if offset is not None:
        params["offset"] = str(offset)
    return params or None


class CallsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list(
        self,
        *,
        agent_id: str | None = None,
        direction: str | None = None,
        state: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """List voice calls, optionally filtered."""
        return self._client.request(
            "GET",
            "/voice/calls",
            query=_to_query(
                agent_id=agent_id,
                direction=direction,
                state=state,
                limit=limit,
                offset=offset,
            ),
            options=options,
        )

    def get(self, call_id: str, *, options: RequestOptions | None = None) -> dict[str, Any]:
        """Get a specific call by ID."""
        return self._client.request("GET", f"/voice/calls/{call_id}", options=options)

    def create(
        self,
        *,
        to: str,
        agent_id: str | None = None,
        tier: str | None = None,
        greeting: str | None = None,
        from_number: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """Create an outbound call."""
        body: dict[str, Any] = {"to": to}
        if agent_id is not None:
            body["agentId"] = agent_id
        if tier is not None:
            body["tier"] = tier
        if greeting is not None:
            body["greeting"] = greeting
        if from_number is not None:
            body["fromNumber"] = from_number
        return self._client.request("POST", "/voice/calls", body, options=options)

    def get_transcript(self, call_id: str, *, options: RequestOptions | None = None) -> dict[str, Any]:
        """Get the transcript for a call."""
        return self._client.request("GET", f"/voice/calls/{call_id}/transcript", options=options)


class AsyncCallsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        agent_id: str | None = None,
        direction: str | None = None,
        state: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """List voice calls, optionally filtered."""
        return await self._client.request(
            "GET",
            "/voice/calls",
            query=_to_query(
                agent_id=agent_id,
                direction=direction,
                state=state,
                limit=limit,
                offset=offset,
            ),
            options=options,
        )

    async def get(self, call_id: str, *, options: RequestOptions | None = None) -> dict[str, Any]:
        """Get a specific call by ID."""
        return await self._client.request("GET", f"/voice/calls/{call_id}", options=options)

    async def create(
        self,
        *,
        to: str,
        agent_id: str | None = None,
        tier: str | None = None,
        greeting: str | None = None,
        from_number: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """Create an outbound call."""
        body: dict[str, Any] = {"to": to}
        if agent_id is not None:
            body["agentId"] = agent_id
        if tier is not None:
            body["tier"] = tier
        if greeting is not None:
            body["greeting"] = greeting
        if from_number is not None:
            body["fromNumber"] = from_number
        return await self._client.request("POST", "/voice/calls", body, options=options)

    async def get_transcript(self, call_id: str, *, options: RequestOptions | None = None) -> dict[str, Any]:
        """Get the transcript for a call."""
        return await self._client.request("GET", f"/voice/calls/{call_id}/transcript", options=options)
