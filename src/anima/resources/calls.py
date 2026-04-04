from __future__ import annotations

import re
from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import CallOutput, CallTranscript, CreateCallOutput
from .._voice_connection import VoiceConnection


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
    def __init__(self, client: HTTPClient, api_key: str = "", base_url: str = "") -> None:
        self._client = client
        self._api_key = api_key
        self._ws_base_url = re.sub(r"^https://", "wss://", re.sub(r"^http://", "ws://", base_url))

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
        raw = self._client.request(
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
        if isinstance(raw, dict) and "calls" in raw:
            raw["calls"] = [CallOutput.model_validate(c) for c in raw["calls"]]
        return raw

    def get(self, call_id: str, *, options: RequestOptions | None = None) -> CallOutput:
        """Get a specific call by ID."""
        raw = self._client.request("GET", f"/voice/calls/{call_id}", options=options)
        return CallOutput.model_validate(raw)

    def create(
        self,
        *,
        to: str,
        agent_id: str | None = None,
        tier: str | None = None,
        greeting: str | None = None,
        from_number: str | None = None,
        options: RequestOptions | None = None,
    ) -> CreateCallOutput:
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
        raw = self._client.request("POST", "/voice/calls", body, options=options)
        return CreateCallOutput.model_validate(raw)

    def get_transcript(
        self, call_id: str, *, options: RequestOptions | None = None
    ) -> CallTranscript:
        """Get the transcript for a call."""
        raw = self._client.request("GET", f"/voice/calls/{call_id}/transcript", options=options)
        return CallTranscript.model_validate(raw)

    def connect(self, *, agent_id: str | None = None) -> VoiceConnection:
        """Open a bidirectional WebSocket for real-time voice call control.

        Usage::

            conn = client.calls.connect()
            conn.on_message(lambda msg: print(msg["type"], msg.get("data")))
            conn.create_call("+15551234567")
            # ... handle events ...
            conn.close()
        """
        params = f"token={self._api_key}"
        if agent_id:
            params += f"&agentId={agent_id}"
        ws_url = f"{self._ws_base_url}/ws/voice?{params}"
        return VoiceConnection(ws_url)


class AsyncCallsResource:
    def __init__(self, client: AsyncHTTPClient, api_key: str = "", base_url: str = "") -> None:
        self._client = client
        self._api_key = api_key
        self._ws_base_url = re.sub(r"^https://", "wss://", re.sub(r"^http://", "ws://", base_url))

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
        raw = await self._client.request(
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
        if isinstance(raw, dict) and "calls" in raw:
            raw["calls"] = [CallOutput.model_validate(c) for c in raw["calls"]]
        return raw

    async def get(self, call_id: str, *, options: RequestOptions | None = None) -> CallOutput:
        """Get a specific call by ID."""
        raw = await self._client.request("GET", f"/voice/calls/{call_id}", options=options)
        return CallOutput.model_validate(raw)

    async def create(
        self,
        *,
        to: str,
        agent_id: str | None = None,
        tier: str | None = None,
        greeting: str | None = None,
        from_number: str | None = None,
        options: RequestOptions | None = None,
    ) -> CreateCallOutput:
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
        raw = await self._client.request("POST", "/voice/calls", body, options=options)
        return CreateCallOutput.model_validate(raw)

    async def get_transcript(
        self, call_id: str, *, options: RequestOptions | None = None
    ) -> CallTranscript:
        """Get the transcript for a call."""
        raw = await self._client.request(
            "GET", f"/voice/calls/{call_id}/transcript", options=options
        )
        return CallTranscript.model_validate(raw)

    def connect(self, *, agent_id: str | None = None) -> VoiceConnection:
        """Open a bidirectional WebSocket for real-time voice call control."""
        params = f"token={self._api_key}"
        if agent_id:
            params += f"&agentId={agent_id}"
        ws_url = f"{self._ws_base_url}/ws/voice?{params}"
        return VoiceConnection(ws_url)
