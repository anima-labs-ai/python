"""Tests for InboxesResource (create / get / list / update / delete)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import InboxOutput
from anima.resources.inboxes import AsyncInboxesResource, InboxesResource

from .conftest import INBOX_RAW, PAGINATED_INBOXES_RAW


class TestInboxesCreate:
    def test_create_with_all_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = INBOX_RAW
        resource = InboxesResource(mock_http)
        result = resource.create(
            username="support",
            domain="agents.useanima.sh",
            display_name="Support",
            agent_id="agent_001",
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/inboxes",
            {
                "username": "support",
                "domain": "agents.useanima.sh",
                "displayName": "Support",
                "agentId": "agent_001",
            },
            options=None,
        )
        assert isinstance(result, InboxOutput)
        assert result.id == "inbox_001"
        assert result.email == "support@agents.useanima.sh"
        assert result.local_part == "support"
        assert result.display_name == "Support"
        assert result.agent_id == "agent_001"

    def test_create_defaults_sends_empty_body(self, mock_http: MagicMock) -> None:
        """All create fields are optional — the server generates the address."""
        mock_http.request.return_value = INBOX_RAW
        InboxesResource(mock_http).create()

        mock_http.request.assert_called_once_with("POST", "/inboxes", {}, options=None)

    def test_create_parses_nullable_fields(self, mock_http: MagicMock) -> None:
        raw = {**INBOX_RAW, "displayName": None, "agentId": None}
        mock_http.request.return_value = raw
        result = InboxesResource(mock_http).create(username="bare")

        assert result.display_name is None
        assert result.agent_id is None


class TestInboxesGet:
    def test_get(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = INBOX_RAW
        result = InboxesResource(mock_http).get("inbox_001")

        mock_http.request.assert_called_once_with("GET", "/inboxes/inbox_001", options=None)
        assert isinstance(result, InboxOutput)
        assert result.id == "inbox_001"


class TestInboxesList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_INBOXES_RAW
        result = InboxesResource(mock_http).list()

        items = result.items  # trigger lazy fetch
        mock_http.request.assert_called_once_with("GET", "/inboxes", query=None)
        assert len(items) == 1
        assert isinstance(items[0], InboxOutput)
        assert result.pagination.has_more is False

    def test_list_with_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_INBOXES_RAW
        result = InboxesResource(mock_http).list(cursor="cur_abc", limit=50, query="supp")

        _ = result.items
        _, kwargs = mock_http.request.call_args
        assert kwargs["query"] == {"cursor": "cur_abc", "limit": "50", "query": "supp"}

    def test_list_auto_pagination_follows_cursor(self, mock_http: MagicMock) -> None:
        page_one = {
            "items": [INBOX_RAW],
            "pagination": {"nextCursor": "cur_2", "hasMore": True},
        }
        page_two = {
            "items": [{**INBOX_RAW, "id": "inbox_002"}],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        mock_http.request.side_effect = [page_one, page_two]

        ids = [inbox.id for inbox in InboxesResource(mock_http).list()]

        assert ids == ["inbox_001", "inbox_002"]
        assert mock_http.request.call_count == 2
        second_query = mock_http.request.call_args_list[1][1]["query"]
        assert second_query["cursor"] == "cur_2"


class TestInboxesUpdate:
    def test_update_display_name_and_agent(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = INBOX_RAW
        result = InboxesResource(mock_http).update(
            "inbox_001", display_name="Support", agent_id="agent_001"
        )

        mock_http.request.assert_called_once_with(
            "PATCH",
            "/inboxes/inbox_001",
            {"displayName": "Support", "agentId": "agent_001"},
            options=None,
        )
        assert isinstance(result, InboxOutput)

    def test_update_omits_unset_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = INBOX_RAW
        InboxesResource(mock_http).update("inbox_001", display_name="Only name")

        payload = mock_http.request.call_args[0][2]
        assert payload == {"displayName": "Only name"}


class TestInboxesDelete:
    def test_delete(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"success": True}
        result = InboxesResource(mock_http).delete("inbox_001")

        mock_http.request.assert_called_once_with("DELETE", "/inboxes/inbox_001", options=None)
        assert result is None


class TestAsyncInboxes:
    @pytest.mark.asyncio
    async def test_create(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = INBOX_RAW
        result = await AsyncInboxesResource(mock_http).create(
            username="support", agent_id="agent_001"
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/inboxes",
            {"username": "support", "agentId": "agent_001"},
            options=None,
        )
        assert isinstance(result, InboxOutput)
        assert result.email == "support@agents.useanima.sh"

    @pytest.mark.asyncio
    async def test_get(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = INBOX_RAW
        result = await AsyncInboxesResource(mock_http).get("inbox_001")

        mock_http.request.assert_called_once_with("GET", "/inboxes/inbox_001", options=None)
        assert result.id == "inbox_001"

    @pytest.mark.asyncio
    async def test_list_single_page_await(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = PAGINATED_INBOXES_RAW
        page = await AsyncInboxesResource(mock_http).list(limit=10)

        mock_http.request.assert_called_once_with("GET", "/inboxes", query={"limit": "10"})
        assert len(page.items) == 1
        assert page.items[0].id == "inbox_001"

    @pytest.mark.asyncio
    async def test_list_async_iteration(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = PAGINATED_INBOXES_RAW
        ids = [inbox.id async for inbox in AsyncInboxesResource(mock_http).list()]

        assert ids == ["inbox_001"]

    @pytest.mark.asyncio
    async def test_update(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = INBOX_RAW
        await AsyncInboxesResource(mock_http).update("inbox_001", display_name="Support")

        mock_http.request.assert_called_once_with(
            "PATCH",
            "/inboxes/inbox_001",
            {"displayName": "Support"},
            options=None,
        )

    @pytest.mark.asyncio
    async def test_delete(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = {"success": True}
        result = await AsyncInboxesResource(mock_http).delete("inbox_001")

        mock_http.request.assert_called_once_with("DELETE", "/inboxes/inbox_001", options=None)
        assert result is None


class TestClientWiring:
    def test_sync_client_exposes_inboxes(self) -> None:
        from anima import Anima

        client = Anima(api_key="sk-test")
        try:
            assert isinstance(client.inboxes, InboxesResource)
        finally:
            client.close()

    @pytest.mark.asyncio
    async def test_async_client_exposes_inboxes(self) -> None:
        from anima import AsyncAnima

        client = AsyncAnima(api_key="sk-test")
        try:
            assert isinstance(client.inboxes, AsyncInboxesResource)
        finally:
            await client.close()
