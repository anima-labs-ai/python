from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import (
    WalletOutput,
    WalletPayOutput,
    WalletTransactionOutput,
    X402FetchOutput,
)


def _to_tx_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    status: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if status is not None:
        params["status"] = status
    return params or None


def _build_pay_body(
    *,
    to: str,
    amount: float,
    currency: str | None = None,
    memo: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"to": to, "amount": amount}
    if currency is not None:
        body["currency"] = currency
    if memo is not None:
        body["memo"] = memo
    if metadata is not None:
        body["metadata"] = metadata
    return body


def _build_x402_body(
    *,
    url: str,
    method: str | None = None,
    headers: dict[str, str] | None = None,
    body: str | None = None,
    max_payment_amount: float | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"url": url}
    if method is not None:
        result["method"] = method
    if headers is not None:
        result["headers"] = headers
    if body is not None:
        result["body"] = body
    if max_payment_amount is not None:
        result["maxPaymentAmount"] = max_payment_amount
    return result


class WalletResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        agent_id: str,
        *,
        currency: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletOutput:
        body: dict[str, Any] = {}
        if currency is not None:
            body["currency"] = currency
        if metadata is not None:
            body["metadata"] = metadata
        return WalletOutput.model_validate(
            self._client.request("POST", f"/agents/{agent_id}/wallet", body or None)
        )

    def get(self, agent_id: str) -> WalletOutput:
        return WalletOutput.model_validate(
            self._client.request("GET", f"/agents/{agent_id}/wallet")
        )

    def update(
        self,
        agent_id: str,
        *,
        metadata: dict[str, Any] | None = None,
        spend_limit_daily: float | None = None,
        spend_limit_monthly: float | None = None,
    ) -> WalletOutput:
        body: dict[str, Any] = {}
        if metadata is not None:
            body["metadata"] = metadata
        if spend_limit_daily is not None:
            body["spendLimitDaily"] = spend_limit_daily
        if spend_limit_monthly is not None:
            body["spendLimitMonthly"] = spend_limit_monthly
        return WalletOutput.model_validate(
            self._client.request("PUT", f"/agents/{agent_id}/wallet", body)
        )

    def pay(
        self,
        agent_id: str,
        *,
        to: str,
        amount: float,
        currency: str | None = None,
        memo: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletPayOutput:
        body = _build_pay_body(
            to=to, amount=amount, currency=currency, memo=memo, metadata=metadata
        )
        return WalletPayOutput.model_validate(
            self._client.request("POST", f"/agents/{agent_id}/wallet/pay", body)
        )

    def x402_fetch(
        self,
        agent_id: str,
        *,
        url: str,
        method: str | None = None,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        max_payment_amount: float | None = None,
    ) -> X402FetchOutput:
        req_body = _build_x402_body(
            url=url, method=method, headers=headers, body=body,
            max_payment_amount=max_payment_amount,
        )
        return X402FetchOutput.model_validate(
            self._client.request("POST", f"/agents/{agent_id}/wallet/x402-fetch", req_body)
        )

    def transactions(
        self,
        agent_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: str | None = None,
    ) -> list[WalletTransactionOutput]:
        raw = self._client.request(
            "GET",
            f"/agents/{agent_id}/wallet/transactions",
            query=_to_tx_query(cursor=cursor, limit=limit, status=status),
        )
        return [WalletTransactionOutput.model_validate(item) for item in raw["items"]]

    def freeze(self, agent_id: str) -> None:
        self._client.request("POST", f"/agents/{agent_id}/wallet/freeze")

    def unfreeze(self, agent_id: str) -> None:
        self._client.request("POST", f"/agents/{agent_id}/wallet/unfreeze")


class AsyncWalletResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        agent_id: str,
        *,
        currency: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletOutput:
        body: dict[str, Any] = {}
        if currency is not None:
            body["currency"] = currency
        if metadata is not None:
            body["metadata"] = metadata
        return WalletOutput.model_validate(
            await self._client.request("POST", f"/agents/{agent_id}/wallet", body or None)
        )

    async def get(self, agent_id: str) -> WalletOutput:
        return WalletOutput.model_validate(
            await self._client.request("GET", f"/agents/{agent_id}/wallet")
        )

    async def update(
        self,
        agent_id: str,
        *,
        metadata: dict[str, Any] | None = None,
        spend_limit_daily: float | None = None,
        spend_limit_monthly: float | None = None,
    ) -> WalletOutput:
        body: dict[str, Any] = {}
        if metadata is not None:
            body["metadata"] = metadata
        if spend_limit_daily is not None:
            body["spendLimitDaily"] = spend_limit_daily
        if spend_limit_monthly is not None:
            body["spendLimitMonthly"] = spend_limit_monthly
        return WalletOutput.model_validate(
            await self._client.request("PUT", f"/agents/{agent_id}/wallet", body)
        )

    async def pay(
        self,
        agent_id: str,
        *,
        to: str,
        amount: float,
        currency: str | None = None,
        memo: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletPayOutput:
        body = _build_pay_body(
            to=to, amount=amount, currency=currency, memo=memo, metadata=metadata
        )
        return WalletPayOutput.model_validate(
            await self._client.request("POST", f"/agents/{agent_id}/wallet/pay", body)
        )

    async def x402_fetch(
        self,
        agent_id: str,
        *,
        url: str,
        method: str | None = None,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        max_payment_amount: float | None = None,
    ) -> X402FetchOutput:
        req_body = _build_x402_body(
            url=url, method=method, headers=headers, body=body,
            max_payment_amount=max_payment_amount,
        )
        return X402FetchOutput.model_validate(
            await self._client.request("POST", f"/agents/{agent_id}/wallet/x402-fetch", req_body)
        )

    async def transactions(
        self,
        agent_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: str | None = None,
    ) -> list[WalletTransactionOutput]:
        raw = await self._client.request(
            "GET",
            f"/agents/{agent_id}/wallet/transactions",
            query=_to_tx_query(cursor=cursor, limit=limit, status=status),
        )
        return [WalletTransactionOutput.model_validate(item) for item in raw["items"]]

    async def freeze(self, agent_id: str) -> None:
        await self._client.request("POST", f"/agents/{agent_id}/wallet/freeze")

    async def unfreeze(self, agent_id: str) -> None:
        await self._client.request("POST", f"/agents/{agent_id}/wallet/unfreeze")
