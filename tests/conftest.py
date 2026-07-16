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

INBOX_RAW: dict[str, Any] = {
    "id": "inbox_001",
    "email": "support@agents.useanima.sh",
    "domain": "agents.useanima.sh",
    "localPart": "support",
    "displayName": "Support",
    "agentId": "agent_001",
    "createdAt": "2025-01-01T00:00:00Z",
}

PAGINATED_INBOXES_RAW: dict[str, Any] = {
    "items": [INBOX_RAW],
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

VAULT_CREDENTIAL_RAW: dict[str, Any] = {
    "id": "cred_001",
    "type": "login",
    "name": "GitHub",
    "notes": None,
    "login": {
        "username": "octocat",
        "password": "secret123",
        "uris": [{"uri": "https://github.com"}],
    },
    "card": None,
    "identity": None,
    "fields": None,
    "favorite": False,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

VAULT_SHARE_RAW: dict[str, Any] = {
    "id": "share_001",
    "credentialId": "cred_001",
    "sourceAgentId": "agent_001",
    "targetAgentId": "agent_002",
    "permission": "READ",
    "expiresAt": None,
    "createdAt": "2025-01-01T00:00:00Z",
}

VAULT_SHARE_LIST_RAW: dict[str, Any] = {
    "items": [VAULT_SHARE_RAW],
}

VAULT_TOKEN_RAW: dict[str, Any] = {
    "token": "vtk_abc123def456",
    "credentialId": "cred_001",
    "scope": "autofill",
    "expiresAt": "2025-01-01T00:01:00Z",
}

VAULT_REVOKE_TOKENS_RAW: dict[str, Any] = {
    "success": True,
    "revoked": 3,
}

EXTENSION_CONNECT_RAW: dict[str, Any] = {
    "agentId": "agent_001",
    "connectUrl": "https://useanima.sh/extension/connect#exch_abc123",
    "expiresAt": "2025-01-01T01:00:00Z",
    "exchangeExpiresAt": "2025-01-01T00:05:00Z",
    "policy": "pre_approved",
}

A2A_TASK_RAW: dict[str, Any] = {
    "id": "task_001",
    "agentId": "agent_001",
    "type": "ping",
    "status": "SUBMITTED",
    "input": {},
    "output": None,
    "artifacts": [],
    "fromDid": None,
    "error": None,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}
VAULT_API_KEY_CREDENTIAL_RAW: dict[str, Any] = {
    "id": "cred_ak1",
    "type": "api_key",
    "name": "Stripe key",
    "notes": None,
    "login": None,
    "card": None,
    "identity": None,
    "apiKey": {
        "provider": "stripe",
        "key": "sk_****1234",
        "allowedHosts": ["api.stripe.com"],
        "authHeader": "Authorization",
        "authScheme": "Bearer ",
    },
    "fields": None,
    "favorite": False,
    "revealPolicy": "brokered",
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

VAULT_CREDENTIAL_REQUEST_RAW: dict[str, Any] = {
    "requestId": "req_001",
    "fillUrl": "https://console.useanima.sh/vault/fill/tok_abc",
    "status": "PENDING",
    "expiresAt": "2025-01-01T00:15:00Z",
    "emailSent": True,
    "credentialId": None,
}

VAULT_CREDENTIAL_REQUEST_STATUS_RAW: dict[str, Any] = {
    "status": "FULFILLED",
    "credentialId": "cred_001",
    "maskedPreview": "****1234",
}
