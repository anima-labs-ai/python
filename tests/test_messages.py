"""Tests for MessagesResource send paths (send_email / send_sms).

send_email is the only email send path the SDK exposes; these tests pin the
exact wire payload (camelCase keys, optional keys omitted) and that API
rejections surface as typed exceptions — never as silent success.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from anima._exceptions import NotFoundError, ValidationError
from anima._http import AsyncHTTPClient, HTTPClient
from anima._types import MessageOutput
from anima.resources.messages import AsyncMessagesResource, MessagesResource

from .conftest import MESSAGE_RAW

PDF_BASE64 = "JVBERi0xLjQKJdP0zOEK"  # tiny base64 blob standing in for real bytes


class TestSendEmail:
    def test_send_email_minimal(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = MESSAGE_RAW
        resource = MessagesResource(mock_http)
        result = resource.send_email(
            agent_id="agent_001",
            to=["user@example.com"],
            subject="Hello",
            body="Hi there",
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/messages/email",
            {
                "agentId": "agent_001",
                "to": ["user@example.com"],
                "subject": "Hello",
                "body": "Hi there",
            },
            options=None,
        )
        assert isinstance(result, MessageOutput)
        assert result.id == "msg_001"
        assert result.channel.value == "EMAIL"
        assert result.direction.value == "OUTBOUND"

    def test_send_email_omits_unset_optionals(self, mock_http: MagicMock) -> None:
        """Unset optional params must be ABSENT from the payload, not null."""
        mock_http.request.return_value = MESSAGE_RAW
        MessagesResource(mock_http).send_email(
            agent_id="agent_001",
            to=["user@example.com"],
            subject="Hello",
            body="Hi",
        )

        payload = mock_http.request.call_args[0][2]
        assert set(payload.keys()) == {"agentId", "to", "subject", "body"}

    def test_send_email_full_payload_mapping(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = MESSAGE_RAW
        MessagesResource(mock_http).send_email(
            agent_id="agent_001",
            to=["user@example.com"],
            subject="Hello",
            body="Hi",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            body_html="<p>Hi</p>",
            headers={"X-Campaign": "welcome"},
            metadata={"orderId": "ord_1"},
        )

        payload = mock_http.request.call_args[0][2]
        assert payload["cc"] == ["cc@example.com"]
        assert payload["bcc"] == ["bcc@example.com"]
        assert payload["bodyHtml"] == "<p>Hi</p>"
        assert payload["headers"] == {"X-Campaign": "welcome"}
        assert payload["metadata"] == {"orderId": "ord_1"}

    def test_send_email_with_attachments(self, mock_http: MagicMock) -> None:
        """Attachments must reach the wire unmodified — the exact silent-drop
        gap this SDK had: the param did not exist, so bytes never left the
        client."""
        mock_http.request.return_value = MESSAGE_RAW
        attachments = [
            {
                "filename": "report.pdf",
                "contentType": "application/pdf",
                "content": PDF_BASE64,
            },
            {"url": "https://example.com/invoice.pdf"},
            {"filename": "logo.png", "content": PDF_BASE64, "contentId": "logo"},
        ]
        MessagesResource(mock_http).send_email(
            agent_id="agent_001",
            to=["user@example.com"],
            subject="With attachment",
            body="See attached",
            attachments=attachments,
        )

        payload = mock_http.request.call_args[0][2]
        assert payload["attachments"] == attachments
        # base64 content is passed through byte-for-byte
        assert payload["attachments"][0]["content"] == PDF_BASE64

    def test_send_email_threading_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = MESSAGE_RAW
        MessagesResource(mock_http).send_email(
            agent_id="agent_001",
            to=["user@example.com"],
            subject="Re: Hello",
            body="Replying",
            in_reply_to="<msg-abc@agents.useanima.sh>",
            references=[
                "<msg-root@agents.useanima.sh>",
                "<msg-abc@agents.useanima.sh>",
            ],
        )

        payload = mock_http.request.call_args[0][2]
        assert payload["inReplyTo"] == "<msg-abc@agents.useanima.sh>"
        assert payload["references"] == [
            "<msg-root@agents.useanima.sh>",
            "<msg-abc@agents.useanima.sh>",
        ]


@contextmanager
def _http_client_with_handler(
    handler: Callable[[httpx.Request], httpx.Response],
) -> Iterator[HTTPClient]:
    """Real HTTPClient wired to a canned httpx transport (no network)."""
    client = HTTPClient(api_key="sk-test", base_url="https://api.test")
    client._client.close()  # replace the real transport, don't leak it
    client._client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        yield client
    finally:
        client.close()


@contextmanager
def _http_client_with_response(status_code: int, body: dict) -> Iterator[HTTPClient]:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=body)

    with _http_client_with_handler(handler) as client:
        yield client


class TestSendEmailErrors:
    """4xx responses surface as typed exceptions through the REAL HTTP layer."""

    def test_send_email_400_raises_validation_error(self) -> None:
        with (
            _http_client_with_response(
                400,
                {"error": {"message": "to must contain valid emails", "code": "VALIDATION_ERROR"}},
            ) as http,
            pytest.raises(ValidationError) as exc_info,
        ):
            MessagesResource(http).send_email(
                agent_id="agent_001",
                to=["not-an-email"],
                subject="Hello",
                body="Hi",
            )
        assert exc_info.value.status_code == 400
        assert "valid emails" in exc_info.value.message

    def test_send_email_404_raises_not_found(self) -> None:
        with (
            _http_client_with_response(
                404, {"error": {"message": "Agent not found", "code": "NOT_FOUND"}}
            ) as http,
            pytest.raises(NotFoundError),
        ):
            MessagesResource(http).send_email(
                agent_id="agent_missing",
                to=["user@example.com"],
                subject="Hello",
                body="Hi",
            )

    def test_send_email_wire_body_is_json_with_attachments(self) -> None:
        """End-to-end through httpx: the JSON body on the wire carries the
        attachment entries."""
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content.decode())
            captured["url"] = str(request.url)
            return httpx.Response(200, json=MESSAGE_RAW)

        with _http_client_with_handler(handler) as http:
            MessagesResource(http).send_email(
                agent_id="agent_001",
                to=["user@example.com"],
                subject="Wire check",
                body="Hi",
                attachments=[{"filename": "a.txt", "content": PDF_BASE64}],
                in_reply_to="<parent@agents.useanima.sh>",
            )

        assert captured["url"] == "https://api.test/v1/messages/email"
        assert captured["body"]["attachments"] == [{"filename": "a.txt", "content": PDF_BASE64}]
        assert captured["body"]["inReplyTo"] == "<parent@agents.useanima.sh>"


class TestSendSms:
    def test_send_sms_minimal(self, mock_http: MagicMock) -> None:
        sms_raw = {**MESSAGE_RAW, "channel": "SMS"}
        mock_http.request.return_value = sms_raw
        result = MessagesResource(mock_http).send_sms(
            agent_id="agent_001",
            to="+15550001111",
            body="ping",
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/phone/send-sms",
            {"agentId": "agent_001", "to": "+15550001111", "body": "ping"},
            options=None,
        )
        assert result.channel.value == "SMS"

    def test_send_sms_media_urls_mapping(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = MESSAGE_RAW
        MessagesResource(mock_http).send_sms(
            agent_id="agent_001",
            to="+15550001111",
            body="pic",
            media_urls=["https://example.com/cat.jpg"],
        )

        payload = mock_http.request.call_args[0][2]
        assert payload["mediaUrls"] == ["https://example.com/cat.jpg"]


class TestAsyncSendEmail:
    @pytest.mark.asyncio
    async def test_send_email_minimal(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = MESSAGE_RAW
        resource = AsyncMessagesResource(mock_http)
        result = await resource.send_email(
            agent_id="agent_001",
            to=["user@example.com"],
            subject="Hello",
            body="Hi there",
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/messages/email",
            {
                "agentId": "agent_001",
                "to": ["user@example.com"],
                "subject": "Hello",
                "body": "Hi there",
            },
            options=None,
        )
        assert isinstance(result, MessageOutput)
        assert result.id == "msg_001"

    @pytest.mark.asyncio
    async def test_send_email_attachments_and_threading(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = MESSAGE_RAW
        await AsyncMessagesResource(mock_http).send_email(
            agent_id="agent_001",
            to=["user@example.com"],
            subject="Re: docs",
            body="Attached",
            attachments=[{"filename": "doc.pdf", "content": PDF_BASE64}],
            in_reply_to="<parent@agents.useanima.sh>",
            references=["<parent@agents.useanima.sh>"],
        )

        payload = mock_http.request.call_args[0][2]
        assert payload["attachments"] == [{"filename": "doc.pdf", "content": PDF_BASE64}]
        assert payload["inReplyTo"] == "<parent@agents.useanima.sh>"
        assert payload["references"] == ["<parent@agents.useanima.sh>"]
