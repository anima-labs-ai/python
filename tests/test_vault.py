"""Tests for VaultResource sharing and ephemeral token methods."""

from __future__ import annotations

from unittest.mock import MagicMock

from anima._types import VaultRevokeTokensResult, VaultShare, VaultTokenOutput
from anima.resources.vault import VaultResource

from .conftest import (
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
        assert result["status"] == 200

    def test_no_plaintext_reveal_method(self) -> None:
        # exchange_token returned plaintext and is deliberately removed; the SDK
        # exposes no plaintext-reveal path (use, never see).
        assert not hasattr(VaultResource, "exchange_token")
        assert hasattr(VaultResource, "use_credential")
        assert hasattr(VaultResource, "get_credential")


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
