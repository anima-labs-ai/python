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

# The list endpoint returns InboxListItem, which adds two fields Get does not
# send. Kept separate from INBOX_RAW so a fixture cannot quietly hand the list
# a payload the real endpoint never produces.
INBOX_LIST_ITEM_RAW: dict[str, Any] = {
    **INBOX_RAW,
    "agentName": "Support Agent",
    "unreadCount": 3,
}

PAGINATED_INBOXES_RAW: dict[str, Any] = {
    "items": [INBOX_LIST_ITEM_RAW],
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
    # lowercase, as the API actually sends it: the A2ATask.status column
    # defaults to "submitted" and the handler writes "submitted". This fixture
    # said "SUBMITTED" and the SDK enum agreed with it, so the pair validated
    # each other while no real response could ever parse.
    "status": "submitted",
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

EMAIL_DRAFT_RAW: dict[str, Any] = {
    "id": "draft_001",
    "agentId": "agent_001",
    "orgId": "org_001",
    "fromIdentityId": None,
    "to": ["user@example.com"],
    "cc": [],
    "bcc": [],
    "subject": "Quarterly report",
    "body": "Draft body",
    "bodyHtml": None,
    "inReplyTo": None,
    "references": [],
    "metadata": None,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
}

PAGINATED_DRAFTS_RAW: dict[str, Any] = {
    "items": [EMAIL_DRAFT_RAW],
    "pagination": {"nextCursor": None, "hasMore": False},
}

SEMANTIC_SEARCH_RAW: dict[str, Any] = {
    "results": [
        {
            "id": "msg_001",
            "content": "Hi there",
            "similarity": 0.91,
            "channel": "EMAIL",
            "direction": "OUTBOUND",
            "createdAt": "2025-01-01T00:00:00Z",
            "agentId": "agent_001",
        }
    ]
}

DOMAIN_RAW: dict[str, Any] = {
    "id": "dom_001",
    "domain": "mail.example.com",
    "status": "PENDING",
    "verified": False,
    "verificationCooldownUntil": None,
    "verificationToken": "anima-verify-tok123",
    "verificationMethod": "DNS_TXT",
    "dkimSelector": "anima",
    "dkimPublicKey": "MIIBIjANBg...",
    "spfConfigured": False,
    "dmarcConfigured": False,
    "mxConfigured": False,
    "feedbackEnabled": False,
    "records": [
        {
            "type": "TXT",
            "name": "_anima.mail.example.com",
            "value": "anima-verify-tok123",
            "priority": None,
            "status": "MISSING",
        }
    ],
    "createdAt": "2025-01-01T00:00:00Z",
}

DOMAIN_DNS_RECORDS_RAW: dict[str, Any] = {
    "txt": {"name": "_anima.mail.example.com", "value": "anima-verify-tok123"},
    "mailFrom": {
        "name": "bounce.mail.example.com",
        "mx": {
            "name": "bounce.mail.example.com",
            "value": "feedback-smtp.useanima.sh",
            "priority": 10,
        },
        "spf": "v=spf1 include:useanima.sh ~all",
    },
    "dkim": [{"name": "anima._domainkey.mail.example.com", "value": "v=DKIM1; p=MIIBIjANBg..."}],
    "mx": {"name": "mail.example.com", "value": "mx.useanima.sh", "priority": 10},
    "spf": "v=spf1 include:useanima.sh ~all",
    "dmarc": "v=DMARC1; p=none; rua=mailto:dmarc@mail.example.com",
}

DOMAIN_DELIVERABILITY_RAW: dict[str, Any] = {
    "domain": "mail.example.com",
    "sent": 100,
    "delivered": 97,
    "bounced": 2,
    "complained": 1,
    "bounceRate": 0.02,
    "complaintRate": 0.01,
    "isHealthy": True,
}

DOMAIN_ZONE_FILE_RAW: dict[str, Any] = {
    "zoneFile": "; Anima DNS zone for mail.example.com\n_anima.mail.example.com. IN TXT ...",
}
