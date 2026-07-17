from __future__ import annotations

# `list` in method annotations would resolve to the sibling `list()` method
# (class-scope shadowing), so the builtin is referenced explicitly where needed.
import builtins
from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import (
    AttachmentDownloadOutput,
    AttachmentOutput,
    MessageOutput,
    PaginatedResponse,
    SemanticSearchResult,
)


def _to_semantic_search_payload(
    query: str,
    *,
    agent_id: str | None = None,
    limit: int | None = None,
    threshold: float | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"query": query}
    if agent_id is not None:
        payload["agentId"] = agent_id
    if limit is not None:
        payload["limit"] = limit
    if threshold is not None:
        payload["threshold"] = threshold
    return payload


def _to_list_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    agent_id: str | None = None,
    thread_id: str | None = None,
    channel: str | None = None,
    direction: str | None = None,
    labels: list[str] | None = None,
    include_spam: bool | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, str | list[str]] | None:
    params: dict[str, str | list[str]] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if agent_id is not None:
        params["agentId"] = agent_id
    if thread_id is not None:
        params["threadId"] = thread_id
    if channel is not None:
        params["channel"] = channel
    if direction is not None:
        params["direction"] = direction
    # Passed through as a list so httpx emits one ``labels=`` key per label.
    # ",".join() would ask for a single label literally named "a,b", which
    # matches nothing — an empty inbox rather than an error.
    if labels:
        params["labels"] = labels
    # ``is not None``, not truthiness: ``include_spam=False`` is the caller
    # explicitly overriding and must reach the wire.
    if include_spam is not None:
        params["includeSpam"] = "true" if include_spam else "false"
    if date_from is not None:
        params["dateRange.from"] = date_from
    if date_to is not None:
        params["dateRange.to"] = date_to
    return params or None


def _to_labels_payload(
    message_id: str,
    add_labels: list[str] | None,
    remove_labels: list[str] | None,
) -> dict[str, Any]:
    """Body for PATCH /messages/{id}/labels.

    Add/remove rather than a whole-array replace: two agents working one inbox
    would silently erase each other's tags under a ``set``, and the server
    applies both operations in a single statement so concurrent callers
    converge. Refusing the empty call here beats a 400 round-trip — the API's
    error would not say which of the two operations the caller forgot.
    """
    if not add_labels and not remove_labels:
        raise ValueError("update_labels requires at least one of add_labels or remove_labels.")
    # ``id`` travels in the path AND the body: the contract's input schema
    # carries it, so omitting it 400s on a required field.
    payload: dict[str, Any] = {"id": message_id}
    if add_labels:
        payload["addLabels"] = add_labels
    if remove_labels:
        payload["removeLabels"] = remove_labels
    return payload


class MessagesResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def send_email(
        self,
        *,
        agent_id: str,
        to: list[str],
        subject: str,
        body: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        body_html: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        in_reply_to: str | None = None,
        references: list[str] | None = None,
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> MessageOutput:
        """Send an email through an agent.

        Each ``attachments`` entry is a dict in the API wire shape:
        ``"filename"``, ``"contentType"`` (both optional, inferred server-side),
        exactly one of ``"content"`` (base64 bytes) or ``"url"`` (server-fetched),
        and optional ``"contentId"`` for inline images referenced from the HTML
        body via ``cid:`` URIs. Max 20 attachments / 25MB total per email.

        ``in_reply_to`` is the Message-ID of the email being replied to;
        ``references`` is the ordered Message-ID chain for threading.
        """
        payload: dict[str, Any] = {
            "agentId": agent_id,
            "to": to,
            "subject": subject,
            "body": body,
        }
        if cc is not None:
            payload["cc"] = cc
        if bcc is not None:
            payload["bcc"] = bcc
        if body_html is not None:
            payload["bodyHtml"] = body_html
        if attachments is not None:
            payload["attachments"] = attachments
        if in_reply_to is not None:
            payload["inReplyTo"] = in_reply_to
        if references is not None:
            payload["references"] = references
        if headers is not None:
            payload["headers"] = headers
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(
            self._client.request("POST", "/messages/email", payload, options=options)
        )

    def send_sms(
        self,
        *,
        agent_id: str,
        to: str,
        body: str,
        media_urls: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> MessageOutput:
        payload: dict[str, Any] = {"agentId": agent_id, "to": to, "body": body}
        if media_urls is not None:
            payload["mediaUrls"] = media_urls
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(
            self._client.request("POST", "/phone/send-sms", payload, options=options)
        )

    def get(self, message_id: str, *, options: RequestOptions | None = None) -> MessageOutput:
        return MessageOutput.model_validate(
            self._client.request("GET", f"/messages/{message_id}", options=options)
        )

    def update_labels(
        self,
        message_id: str,
        *,
        add_labels: builtins.list[str] | None = None,
        remove_labels: builtins.list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> MessageOutput:
        """Add and/or remove labels on one message — the agent's workflow state.

        Adding ``read`` removes ``unread`` and vice versa. Returns the updated
        message, so the caller never has to guess what the labels became. One
        message per call: there is no batch form.
        """
        return MessageOutput.model_validate(
            self._client.request(
                "PATCH",
                f"/messages/{message_id}/labels",
                _to_labels_payload(message_id, add_labels, remove_labels),
                options=options,
            )
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
        thread_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        labels: builtins.list[str] | None = None,
        include_spam: bool | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> SyncPageIterator[MessageOutput]:
        def _fetch(**kw: Any) -> PaginatedResponse[MessageOutput]:
            raw = self._client.request("GET", "/messages", query=_to_list_query(**kw))
            return PaginatedResponse[MessageOutput].model_validate(raw)

        return SyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            agent_id=agent_id,
            thread_id=thread_id,
            channel=channel,
            direction=direction,
            labels=labels,
            include_spam=include_spam,
            date_from=date_from,
            date_to=date_to,
        )

    def search(
        self,
        query: str,
        *,
        agent_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        status: str | None = None,
        labels: builtins.list[str] | None = None,
        include_spam: bool | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[MessageOutput]:
        payload: dict[str, Any] = {"query": query}
        filters: dict[str, Any] = {}
        if agent_id is not None:
            filters["agentId"] = agent_id
        if channel is not None:
            filters["channel"] = channel
        if direction is not None:
            filters["direction"] = direction
        if status is not None:
            filters["status"] = status
        if labels:
            filters["labels"] = labels
        if include_spam is not None:
            filters["includeSpam"] = include_spam
        date_range: dict[str, str] = {}
        if date_from is not None:
            date_range["from"] = date_from
        if date_to is not None:
            date_range["to"] = date_to
        if date_range:
            filters["dateRange"] = date_range
        if filters:
            payload["filters"] = filters
        pagination: dict[str, Any] = {}
        if cursor is not None:
            pagination["cursor"] = cursor
        if limit is not None:
            pagination["limit"] = limit
        if pagination:
            payload["pagination"] = pagination
        raw = self._client.request("POST", "/messages/search", payload, options=options)
        return PaginatedResponse[MessageOutput].model_validate(raw)

    def semantic_search(
        self,
        query: str,
        *,
        agent_id: str | None = None,
        limit: int | None = None,
        threshold: float | None = None,
        options: RequestOptions | None = None,
    ) -> builtins.list[SemanticSearchResult]:
        """Search messages by meaning, not keywords (vector embeddings).

        Returns messages ranked by cosine similarity to ``query``.
        ``threshold`` (0-1, server default 0.7) drops weak matches;
        ``limit`` caps results (server default 10, max 50). An empty list
        means no matches above the threshold.
        """
        raw = self._client.request(
            "POST",
            "/messages/search/semantic",
            _to_semantic_search_payload(query, agent_id=agent_id, limit=limit, threshold=threshold),
            options=options,
        )
        return [SemanticSearchResult.model_validate(item) for item in raw["results"]]

    def upload_attachment(
        self,
        message_id: str,
        *,
        filename: str,
        mime_type: str,
        size_bytes: int,
        options: RequestOptions | None = None,
    ) -> AttachmentOutput:
        payload = {
            "messageId": message_id,
            "filename": filename,
            "mimeType": mime_type,
            "sizeBytes": size_bytes,
        }
        return AttachmentOutput.model_validate(
            self._client.request(
                "POST", f"/messages/{message_id}/attachments", payload, options=options
            )
        )

    def get_attachment_url(
        self, attachment_id: str, *, options: RequestOptions | None = None
    ) -> AttachmentDownloadOutput:
        return AttachmentDownloadOutput.model_validate(
            self._client.request("GET", f"/attachments/{attachment_id}/download", options=options)
        )


class AsyncMessagesResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def send_email(
        self,
        *,
        agent_id: str,
        to: list[str],
        subject: str,
        body: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        body_html: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        in_reply_to: str | None = None,
        references: list[str] | None = None,
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> MessageOutput:
        """Send an email through an agent.

        Each ``attachments`` entry is a dict in the API wire shape:
        ``"filename"``, ``"contentType"`` (both optional, inferred server-side),
        exactly one of ``"content"`` (base64 bytes) or ``"url"`` (server-fetched),
        and optional ``"contentId"`` for inline images referenced from the HTML
        body via ``cid:`` URIs. Max 20 attachments / 25MB total per email.

        ``in_reply_to`` is the Message-ID of the email being replied to;
        ``references`` is the ordered Message-ID chain for threading.
        """
        payload: dict[str, Any] = {
            "agentId": agent_id,
            "to": to,
            "subject": subject,
            "body": body,
        }
        if cc is not None:
            payload["cc"] = cc
        if bcc is not None:
            payload["bcc"] = bcc
        if body_html is not None:
            payload["bodyHtml"] = body_html
        if attachments is not None:
            payload["attachments"] = attachments
        if in_reply_to is not None:
            payload["inReplyTo"] = in_reply_to
        if references is not None:
            payload["references"] = references
        if headers is not None:
            payload["headers"] = headers
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(
            await self._client.request("POST", "/messages/email", payload, options=options)
        )

    async def send_sms(
        self,
        *,
        agent_id: str,
        to: str,
        body: str,
        media_urls: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> MessageOutput:
        payload: dict[str, Any] = {"agentId": agent_id, "to": to, "body": body}
        if media_urls is not None:
            payload["mediaUrls"] = media_urls
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(
            await self._client.request("POST", "/phone/send-sms", payload, options=options)
        )

    async def get(self, message_id: str, *, options: RequestOptions | None = None) -> MessageOutput:
        return MessageOutput.model_validate(
            await self._client.request("GET", f"/messages/{message_id}", options=options)
        )

    async def update_labels(
        self,
        message_id: str,
        *,
        add_labels: builtins.list[str] | None = None,
        remove_labels: builtins.list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> MessageOutput:
        """Add and/or remove labels on one message — the agent's workflow state.

        Adding ``read`` removes ``unread`` and vice versa. Returns the updated
        message, so the caller never has to guess what the labels became. One
        message per call: there is no batch form.
        """
        return MessageOutput.model_validate(
            await self._client.request(
                "PATCH",
                f"/messages/{message_id}/labels",
                _to_labels_payload(message_id, add_labels, remove_labels),
                options=options,
            )
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
        thread_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        labels: builtins.list[str] | None = None,
        include_spam: bool | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> AsyncPageIterator[MessageOutput]:
        async def _fetch(**kw: Any) -> PaginatedResponse[MessageOutput]:
            raw = await self._client.request("GET", "/messages", query=_to_list_query(**kw))
            return PaginatedResponse[MessageOutput].model_validate(raw)

        return AsyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            agent_id=agent_id,
            thread_id=thread_id,
            channel=channel,
            direction=direction,
            labels=labels,
            include_spam=include_spam,
            date_from=date_from,
            date_to=date_to,
        )

    async def search(
        self,
        query: str,
        *,
        agent_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        status: str | None = None,
        labels: builtins.list[str] | None = None,
        include_spam: bool | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[MessageOutput]:
        payload: dict[str, Any] = {"query": query}
        filters: dict[str, Any] = {}
        if agent_id is not None:
            filters["agentId"] = agent_id
        if channel is not None:
            filters["channel"] = channel
        if direction is not None:
            filters["direction"] = direction
        if status is not None:
            filters["status"] = status
        if labels:
            filters["labels"] = labels
        if include_spam is not None:
            filters["includeSpam"] = include_spam
        date_range: dict[str, str] = {}
        if date_from is not None:
            date_range["from"] = date_from
        if date_to is not None:
            date_range["to"] = date_to
        if date_range:
            filters["dateRange"] = date_range
        if filters:
            payload["filters"] = filters
        pagination: dict[str, Any] = {}
        if cursor is not None:
            pagination["cursor"] = cursor
        if limit is not None:
            pagination["limit"] = limit
        if pagination:
            payload["pagination"] = pagination
        raw = await self._client.request("POST", "/messages/search", payload, options=options)
        return PaginatedResponse[MessageOutput].model_validate(raw)

    async def semantic_search(
        self,
        query: str,
        *,
        agent_id: str | None = None,
        limit: int | None = None,
        threshold: float | None = None,
        options: RequestOptions | None = None,
    ) -> builtins.list[SemanticSearchResult]:
        """Search messages by meaning, not keywords (vector embeddings).

        Returns messages ranked by cosine similarity to ``query``.
        ``threshold`` (0-1, server default 0.7) drops weak matches;
        ``limit`` caps results (server default 10, max 50). An empty list
        means no matches above the threshold.
        """
        raw = await self._client.request(
            "POST",
            "/messages/search/semantic",
            _to_semantic_search_payload(query, agent_id=agent_id, limit=limit, threshold=threshold),
            options=options,
        )
        return [SemanticSearchResult.model_validate(item) for item in raw["results"]]

    async def upload_attachment(
        self,
        message_id: str,
        *,
        filename: str,
        mime_type: str,
        size_bytes: int,
        options: RequestOptions | None = None,
    ) -> AttachmentOutput:
        payload = {
            "messageId": message_id,
            "filename": filename,
            "mimeType": mime_type,
            "sizeBytes": size_bytes,
        }
        return AttachmentOutput.model_validate(
            await self._client.request(
                "POST", f"/messages/{message_id}/attachments", payload, options=options
            )
        )

    async def get_attachment_url(
        self, attachment_id: str, *, options: RequestOptions | None = None
    ) -> AttachmentDownloadOutput:
        return AttachmentDownloadOutput.model_validate(
            await self._client.request(
                "GET", f"/attachments/{attachment_id}/download", options=options
            )
        )
