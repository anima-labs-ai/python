from __future__ import annotations

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import AttachmentDownloadOutput, AttachmentOutput, MessageOutput, PaginatedResponse


def _to_query(
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


class EmailsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> SyncPageIterator[MessageOutput]:
        def _fetch(cursor: str | None = cursor, limit: int | None = limit, agent_id: str | None = agent_id) -> PaginatedResponse[MessageOutput]:
            raw = self._client.request("GET", "/email", query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id))
            return PaginatedResponse[MessageOutput].model_validate(raw)

        return SyncPageIterator(_fetch, cursor=cursor, limit=limit, agent_id=agent_id)

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
            self._client.request("POST", f"/messages/{message_id}/attachments", payload, options=options)
        )

    def get_attachment_url(self, attachment_id: str, *, options: RequestOptions | None = None) -> AttachmentDownloadOutput:
        return AttachmentDownloadOutput.model_validate(
            self._client.request("GET", f"/attachments/{attachment_id}/download", options=options)
        )


class AsyncEmailsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> AsyncPageIterator[MessageOutput]:
        async def _fetch(cursor: str | None = cursor, limit: int | None = limit, agent_id: str | None = agent_id) -> PaginatedResponse[MessageOutput]:
            raw = await self._client.request("GET", "/email", query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id))
            return PaginatedResponse[MessageOutput].model_validate(raw)

        return AsyncPageIterator(_fetch, cursor=cursor, limit=limit, agent_id=agent_id)

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
            await self._client.request("POST", f"/messages/{message_id}/attachments", payload, options=options)
        )

    async def get_attachment_url(self, attachment_id: str, *, options: RequestOptions | None = None) -> AttachmentDownloadOutput:
        return AttachmentDownloadOutput.model_validate(
            await self._client.request("GET", f"/attachments/{attachment_id}/download", options=options)
        )
