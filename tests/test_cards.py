"""Tests for CardsResource with mocked HTTP."""

from __future__ import annotations

from unittest.mock import MagicMock

from anima._types import (
    ApprovalList,
    Card,
    CardApproval,
    CardList,
    CardTransaction,
    KillSwitchResult,
    SpendingPolicy,
    TransactionList,
)
from anima.resources.cards import CardsResource

from .conftest import (
    APPROVAL_LIST_RAW,
    APPROVAL_RAW,
    CARD_LIST_RAW,
    CARD_RAW,
    KILL_SWITCH_RAW,
    SPENDING_POLICY_RAW,
    TRANSACTION_LIST_RAW,
    TRANSACTION_RAW,
)


class TestCardsCreate:
    def test_create_minimal(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_RAW
        resource = CardsResource(mock_http)
        result = resource.create(agent_id="agent_001")

        call_body = mock_http.request.call_args[0][2]
        assert call_body["agentId"] == "agent_001"
        assert call_body["cardType"] == "VIRTUAL"
        assert call_body["currency"] == "usd"
        assert isinstance(result, Card)
        assert result.id == "card_001"

    def test_create_with_limits(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_RAW
        resource = CardsResource(mock_http)
        resource.create(
            agent_id="agent_001",
            label="My Card",
            spend_limit_daily=10000,
            spend_limit_monthly=50000,
            spend_limit_per_auth=5000,
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["label"] == "My Card"
        assert call_body["spendLimitDaily"] == 10000
        assert call_body["spendLimitMonthly"] == 50000
        assert call_body["spendLimitPerAuth"] == 5000


class TestCardsGet:
    def test_get(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_RAW
        resource = CardsResource(mock_http)
        result = resource.get("card_001")

        mock_http.request.assert_called_once_with("GET", "/cards/card_001", options=None)
        assert isinstance(result, Card)
        assert result.last4 == "4242"
        assert result.brand == "Visa"
        assert result.exp_month == 12
        assert result.exp_year == 2027


class TestCardsList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_LIST_RAW
        resource = CardsResource(mock_http)
        result = resource.list()

        assert isinstance(result, CardList)
        assert len(result.items) == 1

    def test_list_with_filters(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_LIST_RAW
        resource = CardsResource(mock_http)
        resource.list(agent_id="agent_001", status="ACTIVE", limit=10)

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["agentId"] == "agent_001"
        assert query["status"] == "ACTIVE"
        assert query["limit"] == "10"


class TestCardsUpdate:
    def test_update_label(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_RAW
        resource = CardsResource(mock_http)
        result = resource.update("card_001", label="New Label")

        mock_http.request.assert_called_once_with(
            "PATCH", "/cards/card_001", {"label": "New Label"}, options=None
        )
        assert isinstance(result, Card)

    def test_update_omits_none(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_RAW
        resource = CardsResource(mock_http)
        resource.update("card_001", spend_limit_daily=5000)

        call_body = mock_http.request.call_args[0][2]
        assert "label" not in call_body
        assert call_body["spendLimitDaily"] == 5000


class TestCardsDelete:
    def test_delete(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = None
        resource = CardsResource(mock_http)
        resource.delete("card_001")

        mock_http.request.assert_called_once_with("DELETE", "/cards/card_001", options=None)


class TestCardsFreezeUnfreeze:
    def test_freeze(self, mock_http: MagicMock) -> None:
        frozen = {**CARD_RAW, "status": "FROZEN"}
        mock_http.request.return_value = frozen
        resource = CardsResource(mock_http)
        result = resource.freeze("card_001")

        mock_http.request.assert_called_once_with("POST", "/cards/card_001/freeze", options=None)
        assert isinstance(result, Card)

    def test_unfreeze(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CARD_RAW
        resource = CardsResource(mock_http)
        result = resource.unfreeze("card_001")

        mock_http.request.assert_called_once_with("POST", "/cards/card_001/unfreeze", options=None)
        assert isinstance(result, Card)


class TestCardsTransactions:
    def test_list_transactions(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = TRANSACTION_LIST_RAW
        resource = CardsResource(mock_http)
        result = resource.list_transactions(card_id="card_001")

        assert isinstance(result, TransactionList)
        assert len(result.items) == 1

    def test_list_transactions_with_filters(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = TRANSACTION_LIST_RAW
        resource = CardsResource(mock_http)
        resource.list_transactions(card_id="card_001", status="APPROVED", limit=5)

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["cardId"] == "card_001"
        assert query["status"] == "APPROVED"

    def test_get_transaction(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = TRANSACTION_RAW
        resource = CardsResource(mock_http)
        result = resource.get_transaction("txn_001")

        mock_http.request.assert_called_once_with(
            "GET", "/cards/transactions/txn_001", options=None
        )
        assert isinstance(result, CardTransaction)
        assert result.amount_cents == 1500
        assert result.merchant_name == "Amazon"


class TestCardsPolicies:
    def test_create_policy(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = SPENDING_POLICY_RAW
        resource = CardsResource(mock_http)
        result = resource.create_policy(
            "card_001",
            name="Default Policy",
            priority=1,
            action="AUTO_APPROVE",
            max_amount_cents=10000,
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["cardId"] == "card_001"
        assert call_body["name"] == "Default Policy"
        assert call_body["maxAmountCents"] == 10000
        assert isinstance(result, SpendingPolicy)

    def test_list_policies(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = [SPENDING_POLICY_RAW]
        resource = CardsResource(mock_http)
        result = resource.list_policies("card_001")

        assert len(result) == 1
        assert isinstance(result[0], SpendingPolicy)

    def test_list_policies_dict_response(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"items": [SPENDING_POLICY_RAW]}
        resource = CardsResource(mock_http)
        result = resource.list_policies("card_001")

        assert len(result) == 1

    def test_update_policy(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = SPENDING_POLICY_RAW
        resource = CardsResource(mock_http)
        result = resource.update_policy("pol_001", name="Updated", priority=2)

        call_body = mock_http.request.call_args[0][2]
        assert call_body["name"] == "Updated"
        assert call_body["priority"] == 2
        assert isinstance(result, SpendingPolicy)

    def test_delete_policy(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = None
        resource = CardsResource(mock_http)
        resource.delete_policy("pol_001")

        mock_http.request.assert_called_once_with("DELETE", "/cards/policies/pol_001", options=None)


class TestCardsKillSwitch:
    def test_kill_switch(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = KILL_SWITCH_RAW
        resource = CardsResource(mock_http)
        result = resource.kill_switch(active=True)

        call_body = mock_http.request.call_args[0][2]
        assert call_body["active"] is True
        assert isinstance(result, KillSwitchResult)
        assert result.affected == 3

    def test_kill_switch_with_agent_id(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = KILL_SWITCH_RAW
        resource = CardsResource(mock_http)
        resource.kill_switch(agent_id="agent_001", active=False)

        call_body = mock_http.request.call_args[0][2]
        assert call_body["agentId"] == "agent_001"
        assert call_body["active"] is False


class TestCardsApprovals:
    def test_list_approvals(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = APPROVAL_LIST_RAW
        resource = CardsResource(mock_http)
        result = resource.list_approvals(card_id="card_001")

        assert isinstance(result, ApprovalList)
        assert len(result.items) == 1

    def test_decide_approval(self, mock_http: MagicMock) -> None:
        decided = {**APPROVAL_RAW, "status": "APPROVED", "decidedBy": "user_001"}
        mock_http.request.return_value = decided
        resource = CardsResource(mock_http)
        result = resource.decide_approval("apr_001", "APPROVED")

        mock_http.request.assert_called_once_with(
            "POST",
            "/cards/approvals/apr_001/decision",
            {"decision": "APPROVED"},
            options=None,
        )
        assert isinstance(result, CardApproval)
