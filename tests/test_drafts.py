"""Tests for EmailDraftsResource (create / get / list / send / delete).

Intent: drafts are the compose-review-send workflow for agents. The wire
contract these tests pin down is the one the live API serves
(`/v1/email/drafts`): camelCase payloads, cursor pagination, send-with-no-body
returning a Message (not a draft), and delete returning the deleted draft.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import EmailDraftOutput, MessageOutput
from anima.resources.drafts import AsyncEmailDraftsResource, EmailDraftsResource

from .conftest import EMAIL_DRAFT_RAW, MESSAGE_RAW, PAGINATED_DRAFTS_RAW


class TestDraftsCreate:
    def test_create_with_all_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = EMAIL_DRAFT_RAW
        result = EmailDraftsResource(mock_http).create(
            agent_id="agent_001",
            from_identity_id="ei_001",
            to=["user@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            subject="Quarterly report",
            body="Draft body",
            body_html="<p>Draft body</p>",
            in_reply_to="<abc@agents.useanima.sh>",
            references=["<abc@agents.useanima.sh>"],
            metadata={"k": "v"},
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/email/drafts",
            {
                "agentId": "agent_001",
                "fromIdentityId": "ei_001",
                "to": ["user@example.com"],
                "cc": ["cc@example.com"],
                "bcc": ["bcc@example.com"],
                "subject": "Quarterly report",
                "body": "Draft body",
                "bodyHtml": "<p>Draft body</p>",
                "inReplyTo": "<abc@agents.useanima.sh>",
                "references": ["<abc@agents.useanima.sh>"],
                "metadata": {"k": "v"},
            },
            options=None,
        )
        assert isinstance(result, EmailDraftOutput)
        assert result.id == "draft_001"
        assert result.agent_id == "agent_001"
        assert result.subject == "Quarterly report"

    def test_create_incomplete_draft_sends_agent_id_only(self, mock_http: MagicMock) -> None:
        """Drafts may be incomplete — no recipients, subject, or body yet.

        Only agentId must go over the wire so the server doesn't reject the
        draft for empty optional fields.
        """
        mock_http.request.return_value = EMAIL_DRAFT_RAW
        EmailDraftsResource(mock_http).create(agent_id="agent_001")

        mock_http.request.assert_called_once_with(
            "POST", "/email/drafts", {"agentId": "agent_001"}, options=None
        )

    def test_create_parses_nullable_fields(self, mock_http: MagicMock) -> None:
        raw = {**EMAIL_DRAFT_RAW, "subject": None, "body": None, "fromIdentityId": None}
        mock_http.request.return_value = raw
        result = EmailDraftsResource(mock_http).create(agent_id="agent_001")

        assert result.subject is None
        assert result.body is None
        assert result.from_identity_id is None


class TestDraftsGet:
    def test_get(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = EMAIL_DRAFT_RAW
        result = EmailDraftsResource(mock_http).get("draft_001")

        mock_http.request.assert_called_once_with("GET", "/email/drafts/draft_001", options=None)
        assert isinstance(result, EmailDraftOutput)
        assert result.id == "draft_001"


class TestDraftsList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_DRAFTS_RAW
        result = EmailDraftsResource(mock_http).list()

        items = result.items  # trigger lazy fetch
        mock_http.request.assert_called_once_with("GET", "/email/drafts", query=None)
        assert len(items) == 1
        assert isinstance(items[0], EmailDraftOutput)

    def test_list_with_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_DRAFTS_RAW
        result = EmailDraftsResource(mock_http).list(
            cursor="cur_abc", limit=25, agent_id="agent_001"
        )

        _ = result.items
        _, kwargs = mock_http.request.call_args
        assert kwargs["query"] == {"cursor": "cur_abc", "limit": "25", "agentId": "agent_001"}

    def test_list_auto_pagination_follows_cursor(self, mock_http: MagicMock) -> None:
        page_one = {
            "items": [EMAIL_DRAFT_RAW],
            "pagination": {"nextCursor": "cur_2", "hasMore": True},
        }
        page_two = {
            "items": [{**EMAIL_DRAFT_RAW, "id": "draft_002"}],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        mock_http.request.side_effect = [page_one, page_two]

        ids = [draft.id for draft in EmailDraftsResource(mock_http).list()]

        assert ids == ["draft_001", "draft_002"]
        assert mock_http.request.call_count == 2
        assert mock_http.request.call_args_list[1][1]["query"]["cursor"] == "cur_2"


class TestDraftsSend:
    def test_send_posts_without_body_and_returns_message(self, mock_http: MagicMock) -> None:
        """Send converts the draft into a Message atomically.

        The endpoint takes no request body (the draft id is in the path), and
        the response is the newly created Message — callers must get back a
        MessageOutput with delivery state, not the draft they started from.
        """
        mock_http.request.return_value = MESSAGE_RAW
        result = EmailDraftsResource(mock_http).send("draft_001")

        mock_http.request.assert_called_once_with(
            "POST", "/email/drafts/draft_001/send", options=None
        )
        assert isinstance(result, MessageOutput)
        assert result.id == "msg_001"
        assert result.status.value == "SENT"


class TestDraftsDelete:
    def test_delete_returns_deleted_draft(self, mock_http: MagicMock) -> None:
        """Delete returns the discarded draft's final state (unlike inbox
        delete, which returns nothing) so callers can log what was thrown
        away."""
        mock_http.request.return_value = EMAIL_DRAFT_RAW
        result = EmailDraftsResource(mock_http).delete("draft_001")

        mock_http.request.assert_called_once_with("DELETE", "/email/drafts/draft_001", options=None)
        assert isinstance(result, EmailDraftOutput)
        assert result.id == "draft_001"


class TestAsyncDrafts:
    @pytest.mark.asyncio
    async def test_create(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = EMAIL_DRAFT_RAW
        result = await AsyncEmailDraftsResource(mock_http).create(
            agent_id="agent_001", to=["user@example.com"], subject="Quarterly report"
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/email/drafts",
            {
                "agentId": "agent_001",
                "to": ["user@example.com"],
                "subject": "Quarterly report",
            },
            options=None,
        )
        assert isinstance(result, EmailDraftOutput)

    @pytest.mark.asyncio
    async def test_get(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = EMAIL_DRAFT_RAW
        result = await AsyncEmailDraftsResource(mock_http).get("draft_001")

        mock_http.request.assert_called_once_with("GET", "/email/drafts/draft_001", options=None)
        assert result.id == "draft_001"

    @pytest.mark.asyncio
    async def test_list_async_iteration(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = PAGINATED_DRAFTS_RAW
        ids = [draft.id async for draft in AsyncEmailDraftsResource(mock_http).list(limit=10)]

        assert ids == ["draft_001"]
        mock_http.request.assert_called_once_with("GET", "/email/drafts", query={"limit": "10"})

    @pytest.mark.asyncio
    async def test_send(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = MESSAGE_RAW
        result = await AsyncEmailDraftsResource(mock_http).send("draft_001")

        mock_http.request.assert_called_once_with(
            "POST", "/email/drafts/draft_001/send", options=None
        )
        assert isinstance(result, MessageOutput)

    @pytest.mark.asyncio
    async def test_delete(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = EMAIL_DRAFT_RAW
        result = await AsyncEmailDraftsResource(mock_http).delete("draft_001")

        mock_http.request.assert_called_once_with("DELETE", "/email/drafts/draft_001", options=None)
        assert isinstance(result, EmailDraftOutput)


class TestClientWiring:
    def test_sync_client_exposes_drafts_under_emails(self) -> None:
        from anima import Anima

        client = Anima(api_key="sk-test")
        try:
            assert isinstance(client.emails.drafts, EmailDraftsResource)
        finally:
            client.close()

    @pytest.mark.asyncio
    async def test_async_client_exposes_drafts_under_emails(self) -> None:
        from anima import AsyncAnima

        client = AsyncAnima(api_key="sk-test")
        try:
            assert isinstance(client.emails.drafts, AsyncEmailDraftsResource)
        finally:
            await client.close()
