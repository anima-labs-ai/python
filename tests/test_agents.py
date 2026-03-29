"""Tests for AgentsResource CRUD operations with mocked HTTP."""

from __future__ import annotations

from unittest.mock import MagicMock

from anima._types import AgentOutput, PaginatedResponse
from anima.resources.agents import AgentsResource

from .conftest import AGENT_RAW, PAGINATED_AGENTS_RAW


class TestAgentsCreate:
    def test_create_minimal(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        result = resource.create(org_id="org_001", name="Test Agent", slug="test-agent")

        mock_http.request.assert_called_once_with(
            "POST",
            "/agents",
            {"orgId": "org_001", "name": "Test Agent", "slug": "test-agent"},
        )
        assert isinstance(result, AgentOutput)
        assert result.id == "agent_001"
        assert result.name == "Test Agent"

    def test_create_with_all_options(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        resource.create(
            org_id="org_001",
            name="Test Agent",
            slug="test-agent",
            email="agent@test.com",
            provision_phone=True,
            metadata={"env": "test"},
        )

        call_body = mock_http.request.call_args[0][2]
        assert call_body["email"] == "agent@test.com"
        assert call_body["provisionPhone"] is True
        assert call_body["metadata"] == {"env": "test"}

    def test_create_omits_none_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        resource.create(org_id="org_001", name="Test Agent", slug="test-agent")

        call_body = mock_http.request.call_args[0][2]
        assert "email" not in call_body
        assert "provisionPhone" not in call_body
        assert "metadata" not in call_body


class TestAgentsGet:
    def test_get(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        result = resource.get("agent_001")

        mock_http.request.assert_called_once_with("GET", "/agents/agent_001")
        assert isinstance(result, AgentOutput)
        assert result.id == "agent_001"
        assert result.org_id == "org_001"

    def test_get_parses_email_identities(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        result = resource.get("agent_001")

        assert len(result.email_identities) == 1
        assert result.email_identities[0].email == "agent@test.com"
        assert result.email_identities[0].is_primary is True


class TestAgentsList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_AGENTS_RAW
        resource = AgentsResource(mock_http)
        result = resource.list()

        mock_http.request.assert_called_once_with("GET", "/agents", query=None)
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.pagination.has_more is True
        assert result.pagination.next_cursor == "cur_abc"

    def test_list_with_cursor_and_limit(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_AGENTS_RAW
        resource = AgentsResource(mock_http)
        resource.list(cursor="cur_xyz", limit=10)

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["cursor"] == "cur_xyz"
        assert query["limit"] == "10"

    def test_list_with_filters(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = PAGINATED_AGENTS_RAW
        resource = AgentsResource(mock_http)
        resource.list(org_id="org_001", status="ACTIVE", query="test")

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["orgId"] == "org_001"
        assert query["status"] == "ACTIVE"
        assert query["query"] == "test"


class TestAgentsUpdate:
    def test_update_name(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        result = resource.update("agent_001", name="Updated")

        mock_http.request.assert_called_once_with(
            "PATCH",
            "/agents/agent_001",
            {"id": "agent_001", "name": "Updated"},
        )
        assert isinstance(result, AgentOutput)

    def test_update_multiple_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        resource.update("agent_001", name="New", slug="new-slug", status="SUSPENDED")

        call_body = mock_http.request.call_args[0][2]
        assert call_body["name"] == "New"
        assert call_body["slug"] == "new-slug"
        assert call_body["status"] == "SUSPENDED"

    def test_update_omits_none_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        resource = AgentsResource(mock_http)
        resource.update("agent_001", name="Updated")

        call_body = mock_http.request.call_args[0][2]
        assert "slug" not in call_body
        assert "status" not in call_body
        assert "metadata" not in call_body


class TestAgentsDelete:
    def test_delete(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = None
        resource = AgentsResource(mock_http)
        resource.delete("agent_001")

        mock_http.request.assert_called_once_with("DELETE", "/agents/agent_001")


class TestAgentsRotateKey:
    def test_rotate_key(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "apiKey": "sk-new-key-123",
            "apiKeyPrefix": "sk-new",
        }
        resource = AgentsResource(mock_http)
        result = resource.rotate_key("agent_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/agents/agent_001/rotate-key",
            {"id": "agent_001"},
        )
        assert result == {
            "api_key": "sk-new-key-123",
            "api_key_prefix": "sk-new",
        }
