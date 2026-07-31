"""Tests for VaultResource sharing and ephemeral token methods."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import (
    CredentialRequestStatus,
    RevealPolicy,
    UseCredentialOutput,
    VaultAuditLogEntry,
    VaultCredential,
    VaultCredentialRequest,
    VaultCredentialRequestCancelResult,
    VaultCredentialRequestStatusOutput,
    VaultIdentityListItem,
    VaultRevokeTokensResult,
    VaultShare,
    VaultTokenOutput,
)
from anima.resources.vault import AsyncVaultResource, VaultResource

from .conftest import (
    VAULT_API_KEY_CREDENTIAL_RAW,
    VAULT_CREDENTIAL_RAW,
    VAULT_CREDENTIAL_REQUEST_RAW,
    VAULT_CREDENTIAL_REQUEST_STATUS_RAW,
    VAULT_REVOKE_TOKENS_RAW,
    VAULT_SHARE_LIST_RAW,
    VAULT_SHARE_RAW,
    VAULT_TOKEN_RAW,
)

# ---------------------------------------------------------------------------
# Sharing
# ---------------------------------------------------------------------------


class TestShareCredential:
    def test_share_credential(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_SHARE_RAW
        resource = VaultResource(mock_http)
        result = resource.share_credential(
            agent_id="agent_001",
            credential_id="cred_001",
            target_agent_id="agent_002",
            permission="READ",
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/share",
            {
                "agentId": "agent_001",
                "credentialId": "cred_001",
                "targetAgentId": "agent_002",
                "permission": "READ",
            },
            options=None,
        )
        assert isinstance(result, VaultShare)
        assert result.id == "share_001"
        assert result.permission == "READ"
        assert result.source_agent_id == "agent_001"
        assert result.target_agent_id == "agent_002"

    def test_share_credential_with_expiry(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_SHARE_RAW
        resource = VaultResource(mock_http)
        resource.share_credential(
            agent_id="agent_001",
            credential_id="cred_001",
            target_agent_id="agent_002",
            permission="USE",
            expires_in_seconds=3600,
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["expiresInSeconds"] == 3600
        assert call_body["permission"] == "USE"


class TestListShares:
    def test_list_shares_granted(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_SHARE_LIST_RAW
        resource = VaultResource(mock_http)
        result = resource.list_shares(direction="granted", agent_id="agent_001")

        mock_http.request.assert_called_once_with(
            "GET",
            "/vault/shares",
            query={"direction": "granted", "agentId": "agent_001"},
            options=None,
        )
        assert len(result) == 1
        assert isinstance(result[0], VaultShare)
        assert result[0].credential_id == "cred_001"

    def test_list_shares_received(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_SHARE_LIST_RAW
        resource = VaultResource(mock_http)
        resource.list_shares(direction="received")

        mock_http.request.assert_called_once_with(
            "GET",
            "/vault/shares",
            query={"direction": "received"},
            options=None,
        )


class TestRevokeShare:
    def test_revoke_share(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = None
        resource = VaultResource(mock_http)
        resource.revoke_share(share_id="share_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/share/revoke",
            {"shareId": "share_001"},
            options=None,
        )

    def test_revoke_share_with_agent_id(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = None
        resource = VaultResource(mock_http)
        resource.revoke_share(share_id="share_001", agent_id="agent_001")

        call_body = mock_http.request.call_args[0][2]
        assert call_body["agentId"] == "agent_001"


# ---------------------------------------------------------------------------
# Ephemeral Tokens
# ---------------------------------------------------------------------------


class TestCreateToken:
    def test_create_token(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_TOKEN_RAW
        resource = VaultResource(mock_http)
        result = resource.create_token(credential_id="cred_001", scope="autofill")

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/token",
            {"credentialId": "cred_001", "scope": "autofill"},
            options=None,
        )
        assert isinstance(result, VaultTokenOutput)
        assert result.token == "vtk_abc123def456"
        assert result.scope == "autofill"
        assert result.credential_id == "cred_001"

    def test_create_token_with_ttl(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_TOKEN_RAW
        resource = VaultResource(mock_http)
        resource.create_token(
            credential_id="cred_001",
            scope="proxy",
            ttl_seconds=300,
            agent_id="agent_001",
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["ttlSeconds"] == 300
        assert call_body["agentId"] == "agent_001"
        assert call_body["scope"] == "proxy"


class TestUseCredential:
    def test_use_credential_brokers_via_use_endpoint(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "status": 200,
            "headers": {},
            "body": "{}",
            "truncated": False,
        }
        resource = VaultResource(mock_http)
        result = resource.use_credential(
            "cred_001",
            method="GET",
            url="https://api.example.com/v1/thing",
            headers={"X-Keep": "1"},
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/credentials/cred_001/use",
            {
                "method": "GET",
                "url": "https://api.example.com/v1/thing",
                "headers": {"X-Keep": "1"},
            },
            options=None,
        )
        # Typed since 0.8.0 -- this returned a bare dict, alone among the
        # vault methods and unlike the node and go SDKs.
        assert isinstance(result, UseCredentialOutput)
        assert result.status == 200
        assert result.truncated is False

    def test_agent_use_path_is_broker(self) -> None:
        # The old UNGATED exchange_token is gone; an agent uses secrets via the
        # broker (use_credential), and get_credential sends no reveal flag.
        assert not hasattr(VaultResource, "exchange_token")
        assert hasattr(VaultResource, "use_credential")
        assert hasattr(VaultResource, "get_credential")

    @pytest.mark.asyncio
    async def test_async_use_credential_brokers_via_use_endpoint(self) -> None:
        # Guard the async mirror of the security-critical broker path against
        # sync/async drift: it must POST to /use and return the upstream
        # response, never the secret.
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = {
            "status": 200,
            "headers": {},
            "body": "{}",
            "truncated": False,
        }
        resource = AsyncVaultResource(mock_http)
        result = await resource.use_credential(
            "cred_001",
            method="GET",
            url="https://api.example.com/v1/thing",
            headers={"X-Keep": "1"},
        )

        mock_http.request.assert_awaited_once_with(
            "POST",
            "/vault/credentials/cred_001/use",
            {
                "method": "GET",
                "url": "https://api.example.com/v1/thing",
                "headers": {"X-Keep": "1"},
            },
            options=None,
        )
        assert isinstance(result, UseCredentialOutput)
        assert result.status == 200

    def test_exchange_token_for_injection_posts_to_exchange(self, mock_http: MagicMock) -> None:
        # Returns plaintext; the API gates it to injector credentials (master /
        # vault:inject), so a plain agent key gets 403 server-side.
        mock_http.request.return_value = VAULT_CREDENTIAL_RAW
        resource = VaultResource(mock_http)
        result = resource.exchange_token_for_injection("vtk_abc")
        mock_http.request.assert_called_once_with(
            "POST", "/vault/token/exchange", {"token": "vtk_abc"}, options=None
        )
        assert isinstance(result, VaultCredential)


class TestApiKeyCredentials:
    def test_create_credential_carries_broker_config(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_API_KEY_CREDENTIAL_RAW
        resource = VaultResource(mock_http)
        result = resource.create_credential(
            agent_id="agent_001",
            type="api_key",
            name="Stripe key",
            api_key={
                "provider": "stripe",
                "key": "sk_live_x",
                "allowedHosts": ["api.stripe.com"],
                "authScheme": "Bearer ",
            },
            reveal_policy="brokered",
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/credentials",
            {
                "agentId": "agent_001",
                "type": "api_key",
                "name": "Stripe key",
                "favorite": False,
                "apiKey": {
                    "provider": "stripe",
                    "key": "sk_live_x",
                    "allowedHosts": ["api.stripe.com"],
                    "authScheme": "Bearer ",
                },
                "revealPolicy": "brokered",
            },
            options=None,
        )
        assert isinstance(result, VaultCredential)
        assert result.api_key is not None
        assert result.api_key.allowed_hosts == ["api.stripe.com"]
        assert result.reveal_policy is RevealPolicy.BROKERED

    def test_update_credential_carries_api_key_and_policy(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_API_KEY_CREDENTIAL_RAW
        resource = VaultResource(mock_http)
        resource.update_credential(
            "cred_ak1",
            api_key={"provider": "stripe", "key": "sk_live_y"},
            reveal_policy="brokered",
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["apiKey"] == {"provider": "stripe", "key": "sk_live_y"}
        assert call_body["revealPolicy"] == "brokered"


class TestCredentialRequests:
    def test_credential_request_create(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_CREDENTIAL_REQUEST_RAW
        resource = VaultResource(mock_http)
        result = resource.credential_request_create(
            type="api_key",
            name="Prod Stripe key",
            reason="Deploy needs to verify billing",
            ttl_seconds=600,
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/credential-requests",
            {
                "type": "api_key",
                "name": "Prod Stripe key",
                "reason": "Deploy needs to verify billing",
                "ttlSeconds": 600,
            },
            options=None,
        )
        assert isinstance(result, VaultCredentialRequest)
        assert result.request_id == "req_001"
        assert result.status is CredentialRequestStatus.PENDING
        assert result.fill_url.startswith("https://")

    def test_credential_request_status_returns_masked_preview_only(
        self, mock_http: MagicMock
    ) -> None:
        mock_http.request.return_value = VAULT_CREDENTIAL_REQUEST_STATUS_RAW
        resource = VaultResource(mock_http)
        result = resource.credential_request_status("req_001")

        mock_http.request.assert_called_once_with(
            "GET",
            "/vault/credential-requests/req_001",
            options=None,
        )
        assert isinstance(result, VaultCredentialRequestStatusOutput)
        assert result.status is CredentialRequestStatus.FULFILLED
        assert result.credential_id == "cred_001"
        # Only a masked preview comes back — never the plaintext.
        assert result.masked_preview == "****1234"

    def test_credential_request_cancel(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"status": "CANCELLED"}
        resource = VaultResource(mock_http)
        result = resource.credential_request_cancel("req_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/credential-requests/req_001/cancel",
            None,
            options=None,
        )
        assert isinstance(result, VaultCredentialRequestCancelResult)
        assert result.status is CredentialRequestStatus.CANCELLED


class TestRevokeTokens:
    def test_revoke_tokens(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_REVOKE_TOKENS_RAW
        resource = VaultResource(mock_http)
        result = resource.revoke_tokens(credential_id="cred_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/token/revoke",
            {"credentialId": "cred_001"},
            options=None,
        )
        assert isinstance(result, VaultRevokeTokensResult)
        assert result.success is True
        assert result.revoked == 3

    def test_revoke_tokens_with_agent_id(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_REVOKE_TOKENS_RAW
        resource = VaultResource(mock_http)
        resource.revoke_tokens(credential_id="cred_001", agent_id="agent_001")

        call_body = mock_http.request.call_args[0][2]
        assert call_body["agentId"] == "agent_001"


# ---------------------------------------------------------------------------
# Server-side password generation
# ---------------------------------------------------------------------------


class TestCreateCredentialGeneratePassword:
    def test_generate_password_sends_options_and_no_password(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_CREDENTIAL_RAW
        resource = VaultResource(mock_http)
        result = resource.create_credential(
            agent_id="agent_001",
            type="login",
            name="Acme Portal",
            login={"username": "bot@acme.io"},
            generate_password={"length": 32, "special": False},
        )

        mock_http.request.assert_called_once_with(
            "POST",
            "/vault/credentials",
            {
                "agentId": "agent_001",
                "type": "login",
                "name": "Acme Portal",
                "favorite": False,
                "login": {"username": "bot@acme.io"},
                "generatePassword": {"length": 32, "special": False},
            },
            options=None,
        )
        assert isinstance(result, VaultCredential)

    def test_no_generate_password_omits_field(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = VAULT_CREDENTIAL_RAW
        resource = VaultResource(mock_http)
        resource.create_credential(
            agent_id="agent_001",
            type="login",
            name="Plain",
            login={"username": "u", "password": "p"},
        )
        body = mock_http.request.call_args[0][2]
        assert "generatePassword" not in body


class TestIdentitiesAndAudit:
    def test_list_identities_paginates(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [
                {
                    "id": "vi_1",
                    "agentId": "agent_001",
                    "orgId": "org_001",
                    "status": "ACTIVE",
                    "credentialCount": 3,
                    "lastSyncAt": None,
                    "createdAt": "2025-01-01T00:00:00Z",
                    "agentName": "Billing Agent",
                    "agentSlug": "billing",
                }
            ],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        resource = VaultResource(mock_http)
        page = resource.list_identities(status="ACTIVE", limit=10)
        items = page.items

        mock_http.request.assert_called_once_with(
            "GET",
            "/vault/identities",
            query={"limit": "10", "status": "ACTIVE"},
            options=None,
        )
        assert len(items) == 1
        assert isinstance(items[0], VaultIdentityListItem)
        assert items[0].agent_slug == "billing"

    def test_audit_queries_broker_actions_without_secrets(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [
                {
                    "id": "audit_1",
                    "credentialId": "cred_001",
                    "agentId": "agent_001",
                    "orgId": "org_001",
                    "action": "broker_use",
                    "actor": "org_001",
                    "metadata": {"method": "GET", "host": "api.stripe.com", "status": 200},
                    "createdAt": "2025-01-01T00:00:00Z",
                }
            ],
            "pagination": {"nextCursor": None, "hasMore": False},
        }
        resource = VaultResource(mock_http)
        page = resource.audit(credential_id="cred_001", action="broker_use")
        entries = page.items

        mock_http.request.assert_called_once_with(
            "GET",
            "/vault/audit",
            query={"credentialId": "cred_001", "action": "broker_use"},
            options=None,
        )
        assert len(entries) == 1
        assert isinstance(entries[0], VaultAuditLogEntry)
        assert entries[0].action == "broker_use"
        assert entries[0].metadata is not None
        assert entries[0].metadata["host"] == "api.stripe.com"
