"""Tests for raw response support."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from anima._http import HTTPClient, RawResponse, RequestOptions


class TestRawResponse:
    """Test raw response mode."""

    def _mock_response(self, status: int = 200, json_data: dict | None = None, headers: dict | None = None) -> httpx.Response:
        response = MagicMock(spec=httpx.Response)
        response.status_code = status
        response.is_success = 200 <= status < 300
        response.json.return_value = json_data
        h = httpx.Headers(headers or {})
        response.headers = h
        return response

    def test_returns_data_directly_by_default(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=0)
        mock_resp = self._mock_response(200, {"id": "agent_1"})

        with patch.object(client._client, "request", return_value=mock_resp):
            result = client.request("GET", "/agents/1")

        assert result == {"id": "agent_1"}
        client.close()

    def test_returns_tuple_when_raw_response(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=0)
        mock_resp = self._mock_response(200, {"id": "agent_1"}, {"x-request-id": "req_abc"})

        with patch.object(client._client, "request", return_value=mock_resp):
            data, raw = client.request("GET", "/agents/1", options=RequestOptions(raw_response=True))

        assert data == {"id": "agent_1"}
        assert isinstance(raw, RawResponse)
        assert raw.status == 200
        assert raw.request_id == "req_abc"
        assert raw.response_time_ms >= 0
        client.close()

    def test_raw_response_with_204(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=0)
        mock_resp = self._mock_response(204, headers={"x-request-id": "req_del"})

        with patch.object(client._client, "request", return_value=mock_resp):
            data, raw = client.request("DELETE", "/agents/1", options=RequestOptions(raw_response=True))

        assert data is None
        assert raw.status == 204
        assert raw.request_id == "req_del"
        client.close()

    def test_raw_response_includes_all_headers(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=0)
        mock_resp = self._mock_response(200, {"ok": True}, {"x-custom": "value", "content-type": "application/json"})

        with patch.object(client._client, "request", return_value=mock_resp):
            _, raw = client.request("GET", "/test", options=RequestOptions(raw_response=True))

        assert "x-custom" in raw.headers
        assert raw.headers["x-custom"] == "value"
        client.close()

    def test_raw_response_false_returns_data_only(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=0)
        mock_resp = self._mock_response(200, {"id": "test"})

        with patch.object(client._client, "request", return_value=mock_resp):
            result = client.request("GET", "/test", options=RequestOptions(raw_response=False))

        assert result == {"id": "test"}
        assert not isinstance(result, tuple)
        client.close()
