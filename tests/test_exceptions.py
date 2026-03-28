"""Tests for exception hierarchy and error parsing from HTTP responses."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from anima._exceptions import (
    APIError,
    AnimaError,
    AuthenticationError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from anima._http import _parse_error


class TestExceptionHierarchy:
    """Verify exception types and their default values."""

    def test_anima_error_base(self) -> None:
        err = AnimaError("something broke", details={"key": "val"})
        assert str(err) == "something broke"
        assert err.message == "something broke"
        assert err.details == {"key": "val"}

    def test_api_error(self) -> None:
        err = APIError("bad request", 400, "BAD_REQ", {"field": "name"})
        assert err.status_code == 400
        assert err.code == "BAD_REQ"
        assert "[400]" in str(err)
        assert "(BAD_REQ)" in str(err)

    def test_api_error_str_without_code(self) -> None:
        err = APIError("fail", 500)
        assert str(err) == "[500] fail"

    def test_authentication_error_defaults(self) -> None:
        err = AuthenticationError()
        assert err.status_code == 401
        assert err.code == "AUTH_ERROR"
        assert err.message == "Authentication failed"

    def test_not_found_error_defaults(self) -> None:
        err = NotFoundError()
        assert err.status_code == 404
        assert err.code == "NOT_FOUND"

    def test_validation_error_defaults(self) -> None:
        err = ValidationError()
        assert err.status_code == 400
        assert err.code == "VALIDATION_ERROR"

    def test_rate_limit_error(self) -> None:
        err = RateLimitError(retry_after=30.0)
        assert err.status_code == 429
        assert err.retry_after == 30.0

    def test_conflict_error_defaults(self) -> None:
        err = ConflictError()
        assert err.status_code == 409

    def test_internal_server_error_defaults(self) -> None:
        err = InternalServerError()
        assert err.status_code == 500
        assert err.code == "INTERNAL_ERROR"

    def test_internal_server_error_custom_status(self) -> None:
        err = InternalServerError(status_code=503)
        assert err.status_code == 503

    def test_all_inherit_from_anima_error(self) -> None:
        for cls in [
            APIError, AuthenticationError, NotFoundError,
            ValidationError, RateLimitError, ConflictError, InternalServerError,
        ]:
            assert issubclass(cls, AnimaError)

    def test_all_inherit_from_api_error(self) -> None:
        for cls in [
            AuthenticationError, NotFoundError, ValidationError,
            RateLimitError, ConflictError, InternalServerError,
        ]:
            assert issubclass(cls, APIError)


class TestParseError:
    """Test _parse_error correctly maps HTTP status codes."""

    def _make_response(
        self,
        status_code: int,
        json_body: dict | None = None,
        headers: dict | None = None,
    ) -> MagicMock:
        resp = MagicMock()
        resp.status_code = status_code
        resp.headers = headers or {}
        if json_body is not None:
            resp.json.return_value = json_body
        else:
            resp.json.side_effect = ValueError("No JSON")
        return resp

    def test_400_returns_validation_error(self) -> None:
        resp = self._make_response(400, {"error": {"message": "bad field"}})
        err = _parse_error(resp)
        assert isinstance(err, ValidationError)
        assert "bad field" in err.message

    def test_422_returns_validation_error(self) -> None:
        resp = self._make_response(422, {"message": "invalid"})
        err = _parse_error(resp)
        assert isinstance(err, ValidationError)

    def test_401_returns_auth_error(self) -> None:
        resp = self._make_response(401)
        err = _parse_error(resp)
        assert isinstance(err, AuthenticationError)

    def test_403_returns_auth_error(self) -> None:
        resp = self._make_response(403)
        err = _parse_error(resp)
        assert isinstance(err, AuthenticationError)

    def test_404_returns_not_found(self) -> None:
        resp = self._make_response(404, {"error": {"message": "Agent not found", "code": "NOT_FOUND"}})
        err = _parse_error(resp)
        assert isinstance(err, NotFoundError)

    def test_409_returns_conflict(self) -> None:
        resp = self._make_response(409)
        err = _parse_error(resp)
        assert isinstance(err, ConflictError)

    def test_429_returns_rate_limit_with_retry_after(self) -> None:
        resp = self._make_response(429, headers={"retry-after": "60"})
        err = _parse_error(resp)
        assert isinstance(err, RateLimitError)
        assert err.retry_after == 60.0

    def test_429_without_retry_after_header(self) -> None:
        resp = self._make_response(429)
        err = _parse_error(resp)
        assert isinstance(err, RateLimitError)
        assert err.retry_after is None

    def test_500_returns_internal_server_error(self) -> None:
        resp = self._make_response(500)
        err = _parse_error(resp)
        assert isinstance(err, InternalServerError)
        assert err.status_code == 500

    def test_502_returns_internal_server_error(self) -> None:
        resp = self._make_response(502)
        err = _parse_error(resp)
        assert isinstance(err, InternalServerError)
        assert err.status_code == 502

    def test_unknown_status_returns_api_error(self) -> None:
        resp = self._make_response(418)
        err = _parse_error(resp)
        assert type(err) is APIError
        assert err.status_code == 418

    def test_error_object_with_details(self) -> None:
        body = {
            "error": {
                "message": "Validation failed",
                "code": "VALIDATION",
                "details": [{"field": "name", "reason": "required"}],
            }
        }
        resp = self._make_response(400, body)
        err = _parse_error(resp)
        assert err.details == [{"field": "name", "reason": "required"}]

    def test_json_parse_failure_uses_default_message(self) -> None:
        resp = self._make_response(500)
        err = _parse_error(resp)
        assert "500" in err.message
