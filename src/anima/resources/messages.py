from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import AttachmentDownloadOutput, AttachmentOutput, MessageOutput, PaginatedResponse


def _to_list_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    agent_id: str | None = None,
    thread_id: str | None = None,
    channel: str | None = None,
    direction: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
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
    if date_from is not None:
        params["dateRange.from"] = date_from
    if date_to is not None:
        params["dateRange.to"] = date_to
    return params or None


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
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageOutput:
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
        if headers is not None:
            payload["headers"] = headers
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(
            self._client.request("POST", "/messages/email", payload)
        )

    def send_sms(
        self,
        *,
        agent_id: str,
        to: str,
        body: str,
        media_urls: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageOutput:
        payload: dict[str, Any] = {"agentId": agent_id, "to": to, "body": body}
        if media_urls is not None:
            payload["mediaUrls"] = media_urls
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(self._client.request("POST", "/phone/send-sms", payload))

    def get(self, message_id: str) -> MessageOutput:
        return MessageOutput.model_validate(self._client.request("GET", f"/messages/{message_id}"))

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
        thread_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> PaginatedResponse[MessageOutput]:
        raw = self._client.request(
            "GET",
            "/messages",
            query=_to_list_query(
                cursor=cursor,
                limit=limit,
                agent_id=agent_id,
                thread_id=thread_id,
                channel=channel,
                direction=direction,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        return PaginatedResponse[MessageOutput].model_validate(raw)

    def search(
        self,
        query: str,
        *,
        agent_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
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
        raw = self._client.request("POST", "/messages/search", payload)
        return PaginatedResponse[MessageOutput].model_validate(raw)

    def upload_attachment(
        self,
        message_id: str,
        *,
        filename: str,
        mime_type: str,
        size_bytes: int,
    ) -> AttachmentOutput:
        payload = {
            "messageId": message_id,
            "filename": filename,
            "mimeType": mime_type,
            "sizeBytes": size_bytes,
        }
        return AttachmentOutput.model_validate(
            self._client.request("POST", f"/messages/{message_id}/attachments", payload)
        )

    def get_attachment_url(self, attachment_id: str) -> AttachmentDownloadOutput:
        return AttachmentDownloadOutput.model_validate(
            self._client.request("GET", f"/attachments/{attachment_id}/download")
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
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageOutput:
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
        if headers is not None:
            payload["headers"] = headers
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(
            await self._client.request("POST", "/messages/email", payload)
        )

    async def send_sms(
        self,
        *,
        agent_id: str,
        to: str,
        body: str,
        media_urls: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageOutput:
        payload: dict[str, Any] = {"agentId": agent_id, "to": to, "body": body}
        if media_urls is not None:
            payload["mediaUrls"] = media_urls
        if metadata is not None:
            payload["metadata"] = metadata
        return MessageOutput.model_validate(
            await self._client.request("POST", "/phone/send-sms", payload)
        )

    async def get(self, message_id: str) -> MessageOutput:
        return MessageOutput.model_validate(
            await self._client.request("GET", f"/messages/{message_id}")
        )

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
        thread_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> PaginatedResponse[MessageOutput]:
        raw = await self._client.request(
            "GET",
            "/messages",
            query=_to_list_query(
                cursor=cursor,
                limit=limit,
                agent_id=agent_id,
                thread_id=thread_id,
                channel=channel,
                direction=direction,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        return PaginatedResponse[MessageOutput].model_validate(raw)

    async def search(
        self,
        query: str,
        *,
        agent_id: str | None = None,
        channel: str | None = None,
        direction: str | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
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
        raw = await self._client.request("POST", "/messages/search", payload)
        return PaginatedResponse[MessageOutput].model_validate(raw)

    async def upload_attachment(
        self,
        message_id: str,
        *,
        filename: str,
        mime_type: str,
        size_bytes: int,
    ) -> AttachmentOutput:
        payload = {
            "messageId": message_id,
            "filename": filename,
            "mimeType": mime_type,
            "sizeBytes": size_bytes,
        }
        return AttachmentOutput.model_validate(
            await self._client.request("POST", f"/messages/{message_id}/attachments", payload)
        )

    async def get_attachment_url(self, attachment_id: str) -> AttachmentDownloadOutput:
        return AttachmentDownloadOutput.model_validate(
            await self._client.request("GET", f"/attachments/{attachment_id}/download")
        )
