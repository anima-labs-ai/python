"""Tests for request/response hooks and webhook middleware."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx

from anima._client import Anima
from anima._http import HTTPClient, RequestEvent, ResponseEvent


class TestRequestResponseHooks:
    """Test request/response event hooks."""

    def _mock_response(self, status: int = 200, json_data: dict | None = None) -> httpx.Response:
        response = MagicMock(spec=httpx.Response)
        response.status_code = status
        response.is_success = 200 <= status < 300
        response.json.return_value = json_data
        response.headers = httpx.Headers({})
        return response

    def test_request_hook_called(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=0)
        events: list[RequestEvent] = []
        client.on_request(lambda e: events.append(e))

        mock_resp = self._mock_response(200, {"ok": True})
        with patch.object(client._client, "request", return_value=mock_resp):
            client.request("GET", "/agents")

        assert len(events) == 1
        assert events[0].method == "GET"
        assert events[0].path == "/agents"
        assert events[0].headers["Authorization"] == "Bearer [REDACTED]"
        client.close()

    def test_response_hook_called(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=0)
        events: list[ResponseEvent] = []
        client.on_response(lambda e: events.append(e))

        mock_resp = self._mock_response(200, {"ok": True})
        with patch.object(client._client, "request", return_value=mock_resp):
            client.request("GET", "/agents")

        assert len(events) == 1
        assert events[0].method == "GET"
        assert events[0].path == "/agents"
        assert events[0].status == 200
        assert events[0].duration_ms >= 0
        client.close()

    def test_request_hook_only_called_once_with_retries(self) -> None:
        client = HTTPClient(api_key="sk_test", max_retries=1)
        events: list[RequestEvent] = []
        client.on_request(lambda e: events.append(e))

        mock_500 = self._mock_response(500)
        mock_500.is_success = False
        mock_200 = self._mock_response(200, {"ok": True})
        with patch.object(client._client, "request", side_effect=[mock_500, mock_200]):
            with patch("anima._http._jittered_delay", return_value=0):
                client.request("GET", "/agents")

        assert len(events) == 1
        client.close()

    def test_anima_client_exposes_hooks(self) -> None:
        client = Anima(api_key="sk_test")
        events: list[RequestEvent] = []
        client.on_request(lambda e: events.append(e))

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.is_success = True
        mock_resp.json.return_value = {"ok": True}
        mock_resp.headers = httpx.Headers({})

        with patch.object(client._http._client, "request", return_value=mock_resp):
            client._http.request("GET", "/test")

        assert len(events) == 1
        client.close()


class TestFastapiWebhookDependency:
    """Test FastAPI webhook dependency (without requiring FastAPI)."""

    def test_import_succeeds(self) -> None:
        from anima._middleware import fastapi_webhook_dependency
        dep = fastapi_webhook_dependency("whsec_test")
        assert callable(dep)
