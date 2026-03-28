"""Tests for EmailsResource with mocked HTTP."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from anima._types import AttachmentDownloadOutput, AttachmentOutput, MessageOutput, PaginatedResponse
from anima.resources.emails import EmailsResource

from .conftest import (
    ATTACHMENT_DOWNLOAD_RAW,
    ATTACHMENT_RAW,
    MESSAGE_RAW,
    PAGINATED_MESSAGES_RAW,
)


class TestEmailsList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_MESSAGES_RAW
        resource = EmailsResource(mock_http)
        result = resource.list()

        mock_http.request.assert_called_once_with("GET", "/email", query=None)
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.pagination.has_more is False

    def test_list_with_cursor_and_limit(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_MESSAGES_RAW
        resource = EmailsResource(mock_http)
        resource.list(cursor="cur_abc", limit=25)

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["cursor"] == "cur_abc"
        assert query["limit"] == "25"

    def test_list_with_agent_id(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_MESSAGES_RAW
        resource = EmailsResource(mock_http)
        resource.list(agent_id="agent_001")

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["agentId"] == "agent_001"

    def test_list_parses_message_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_MESSAGES_RAW
        resource = EmailsResource(mock_http)
        result = resource.list()

        msg = result.items[0]
        assert isinstance(msg, MessageOutput)
        assert msg.id == "msg_001"
        assert msg.from_address == "agent@test.com"
        assert msg.to_address == "user@example.com"
        assert msg.subject == "Hello"
        assert msg.channel.value == "EMAIL"
        assert msg.direction.value == "OUTBOUND"
        assert msg.status.value == "SENT"


class TestEmailsUploadAttachment:
    def test_upload_attachment(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = ATTACHMENT_RAW
        resource = EmailsResource(mock_http)
        result = resource.upload_attachment(
            "msg_001",
            filename="report.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/messages/msg_001/attachments",
            {
                "messageId": "msg_001",
                "filename": "report.pdf",
                "mimeType": "application/pdf",
                "sizeBytes": 1024,
            },
        )
        assert isinstance(result, AttachmentOutput)
        assert result.id == "att_001"
        assert result.filename == "report.pdf"
        assert result.mime_type == "application/pdf"
        assert result.size_bytes == 1024


class TestEmailsGetAttachmentUrl:
    def test_get_attachment_url(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = ATTACHMENT_DOWNLOAD_RAW
        resource = EmailsResource(mock_http)
        result = resource.get_attachment_url("att_001")

        mock_http.request.assert_called_once_with(
            "GET", "/attachments/att_001/download"
        )
        assert isinstance(result, AttachmentDownloadOutput)
        assert "signed=1" in result.url
        assert result.expires_at == "2025-01-01T01:00:00Z"
