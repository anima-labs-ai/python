"""Tests for B3 labels + read state on the Python SDK.

Labels are the agent's workflow state machine: without them every list returns
the same undifferentiated stream forever. anima#307 shipped them server-side;
these tests pin the client half — that a label filter reaches the API in the ONE
shape it reads, and that update_labels cannot report success for a no-op.

The shape matters more than it looks. `,`.join() would ask for a single label
literally named "urgent,unread", which matches nothing — the caller gets a
silently empty inbox rather than an error, and no type checker can see it.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima.resources.emails import EmailsResource
from anima.resources.messages import AsyncMessagesResource, MessagesResource

from .conftest import MESSAGE_RAW

LIST_RAW: dict[str, Any] = {
    "items": [MESSAGE_RAW],
    "pagination": {"nextCursor": None, "hasMore": False},
}


def _query_of(mock: MagicMock) -> dict[str, Any]:
    """The `query` kwarg the resource handed the HTTP client."""
    return mock.request.call_args.kwargs["query"]


class TestListLabelFilters:
    def test_labels_stay_a_list_so_httpx_repeats_the_key(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = LIST_RAW
        items = MessagesResource(mock_http).list(labels=["urgent", "unread"]).items

        assert len(items) == 1

        # A str here (",".join) would request one label named "urgent,unread".
        assert _query_of(mock_http)["labels"] == ["urgent", "unread"]

    def test_a_single_label_is_still_a_list(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = LIST_RAW
        items = MessagesResource(mock_http).list(labels=["unread"]).items

        assert len(items) == 1

        # `?labels=unread` — the most common label call — 400'd until anima#309
        # taught the contract to accept a lone value.
        assert _query_of(mock_http)["labels"] == ["unread"]

    def test_include_spam_false_is_transmitted(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = LIST_RAW
        items = MessagesResource(mock_http).list(include_spam=False).items

        assert len(items) == 1

        # An explicit False is the caller overriding; a truthiness check would
        # drop it and silently apply the server default instead.
        assert _query_of(mock_http)["includeSpam"] == "false"

    def test_no_label_params_means_no_label_keys(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = LIST_RAW
        items = MessagesResource(mock_http).list().items

        assert len(items) == 1

        query = _query_of(mock_http) or {}
        assert "labels" not in query
        assert "includeSpam" not in query

    def test_emails_list_carries_labels_identically(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = LIST_RAW
        items = EmailsResource(mock_http).list(labels=["archived"]).items

        assert len(items) == 1

        # The two surfaces must not drift on what a label filter means.
        assert mock_http.request.call_args.args[1] == "/email"
        assert _query_of(mock_http)["labels"] == ["archived"]


class TestSearchLabelFilters:
    def test_labels_nest_into_search_filters(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = LIST_RAW
        MessagesResource(mock_http).search("invoice", labels=["unread"], include_spam=True)

        payload = mock_http.request.call_args.args[2]
        assert payload["filters"]["labels"] == ["unread"]
        assert payload["filters"]["includeSpam"] is True


class TestUpdateLabels:
    def test_patches_the_labels_route_with_both_operations(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {**MESSAGE_RAW, "labels": ["read"]}
        result = MessagesResource(mock_http).update_labels(
            "msg_001", add_labels=["read"], remove_labels=["unread"]
        )

        method, path, payload = mock_http.request.call_args.args[:3]
        assert method == "PATCH"
        assert path == "/messages/msg_001/labels"
        # `id` rides in the body as well as the path: the contract's input
        # schema requires it.
        assert payload == {"id": "msg_001", "addLabels": ["read"], "removeLabels": ["unread"]}
        assert result.labels == ["read"]

    def test_omits_the_operation_not_asked_for(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = MESSAGE_RAW
        MessagesResource(mock_http).update_labels("msg_001", add_labels=["archived"])

        payload = mock_http.request.call_args.args[2]
        assert "removeLabels" not in payload

    def test_empty_call_raises_before_the_request(self, mock_http: MagicMock) -> None:
        # The failure this prevents: an agent "marks the message read", gets a
        # success back, and nothing changed.
        with pytest.raises(ValueError, match="at least one of add_labels or remove_labels"):
            MessagesResource(mock_http).update_labels("msg_001")
        mock_http.request.assert_not_called()

    def test_empty_lists_count_as_absent(self, mock_http: MagicMock) -> None:
        with pytest.raises(ValueError, match="at least one of add_labels or remove_labels"):
            MessagesResource(mock_http).update_labels("msg_001", add_labels=[], remove_labels=[])


class TestMessageOutputLabels:
    def test_labels_parse_off_the_wire(self) -> None:
        from anima._types import MessageOutput

        msg = MessageOutput.model_validate({**MESSAGE_RAW, "labels": ["unread", "urgent"]})
        assert msg.labels == ["unread", "urgent"]

    def test_labels_default_to_empty_for_a_pre_b3_api(self) -> None:
        from anima._types import MessageOutput

        # An API older than B3 sends no `labels` key. Defaulting keeps this
        # client parsing rather than raising on every message.
        assert MessageOutput.model_validate(MESSAGE_RAW).labels == []


class TestAsyncParity:
    @pytest.mark.asyncio
    async def test_async_update_labels_hits_the_same_route(self) -> None:
        client = MagicMock(spec=AsyncHTTPClient)
        client.request = AsyncMock(return_value={**MESSAGE_RAW, "labels": ["read"]})
        await AsyncMessagesResource(client).update_labels("msg_001", add_labels=["read"])

        method, path, payload = client.request.call_args.args[:3]
        assert (method, path) == ("PATCH", "/messages/msg_001/labels")
        assert payload["addLabels"] == ["read"]

    @pytest.mark.asyncio
    async def test_async_list_sends_labels_as_a_list(self) -> None:
        # The async class is a hand-maintained mirror of the sync one, so the
        # two drift silently unless both are driven.
        client = MagicMock(spec=AsyncHTTPClient)
        client.request = AsyncMock(return_value=LIST_RAW)
        # AsyncPageIterator fetches on await; .items is only valid afterwards.
        await AsyncMessagesResource(client).list(labels=["unread"])

        assert client.request.call_args.kwargs["query"]["labels"] == ["unread"]
