"""Shared fixtures for Anima SDK tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from anima._http import HTTPClient

TEST_API_KEY = "sk-test-key-12345"
TEST_BASE_URL = "https://api.useanima.sh"


@pytest.fixture()
def mock_http() -> MagicMock:
    """Return a MagicMock that mimics HTTPClient.request."""
    client = MagicMock(spec=HTTPClient)
    client._api_key = TEST_API_KEY
    client._base_url = TEST_BASE_URL
    return client


# ---------------------------------------------------------------------------
# Reusable raw API response data
# ---------------------------------------------------------------------------

AGENT_RAW: dict[str, Any] = {
    "id": "agent_001",
    "orgId": "org_001",
    "name": "Test Agent",
    "slug": "test-agent",
    "status": "ACTIVE",
    "apiKeyPrefix": "sk-test",
    "metadata": {"env": "test"},
    "emailIdentities": [
        {
            "id": "ei_001",
            "email": "agent@test.com",
            "domain": "test.com",
            "localPart": "agent",
            "isPrimary": True,
            "verified": True,
            "createdAt": "2025-01-01T00:00:00Z",
        }
    ],
    "phoneIdentities": [],
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

PAGINATED_AGENTS_RAW: dict[str, Any] = {
    "items": [AGENT_RAW],
    "pagination": {"nextCursor": "cur_abc", "hasMore": True},
}

MESSAGE_RAW: dict[str, Any] = {
    "id": "msg_001",
    "agentId": "agent_001",
    "channel": "EMAIL",
    "direction": "OUTBOUND",
    "status": "SENT",
    "fromAddress": "agent@test.com",
    "toAddress": "user@example.com",
    "subject": "Hello",
    "body": "Hi there",
    "bodyHtml": "<p>Hi there</p>",
    "headers": {},
    "metadata": {},
    "threadId": None,
    "inReplyTo": None,
    "externalId": None,
    "sentAt": "2025-01-01T00:00:00Z",
    "receivedAt": None,
    "attachments": [],
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

PAGINATED_MESSAGES_RAW: dict[str, Any] = {
    "items": [MESSAGE_RAW],
    "pagination": {"nextCursor": None, "hasMore": False},
}

ATTACHMENT_RAW: dict[str, Any] = {
    "id": "att_001",
    "filename": "report.pdf",
    "mimeType": "application/pdf",
    "sizeBytes": 1024,
    "storageKey": "s3://bucket/report.pdf",
    "url": "https://cdn.example.com/report.pdf",
    "createdAt": "2025-01-01T00:00:00Z",
}

ATTACHMENT_DOWNLOAD_RAW: dict[str, Any] = {
    "url": "https://cdn.example.com/report.pdf?signed=1",
    "expiresAt": "2025-01-01T01:00:00Z",
}

CARD_RAW: dict[str, Any] = {
    "id": "card_001",
    "agentId": "agent_001",
    "orgId": "org_001",
    "stripeCardId": "ic_test",
    "cardType": "VIRTUAL",
    "status": "ACTIVE",
    "last4": "4242",
    "brand": "Visa",
    "expMonth": 12,
    "expYear": 2027,
    "currency": "usd",
    "label": "Test Card",
    "spendLimitDaily": 10000,
    "spendLimitMonthly": 50000,
    "spendLimitPerAuth": 5000,
    "spentToday": 0,
    "spentThisMonth": 0,
    "killSwitchActive": False,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

CARD_LIST_RAW: dict[str, Any] = {
    "items": [CARD_RAW],
    "cursor": None,
}

TRANSACTION_RAW: dict[str, Any] = {
    "id": "txn_001",
    "cardId": "card_001",
    "status": "APPROVED",
    "decision": "APPROVED",
    "amountCents": 1500,
    "currency": "usd",
    "merchantName": "Amazon",
    "merchantCategory": "retail",
    "merchantCategoryCode": "5411",
    "createdAt": "2025-01-01T00:00:00Z",
}

TRANSACTION_LIST_RAW: dict[str, Any] = {
    "items": [TRANSACTION_RAW],
    "cursor": None,
}

SPENDING_POLICY_RAW: dict[str, Any] = {
    "id": "pol_001",
    "cardId": "card_001",
    "orgId": "org_001",
    "name": "Default Policy",
    "priority": 1,
    "action": "AUTO_APPROVE",
    "maxAmountCents": 10000,
    "minAmountCents": None,
    "allowedCategories": [],
    "blockedCategories": [],
    "allowedMerchants": [],
    "blockedMerchants": [],
    "allowedCountries": ["US"],
    "blockedCountries": [],
    "createdAt": "2025-01-01T00:00:00Z",
}

KILL_SWITCH_RAW: dict[str, Any] = {
    "affected": 3,
    "active": True,
}

APPROVAL_RAW: dict[str, Any] = {
    "id": "apr_001",
    "orgId": "org_001",
    "cardId": "card_001",
    "amountCents": 2500,
    "currency": "usd",
    "merchantName": "Test Merchant",
    "status": "PENDING",
    "decidedBy": None,
    "expiresAt": "2025-01-01T01:00:00Z",
    "createdAt": "2025-01-01T00:00:00Z",
}

APPROVAL_LIST_RAW: dict[str, Any] = {
    "items": [APPROVAL_RAW],
    "cursor": None,
}
