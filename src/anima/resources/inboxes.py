from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import InboxListItem, InboxOutput, PaginatedResponse


def _to_list_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    query: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if query is not None:
        params["query"] = query
    return params or None


def _to_create_payload(
    *,
    username: str | None = None,
    domain: str | None = None,
    display_name: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if username is not None:
        payload["username"] = username
    if domain is not None:
        payload["domain"] = domain
    if display_name is not None:
        payload["displayName"] = display_name
    if agent_id is not None:
        payload["agentId"] = agent_id
    return payload


def _to_update_payload(
    *,
    display_name: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if display_name is not None:
        payload["displayName"] = display_name
    if agent_id is not None:
        payload["agentId"] = agent_id
    return payload


class InboxesResource:
    """Email inboxes: create, get, list, update, delete."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        username: str | None = None,
        domain: str | None = None,
        display_name: str | None = None,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> InboxOutput:
        """Create an inbox.

        All fields are optional: the server generates a username when omitted
        and falls back to the default domain.
        """
        payload = _to_create_payload(
            username=username,
            domain=domain,
            display_name=display_name,
            agent_id=agent_id,
        )
        return InboxOutput.model_validate(
            self._client.request("POST", "/inboxes", payload, options=options)
        )

    def get(self, inbox_id: str, *, options: RequestOptions | None = None) -> InboxOutput:
        return InboxOutput.model_validate(
            self._client.request("GET", f"/inboxes/{inbox_id}", options=options)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        query: str | None = None,
    ) -> SyncPageIterator[InboxListItem]:
        def _fetch(**kw: Any) -> PaginatedResponse[InboxListItem]:
            raw = self._client.request("GET", "/inboxes", query=_to_list_query(**kw))
            return PaginatedResponse[InboxListItem].model_validate(raw)

        return SyncPageIterator(_fetch, cursor=cursor, limit=limit, query=query)

    def update(
        self,
        inbox_id: str,
        *,
        display_name: str | None = None,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> InboxOutput:
        body = _to_update_payload(display_name=display_name, agent_id=agent_id)
        return InboxOutput.model_validate(
            self._client.request("PATCH", f"/inboxes/{inbox_id}", body, options=options)
        )

    def delete(self, inbox_id: str, *, options: RequestOptions | None = None) -> None:
        self._client.request("DELETE", f"/inboxes/{inbox_id}", options=options)


class AsyncInboxesResource:
    """Email inboxes: create, get, list, update, delete (async)."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        username: str | None = None,
        domain: str | None = None,
        display_name: str | None = None,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> InboxOutput:
        """Create an inbox.

        All fields are optional: the server generates a username when omitted
        and falls back to the default domain.
        """
        payload = _to_create_payload(
            username=username,
            domain=domain,
            display_name=display_name,
            agent_id=agent_id,
        )
        return InboxOutput.model_validate(
            await self._client.request("POST", "/inboxes", payload, options=options)
        )

    async def get(self, inbox_id: str, *, options: RequestOptions | None = None) -> InboxOutput:
        return InboxOutput.model_validate(
            await self._client.request("GET", f"/inboxes/{inbox_id}", options=options)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        query: str | None = None,
    ) -> AsyncPageIterator[InboxListItem]:
        async def _fetch(**kw: Any) -> PaginatedResponse[InboxListItem]:
            raw = await self._client.request("GET", "/inboxes", query=_to_list_query(**kw))
            return PaginatedResponse[InboxListItem].model_validate(raw)

        return AsyncPageIterator(_fetch, cursor=cursor, limit=limit, query=query)

    async def update(
        self,
        inbox_id: str,
        *,
        display_name: str | None = None,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> InboxOutput:
        body = _to_update_payload(display_name=display_name, agent_id=agent_id)
        return InboxOutput.model_validate(
            await self._client.request("PATCH", f"/inboxes/{inbox_id}", body, options=options)
        )

    async def delete(self, inbox_id: str, *, options: RequestOptions | None = None) -> None:
        await self._client.request("DELETE", f"/inboxes/{inbox_id}", options=options)
