"""The org-wide number list and the SMS conversation surface.

Added when the anima contracts gained ``phone.listIdentities`` and
``phone.smsThreadStats``; the four SMS routes alongside them had been declared
and served since spec F2/F3 with no SDK method reaching them at all.

Payloads are transcribed from packages/contracts/src/schemas/phone.ts. Because
every response goes through ``model_validate``, a field this SDK gets wrong
raises here rather than decoding to a zero value the way Go and TypeScript do.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import PhoneIdentityListItem, SmsThreadList
from anima.resources.phones import AsyncPhonesResource, PhonesResource

PHONE_IDENTITY_ITEM_RAW: dict[str, Any] = {
    "id": "pi_001",
    "phoneNumber": "+15551234567",
    "providerId": None,
    "capabilities": {"sms": True, "mms": False, "voice": True},
    "tenDlcStatus": "UNREGISTERED",
    "isPrimary": True,
    "voiceId": None,
    "createdAt": "2026-08-20T00:00:00Z",
    "agentId": "agent_001",
    "agentName": "Support",
    "agentSlug": "support",
}

SMS_THREAD_RAW: dict[str, Any] = {
    "threadId": "msg_001",
    "agentId": "agent_001",
    "participantAddress": "+15550001",
    "agentAddress": "+15551234567",
    "lastMessageAt": "2026-08-20T00:00:00Z",
    "lastMessageSnippet": "thanks!",
    "lastMessageDirection": "INBOUND",
    "messageCount": 3,
    "unreadCount": 1,
}


class TestListIdentities:
    def test_path_and_query(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [PHONE_IDENTITY_ITEM_RAW],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        page = PhonesResource(mock_http).list_identities(query="555-123", agent_id="agent_001")

        items = page.items  # trigger the lazy fetch
        _, kwargs = mock_http.request.call_args
        assert mock_http.request.call_args[0][:2] == ("GET", "/phone/identities")
        assert kwargs["query"] == {"query": "555-123", "agentId": "agent_001"}
        assert isinstance(items[0], PhoneIdentityListItem)
        # Both halves must decode: the inherited number and the joined agent.
        # This list exists so a caller need not fetch agents and join by hand.
        assert items[0].phone_number == "+15551234567"
        assert items[0].agent_name == "Support"


class TestListSmsThreads:
    def test_offset_envelope_is_preserved(self, mock_http: MagicMock) -> None:
        """{items, total, hasMore} — neither cursor envelope.

        Validating this against PaginatedResponse raises (no ``pagination``)
        and against CursorPage loses ``has_more``, which would report the first
        page as the whole list.
        """
        mock_http.request.return_value = {
            "items": [SMS_THREAD_RAW],
            "total": 57,
            "hasMore": True,
        }
        result = PhonesResource(mock_http).list_sms_threads(
            agent_id="agent_001", limit=20, offset=40
        )

        assert isinstance(result, SmsThreadList)
        assert result.total == 57
        assert result.has_more is True
        assert result.items[0].last_message_direction == "INBOUND"
        _, kwargs = mock_http.request.call_args
        assert kwargs["query"] == {"agentId": "agent_001", "limit": "20", "offset": "40"}

    @pytest.mark.parametrize(
        ("unread", "expected"),
        [(None, {}), (False, {"unread": "false"}), (True, {"unread": "true"})],
    )
    def test_explicit_unread_survives_encoding(
        self, mock_http: MagicMock, unread: bool | None, expected: dict[str, str]
    ) -> None:
        """An explicit ``unread=False`` reaches the wire.

        The obvious truthiness check drops it. The API gates on
        ``params.unread ? ...`` and treats absent and false alike today, so
        this pins the encoding rather than a live bug -- the request log
        matches the call, and the day either side stops treating the two alike
        it fails here instead of in someone's thread list.
        """
        mock_http.request.return_value = {"items": [], "total": 0, "hasMore": False}
        PhonesResource(mock_http).list_sms_threads(unread=unread)

        _, kwargs = mock_http.request.call_args
        assert kwargs["query"] == (expected or None)


class TestGetSmsThread:
    def test_path_and_limit(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "threadId": "msg_001",
            "agentId": "agent_001",
            "participantAddress": "+15550001",
            "agentAddress": "+15551234567",
            "messages": [],
            "messageCount": 3,
            "hasMore": True,
        }
        thread = PhonesResource(mock_http).get_sms_thread("msg_001", limit=25)

        assert mock_http.request.call_args[0][:2] == ("GET", "/phone/sms/threads/msg_001")
        assert mock_http.request.call_args[1]["query"] == {"limit": "25"}
        assert thread.has_more is True


class TestSmsThreadStats:
    def test_nullable_last_message(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [
                {
                    "agentId": "agent_001",
                    "conversations": 4,
                    "unread": 2,
                    "lastMessageAt": "2026-08-20T00:00:00Z",
                },
                # An agent with no messages reports null, not a missing key.
                {"agentId": "agent_002", "conversations": 0, "unread": 0, "lastMessageAt": None},
            ]
        }
        stats = PhonesResource(mock_http).sms_thread_stats(agent_id="agent_001")

        assert mock_http.request.call_args[0][:2] == ("GET", "/phone/sms/stats")
        assert stats.items[0].unread == 2
        assert stats.items[1].last_message_at is None


class TestSmsSuppressions:
    def test_list_parses_a_workspace_wide_entry(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [
                {
                    "id": "sup_001",
                    "phoneNumber": "+15550001",
                    # None is the common case: a STOP applies to the org, not
                    # to whichever agent happened to be texting.
                    "agentId": None,
                    "reason": "STOP_KEYWORD",
                    "source": "inbound-stop-keyword",
                    "createdAt": "2026-08-20T00:00:00Z",
                }
            ],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        page = PhonesResource(mock_http).list_sms_suppressions(phone_number="+15550001")

        items = page.items
        assert mock_http.request.call_args[0][:2] == ("GET", "/phone/sms-suppressions")
        assert mock_http.request.call_args[1]["query"] == {"phoneNumber": "+15550001"}
        assert items[0].agent_id is None
        assert items[0].reason == "STOP_KEYWORD"

    def test_unsuppress_posts_the_number(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"phoneNumber": "+15550001", "removed": 2}
        result = PhonesResource(mock_http).unsuppress_sms(phone_number="+15550001")

        mock_http.request.assert_called_once_with(
            "POST", "/phone/sms-unsuppress", {"phoneNumber": "+15550001"}, options=None
        )
        assert result.removed == 2


class TestAsyncPhones:
    @pytest.mark.asyncio
    async def test_list_sms_threads(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = {"items": [SMS_THREAD_RAW], "total": 1, "hasMore": False}
        result = await AsyncPhonesResource(mock_http).list_sms_threads(limit=5)

        assert result.items[0].thread_id == "msg_001"
        assert mock_http.request.call_args[1]["query"] == {"limit": "5"}

    @pytest.mark.asyncio
    async def test_list_identities_iterates(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = {
            "items": [PHONE_IDENTITY_ITEM_RAW],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        names = [item.agent_name async for item in AsyncPhonesResource(mock_http).list_identities()]

        assert names == ["Support"]


class TestTenDlcStatus:
    """UNREGISTERED must parse.

    The contract has carried it since anima #314 (2026-07-17) and calls it "the
    state every newly provisioned US long code starts in", but all three SDKs
    omitted it. Here that was not a cosmetic gap: every response carrying it
    raised ValidationError, so `phones.provision()` and `phones.list()` both
    failed outright on a fresh US number.

    The drift canary cannot see this class of bug — it diffs the pinned commit
    against HEAD, and this landed before the pin.
    """

    @pytest.mark.parametrize(
        "status", ["PENDING", "REGISTERED", "REJECTED", "NOT_REQUIRED", "UNREGISTERED"]
    )
    def test_every_contract_value_parses(self, mock_http: MagicMock, status: str) -> None:
        mock_http.request.return_value = {
            "items": [{**PHONE_IDENTITY_ITEM_RAW, "tenDlcStatus": status}],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        page = PhonesResource(mock_http).list_identities()

        assert page.items[0].ten_dlc_status.value == status
