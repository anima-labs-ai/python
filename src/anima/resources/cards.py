from __future__ import annotations

from typing import Any, Literal

from .._http import AsyncHTTPClient, HTTPClient
from .._types import (
    ApprovalList,
    Card,
    CardApproval,
    CardList,
    CardTransaction,
    KillSwitchResult,
    SpendingPolicy,
    TransactionList,
)


def _to_query(params: dict[str, Any] | None) -> dict[str, str] | None:
    if not params:
        return None
    query: dict[str, str] = {}
    for key, value in params.items():
        if value is not None:
            query[key] = str(value)
    return query or None


class CardsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        agent_id: str,
        card_type: str = "VIRTUAL",
        currency: str = "usd",
        label: str | None = None,
        spend_limit_daily: int | None = None,
        spend_limit_monthly: int | None = None,
        spend_limit_per_auth: int | None = None,
    ) -> Card:
        body: dict[str, Any] = {
            "agentId": agent_id,
            "cardType": card_type,
            "currency": currency,
        }
        if label is not None:
            body["label"] = label
        if spend_limit_daily is not None:
            body["spendLimitDaily"] = spend_limit_daily
        if spend_limit_monthly is not None:
            body["spendLimitMonthly"] = spend_limit_monthly
        if spend_limit_per_auth is not None:
            body["spendLimitPerAuth"] = spend_limit_per_auth
        return Card.model_validate(self._client.request("POST", "/cards", body))

    def get(self, card_id: str) -> Card:
        return Card.model_validate(self._client.request("GET", f"/cards/{card_id}"))

    def list(
        self,
        *,
        agent_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> CardList:
        return CardList.model_validate(
            self._client.request(
                "GET",
                "/cards",
                query=_to_query(
                    {"agentId": agent_id, "status": status, "cursor": cursor, "limit": limit}
                ),
            )
        )

    def update(
        self,
        card_id: str,
        *,
        label: str | None = None,
        spend_limit_daily: int | None = None,
        spend_limit_monthly: int | None = None,
        spend_limit_per_auth: int | None = None,
    ) -> Card:
        body: dict[str, Any] = {}
        if label is not None:
            body["label"] = label
        if spend_limit_daily is not None:
            body["spendLimitDaily"] = spend_limit_daily
        if spend_limit_monthly is not None:
            body["spendLimitMonthly"] = spend_limit_monthly
        if spend_limit_per_auth is not None:
            body["spendLimitPerAuth"] = spend_limit_per_auth
        return Card.model_validate(self._client.request("PATCH", f"/cards/{card_id}", body))

    def delete(self, card_id: str) -> None:
        self._client.request("DELETE", f"/cards/{card_id}")

    def freeze(self, card_id: str) -> Card:
        return Card.model_validate(self._client.request("POST", f"/cards/{card_id}/freeze"))

    def unfreeze(self, card_id: str) -> Card:
        return Card.model_validate(self._client.request("POST", f"/cards/{card_id}/unfreeze"))

    def create_policy(
        self,
        card_id: str,
        *,
        name: str,
        priority: int,
        action: str,
        max_amount_cents: int | None = None,
        min_amount_cents: int | None = None,
        allowed_categories: list[str] | None = None,
        blocked_categories: list[str] | None = None,
        allowed_merchants: list[str] | None = None,
        blocked_merchants: list[str] | None = None,
        allowed_countries: list[str] | None = None,
        blocked_countries: list[str] | None = None,
    ) -> SpendingPolicy:
        body: dict[str, Any] = {
            "cardId": card_id,
            "name": name,
            "priority": priority,
            "action": action,
        }
        if max_amount_cents is not None:
            body["maxAmountCents"] = max_amount_cents
        if min_amount_cents is not None:
            body["minAmountCents"] = min_amount_cents
        if allowed_categories is not None:
            body["allowedCategories"] = allowed_categories
        if blocked_categories is not None:
            body["blockedCategories"] = blocked_categories
        if allowed_merchants is not None:
            body["allowedMerchants"] = allowed_merchants
        if blocked_merchants is not None:
            body["blockedMerchants"] = blocked_merchants
        if allowed_countries is not None:
            body["allowedCountries"] = allowed_countries
        if blocked_countries is not None:
            body["blockedCountries"] = blocked_countries
        return SpendingPolicy.model_validate(self._client.request("POST", "/cards/policies", body))

    def list_policies(self, card_id: str) -> list[SpendingPolicy]:
        raw = self._client.request("GET", "/cards/policies", query={"cardId": card_id})
        items = raw if isinstance(raw, list) else raw.get("items", raw)
        return [SpendingPolicy.model_validate(item) for item in items]

    def update_policy(
        self,
        policy_id: str,
        *,
        name: str | None = None,
        priority: int | None = None,
        action: str | None = None,
        max_amount_cents: int | None = None,
        min_amount_cents: int | None = None,
        allowed_categories: list[str] | None = None,
        blocked_categories: list[str] | None = None,
        allowed_merchants: list[str] | None = None,
        blocked_merchants: list[str] | None = None,
        allowed_countries: list[str] | None = None,
        blocked_countries: list[str] | None = None,
    ) -> SpendingPolicy:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if priority is not None:
            body["priority"] = priority
        if action is not None:
            body["action"] = action
        if max_amount_cents is not None:
            body["maxAmountCents"] = max_amount_cents
        if min_amount_cents is not None:
            body["minAmountCents"] = min_amount_cents
        if allowed_categories is not None:
            body["allowedCategories"] = allowed_categories
        if blocked_categories is not None:
            body["blockedCategories"] = blocked_categories
        if allowed_merchants is not None:
            body["allowedMerchants"] = allowed_merchants
        if blocked_merchants is not None:
            body["blockedMerchants"] = blocked_merchants
        if allowed_countries is not None:
            body["allowedCountries"] = allowed_countries
        if blocked_countries is not None:
            body["blockedCountries"] = blocked_countries
        return SpendingPolicy.model_validate(
            self._client.request("PATCH", f"/cards/policies/{policy_id}", body)
        )

    def delete_policy(self, policy_id: str) -> None:
        self._client.request("DELETE", f"/cards/policies/{policy_id}")

    def list_transactions(
        self,
        *,
        card_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> TransactionList:
        return TransactionList.model_validate(
            self._client.request(
                "GET",
                "/cards/transactions",
                query=_to_query(
                    {"cardId": card_id, "status": status, "cursor": cursor, "limit": limit}
                ),
            )
        )

    def get_transaction(self, transaction_id: str) -> CardTransaction:
        return CardTransaction.model_validate(
            self._client.request("GET", f"/cards/transactions/{transaction_id}")
        )

    def kill_switch(
        self,
        *,
        agent_id: str | None = None,
        active: bool,
    ) -> KillSwitchResult:
        body: dict[str, Any] = {"active": active}
        if agent_id is not None:
            body["agentId"] = agent_id
        return KillSwitchResult.model_validate(
            self._client.request("POST", "/cards/kill-switch", body)
        )

    def list_approvals(
        self,
        *,
        card_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> ApprovalList:
        return ApprovalList.model_validate(
            self._client.request(
                "GET",
                "/cards/approvals",
                query=_to_query(
                    {"cardId": card_id, "status": status, "cursor": cursor, "limit": limit}
                ),
            )
        )

    def decide_approval(
        self,
        approval_id: str,
        decision: Literal["APPROVED", "DECLINED"],
    ) -> CardApproval:
        return CardApproval.model_validate(
            self._client.request(
                "POST", f"/cards/approvals/{approval_id}/decision", {"decision": decision}
            )
        )


class AsyncCardsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        agent_id: str,
        card_type: str = "VIRTUAL",
        currency: str = "usd",
        label: str | None = None,
        spend_limit_daily: int | None = None,
        spend_limit_monthly: int | None = None,
        spend_limit_per_auth: int | None = None,
    ) -> Card:
        body: dict[str, Any] = {
            "agentId": agent_id,
            "cardType": card_type,
            "currency": currency,
        }
        if label is not None:
            body["label"] = label
        if spend_limit_daily is not None:
            body["spendLimitDaily"] = spend_limit_daily
        if spend_limit_monthly is not None:
            body["spendLimitMonthly"] = spend_limit_monthly
        if spend_limit_per_auth is not None:
            body["spendLimitPerAuth"] = spend_limit_per_auth
        return Card.model_validate(await self._client.request("POST", "/cards", body))

    async def get(self, card_id: str) -> Card:
        return Card.model_validate(await self._client.request("GET", f"/cards/{card_id}"))

    async def list(
        self,
        *,
        agent_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> CardList:
        return CardList.model_validate(
            await self._client.request(
                "GET",
                "/cards",
                query=_to_query(
                    {"agentId": agent_id, "status": status, "cursor": cursor, "limit": limit}
                ),
            )
        )

    async def update(
        self,
        card_id: str,
        *,
        label: str | None = None,
        spend_limit_daily: int | None = None,
        spend_limit_monthly: int | None = None,
        spend_limit_per_auth: int | None = None,
    ) -> Card:
        body: dict[str, Any] = {}
        if label is not None:
            body["label"] = label
        if spend_limit_daily is not None:
            body["spendLimitDaily"] = spend_limit_daily
        if spend_limit_monthly is not None:
            body["spendLimitMonthly"] = spend_limit_monthly
        if spend_limit_per_auth is not None:
            body["spendLimitPerAuth"] = spend_limit_per_auth
        return Card.model_validate(await self._client.request("PATCH", f"/cards/{card_id}", body))

    async def delete(self, card_id: str) -> None:
        await self._client.request("DELETE", f"/cards/{card_id}")

    async def freeze(self, card_id: str) -> Card:
        return Card.model_validate(await self._client.request("POST", f"/cards/{card_id}/freeze"))

    async def unfreeze(self, card_id: str) -> Card:
        return Card.model_validate(await self._client.request("POST", f"/cards/{card_id}/unfreeze"))

    async def create_policy(
        self,
        card_id: str,
        *,
        name: str,
        priority: int,
        action: str,
        max_amount_cents: int | None = None,
        min_amount_cents: int | None = None,
        allowed_categories: list[str] | None = None,
        blocked_categories: list[str] | None = None,
        allowed_merchants: list[str] | None = None,
        blocked_merchants: list[str] | None = None,
        allowed_countries: list[str] | None = None,
        blocked_countries: list[str] | None = None,
    ) -> SpendingPolicy:
        body: dict[str, Any] = {
            "cardId": card_id,
            "name": name,
            "priority": priority,
            "action": action,
        }
        if max_amount_cents is not None:
            body["maxAmountCents"] = max_amount_cents
        if min_amount_cents is not None:
            body["minAmountCents"] = min_amount_cents
        if allowed_categories is not None:
            body["allowedCategories"] = allowed_categories
        if blocked_categories is not None:
            body["blockedCategories"] = blocked_categories
        if allowed_merchants is not None:
            body["allowedMerchants"] = allowed_merchants
        if blocked_merchants is not None:
            body["blockedMerchants"] = blocked_merchants
        if allowed_countries is not None:
            body["allowedCountries"] = allowed_countries
        if blocked_countries is not None:
            body["blockedCountries"] = blocked_countries
        return SpendingPolicy.model_validate(
            await self._client.request("POST", "/cards/policies", body)
        )

    async def list_policies(self, card_id: str) -> list[SpendingPolicy]:
        raw = await self._client.request("GET", "/cards/policies", query={"cardId": card_id})
        items = raw if isinstance(raw, list) else raw.get("items", raw)
        return [SpendingPolicy.model_validate(item) for item in items]

    async def update_policy(
        self,
        policy_id: str,
        *,
        name: str | None = None,
        priority: int | None = None,
        action: str | None = None,
        max_amount_cents: int | None = None,
        min_amount_cents: int | None = None,
        allowed_categories: list[str] | None = None,
        blocked_categories: list[str] | None = None,
        allowed_merchants: list[str] | None = None,
        blocked_merchants: list[str] | None = None,
        allowed_countries: list[str] | None = None,
        blocked_countries: list[str] | None = None,
    ) -> SpendingPolicy:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if priority is not None:
            body["priority"] = priority
        if action is not None:
            body["action"] = action
        if max_amount_cents is not None:
            body["maxAmountCents"] = max_amount_cents
        if min_amount_cents is not None:
            body["minAmountCents"] = min_amount_cents
        if allowed_categories is not None:
            body["allowedCategories"] = allowed_categories
        if blocked_categories is not None:
            body["blockedCategories"] = blocked_categories
        if allowed_merchants is not None:
            body["allowedMerchants"] = allowed_merchants
        if blocked_merchants is not None:
            body["blockedMerchants"] = blocked_merchants
        if allowed_countries is not None:
            body["allowedCountries"] = allowed_countries
        if blocked_countries is not None:
            body["blockedCountries"] = blocked_countries
        return SpendingPolicy.model_validate(
            await self._client.request("PATCH", f"/cards/policies/{policy_id}", body)
        )

    async def delete_policy(self, policy_id: str) -> None:
        await self._client.request("DELETE", f"/cards/policies/{policy_id}")

    async def list_transactions(
        self,
        *,
        card_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> TransactionList:
        return TransactionList.model_validate(
            await self._client.request(
                "GET",
                "/cards/transactions",
                query=_to_query(
                    {"cardId": card_id, "status": status, "cursor": cursor, "limit": limit}
                ),
            )
        )

    async def get_transaction(self, transaction_id: str) -> CardTransaction:
        return CardTransaction.model_validate(
            await self._client.request("GET", f"/cards/transactions/{transaction_id}")
        )

    async def kill_switch(
        self,
        *,
        agent_id: str | None = None,
        active: bool,
    ) -> KillSwitchResult:
        body: dict[str, Any] = {"active": active}
        if agent_id is not None:
            body["agentId"] = agent_id
        return KillSwitchResult.model_validate(
            await self._client.request("POST", "/cards/kill-switch", body)
        )

    async def list_approvals(
        self,
        *,
        card_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> ApprovalList:
        return ApprovalList.model_validate(
            await self._client.request(
                "GET",
                "/cards/approvals",
                query=_to_query(
                    {"cardId": card_id, "status": status, "cursor": cursor, "limit": limit}
                ),
            )
        )

    async def decide_approval(
        self,
        approval_id: str,
        decision: Literal["APPROVED", "DECLINED"],
    ) -> CardApproval:
        return CardApproval.model_validate(
            await self._client.request(
                "POST",
                f"/cards/approvals/{approval_id}/decision",
                {"decision": decision},
            )
        )
