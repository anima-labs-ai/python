"""Exception hierarchy for the Anima SDK."""

from __future__ import annotations

from typing import Any


class AnimaError(Exception):
    """Base exception for all Anima SDK errors."""

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class APIError(AnimaError):
    """HTTP API error with status code and optional error code."""

    def __init__(
        self,
        message: str,
        status_code: int,
        code: str | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code
        self.code = code

    def __str__(self) -> str:
        parts = [f"[{self.status_code}]"]
        if self.code:
            parts.append(f"({self.code})")
        parts.append(self.message)
        return " ".join(parts)


class AuthenticationError(APIError):
    """Raised on 401 or 403 responses."""

    def __init__(self, message: str = "Authentication failed", details: Any | None = None) -> None:
        super().__init__(message, 401, "AUTH_ERROR", details)


class NotFoundError(APIError):
    """Raised on 404 responses."""

    def __init__(self, message: str = "Resource not found", details: Any | None = None) -> None:
        super().__init__(message, 404, "NOT_FOUND", details)


class ValidationError(APIError):
    """Raised on 400 or 422 responses."""

    def __init__(self, message: str = "Validation failed", details: Any | None = None) -> None:
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class RateLimitError(APIError):
    """Raised on 429 responses."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message, 429, "RATE_LIMIT", details)
        self.retry_after = retry_after


class ConflictError(APIError):
    """Raised on 409 responses."""

    def __init__(self, message: str = "Resource conflict", details: Any | None = None) -> None:
        super().__init__(message, 409, "CONFLICT", details)


class InternalServerError(APIError):
    """Raised on 5xx responses."""

    def __init__(
        self,
        message: str = "Internal server error",
        status_code: int = 500,
        details: Any | None = None,
    ) -> None:
        super().__init__(message, status_code, "INTERNAL_ERROR", details)
