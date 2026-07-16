from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import EmailDraftOutput, MessageOutput, PaginatedResponse


def _to_list_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    agent_id: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if agent_id is not None:
        params["agentId"] = agent_id
    return params or None


def _to_create_payload(
    *,
    agent_id: str,
    from_identity_id: str | None = None,
    to: list[str] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    subject: str | None = None,
    body: str | None = None,
    body_html: str | None = None,
    in_reply_to: str | None = None,
    references: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"agentId": agent_id}
    if from_identity_id is not None:
        payload["fromIdentityId"] = from_identity_id
    if to is not None:
        payload["to"] = to
    if cc is not None:
        payload["cc"] = cc
    if bcc is not None:
        payload["bcc"] = bcc
    if subject is not None:
        payload["subject"] = subject
    if body is not None:
        payload["body"] = body
    if body_html is not None:
        payload["bodyHtml"] = body_html
    if in_reply_to is not None:
        payload["inReplyTo"] = in_reply_to
    if references is not None:
        payload["references"] = references
    if metadata is not None:
        payload["metadata"] = metadata
    return payload


class EmailDraftsResource:
    """Email drafts: create, get, list, send, delete.

    Drafts are composed-but-not-sent emails owned by an agent. They may be
    incomplete (no recipients, subject, or body yet). ``send`` atomically
    converts a draft into a delivered message and deletes the draft row,
    returning the new :class:`~anima._types.MessageOutput`.
    """

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        agent_id: str,
        from_identity_id: str | None = None,
        to: list[str] | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        subject: str | None = None,
        body: str | None = None,
        body_html: str | None = None,
        in_reply_to: str | None = None,
        references: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> EmailDraftOutput:
        """Create a draft. Only ``agent_id`` is required — everything else can
        be filled in before sending.

        ``from_identity_id`` selects the sender identity; when omitted the
        agent's primary identity is used at send time. ``in_reply_to`` /
        ``references`` carry RFC Message-IDs for threading on send.
        """
        payload = _to_create_payload(
            agent_id=agent_id,
            from_identity_id=from_identity_id,
            to=to,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            body_html=body_html,
            in_reply_to=in_reply_to,
            references=references,
            metadata=metadata,
        )
        return EmailDraftOutput.model_validate(
            self._client.request("POST", "/email/drafts", payload, options=options)
        )

    def get(self, draft_id: str, *, options: RequestOptions | None = None) -> EmailDraftOutput:
        return EmailDraftOutput.model_validate(
            self._client.request("GET", f"/email/drafts/{draft_id}", options=options)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> SyncPageIterator[EmailDraftOutput]:
        def _fetch(**kw: Any) -> PaginatedResponse[EmailDraftOutput]:
            raw = self._client.request("GET", "/email/drafts", query=_to_list_query(**kw))
            return PaginatedResponse[EmailDraftOutput].model_validate(raw)

        return SyncPageIterator(_fetch, cursor=cursor, limit=limit, agent_id=agent_id)

    def send(self, draft_id: str, *, options: RequestOptions | None = None) -> MessageOutput:
        """Send a draft.

        Atomically converts the draft into a Message (email.send semantics)
        and deletes the draft row. The draft must have at least one recipient,
        a subject, and a body. Returns the newly created message, not the
        draft.
        """
        return MessageOutput.model_validate(
            self._client.request("POST", f"/email/drafts/{draft_id}/send", options=options)
        )

    def delete(self, draft_id: str, *, options: RequestOptions | None = None) -> EmailDraftOutput:
        """Discard a draft. Returns the deleted draft's final state."""
        return EmailDraftOutput.model_validate(
            self._client.request("DELETE", f"/email/drafts/{draft_id}", options=options)
        )


class AsyncEmailDraftsResource:
    """Async mirror of :class:`EmailDraftsResource`."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        agent_id: str,
        from_identity_id: str | None = None,
        to: list[str] | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        subject: str | None = None,
        body: str | None = None,
        body_html: str | None = None,
        in_reply_to: str | None = None,
        references: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> EmailDraftOutput:
        """Create a draft. Only ``agent_id`` is required — everything else can
        be filled in before sending.

        ``from_identity_id`` selects the sender identity; when omitted the
        agent's primary identity is used at send time. ``in_reply_to`` /
        ``references`` carry RFC Message-IDs for threading on send.
        """
        payload = _to_create_payload(
            agent_id=agent_id,
            from_identity_id=from_identity_id,
            to=to,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            body_html=body_html,
            in_reply_to=in_reply_to,
            references=references,
            metadata=metadata,
        )
        return EmailDraftOutput.model_validate(
            await self._client.request("POST", "/email/drafts", payload, options=options)
        )

    async def get(
        self, draft_id: str, *, options: RequestOptions | None = None
    ) -> EmailDraftOutput:
        return EmailDraftOutput.model_validate(
            await self._client.request("GET", f"/email/drafts/{draft_id}", options=options)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> AsyncPageIterator[EmailDraftOutput]:
        async def _fetch(**kw: Any) -> PaginatedResponse[EmailDraftOutput]:
            raw = await self._client.request("GET", "/email/drafts", query=_to_list_query(**kw))
            return PaginatedResponse[EmailDraftOutput].model_validate(raw)

        return AsyncPageIterator(_fetch, cursor=cursor, limit=limit, agent_id=agent_id)

    async def send(self, draft_id: str, *, options: RequestOptions | None = None) -> MessageOutput:
        """Send a draft.

        Atomically converts the draft into a Message (email.send semantics)
        and deletes the draft row. The draft must have at least one recipient,
        a subject, and a body. Returns the newly created message, not the
        draft.
        """
        return MessageOutput.model_validate(
            await self._client.request("POST", f"/email/drafts/{draft_id}/send", options=options)
        )

    async def delete(
        self, draft_id: str, *, options: RequestOptions | None = None
    ) -> EmailDraftOutput:
        """Discard a draft. Returns the deleted draft's final state."""
        return EmailDraftOutput.model_validate(
            await self._client.request("DELETE", f"/email/drafts/{draft_id}", options=options)
        )
