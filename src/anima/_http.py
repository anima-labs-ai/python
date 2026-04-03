"""Sync and async HTTP transport with retry logic and error parsing."""

from __future__ import annotations

import asyncio
import contextlib
import random
import time
import uuid
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx

from ._logger import logger

from ._exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

T = TypeVar("T")

DEFAULT_BASE_URL = "https://api.useanima.sh"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
BASE_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 30.0  # seconds

_MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


@dataclass
class RequestOptions:
    """Per-request overrides for mutating operations."""

    idempotency_key: str | None = None
    timeout: float | None = None
    max_retries: int | None = None


def _should_retry(status_code: int) -> bool:
    return status_code == 429 or status_code >= 500


def _jittered_delay(attempt: int) -> float:
    """Jittered exponential backoff: random(0, BASE * 2^attempt), capped at MAX."""
    exponential = BASE_RETRY_DELAY * (2 ** attempt)
    return min(random.random() * exponential, MAX_RETRY_DELAY)


def _parse_retry_after(response: httpx.Response) -> float | None:
    """Parse Retry-After header (seconds) if present."""
    header = response.headers.get("retry-after")
    if not header:
        return None
    try:
        return float(header)
    except ValueError:
        return None


def _parse_error(response: httpx.Response) -> APIError:
    retry_after_raw = response.headers.get("retry-after")
    retry_after = float(retry_after_raw) if retry_after_raw else None

    message = f"Request failed with status {response.status_code}"
    code: str | None = None
    details: Any = None

    with contextlib.suppress(Exception):
        payload = response.json()
        if isinstance(payload, dict):
            err = payload.get("error")
            if isinstance(err, dict):
                message = err.get("message", message)
                code = err.get("code")
                details = err.get("details")
            elif "message" in payload:
                message = payload["message"]

    status = response.status_code

    if status in (400, 422):
        return ValidationError(message, details)
    if status in (401, 403):
        return AuthenticationError(message, details)
    if status == 404:
        return NotFoundError(message, details)
    if status == 409:
        return ConflictError(message, details)
    if status == 429:
        return RateLimitError(message, retry_after, details)
    if status >= 500:
        return InternalServerError(message, status, details)

    return APIError(message, status, code, details)


def _build_headers(
    api_key: str,
    has_body: bool,
    idempotency_key: str | None = None,
) -> dict[str, str]:
    headers: dict[str, str] = {"Authorization": f"Bearer {api_key}"}
    if has_body:
        headers["Content-Type"] = "application/json"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


class HTTPClient:
    """Synchronous HTTP transport using httpx."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.Client(timeout=timeout)
        logger.debug("Client initialized base_url=%s timeout=%s max_retries=%s", self._base_url, timeout, max_retries)

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        body: Any | None = None,
        query: dict[str, str] | None = None,
        options: RequestOptions | None = None,
    ) -> Any:
        url = self._build_url(path)
        max_retries = (options and options.max_retries) or self._max_retries
        idem_key = (
            (options and options.idempotency_key)
            or (str(uuid.uuid4()) if method in _MUTATING_METHODS else None)
        )
        headers = _build_headers(self._api_key, body is not None, idem_key)
        start = time.monotonic()
        logger.debug("%s %s", method, path)

        for attempt in range(max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    url,
                    json=body if body is not None else None,
                    params=query,
                    headers=headers,
                )

                duration_ms = (time.monotonic() - start) * 1000

                if response.is_success:
                    logger.debug("%s %s -> %d (%.0fms)", method, path, response.status_code, duration_ms)
                    if response.status_code == 204:
                        return None
                    return response.json()

                if _should_retry(response.status_code) and attempt < max_retries:
                    retry_after = _parse_retry_after(response)
                    delay = retry_after if retry_after is not None else _jittered_delay(attempt)
                    logger.debug("%s %s -> %d, retrying in %.0fms (attempt %d)", method, path, response.status_code, delay * 1000, attempt + 1)
                    time.sleep(delay)
                    continue

                logger.debug("%s %s -> %d (failed, %.0fms)", method, path, response.status_code, duration_ms)
                raise _parse_error(response)

            except APIError:
                raise
            except httpx.TimeoutException:
                if attempt < max_retries:
                    delay = _jittered_delay(attempt)
                    logger.debug("%s %s -> timeout, retrying in %.0fms (attempt %d)", method, path, delay * 1000, attempt + 1)
                    time.sleep(delay)
                    continue
                logger.debug("%s %s -> timeout (failed)", method, path)
                raise APIError(
                    f"Request timed out after {self._timeout}s", 408, "TIMEOUT"
                ) from None
            except httpx.HTTPError as exc:
                if attempt < max_retries:
                    delay = _jittered_delay(attempt)
                    logger.debug("%s %s -> network error, retrying in %.0fms (attempt %d)", method, path, delay * 1000, attempt + 1)
                    time.sleep(delay)
                    continue
                logger.debug("%s %s -> network error (failed)", method, path)
                raise APIError(str(exc), 0, "NETWORK_ERROR") from exc

        raise APIError("Request failed after retries", 0, "RETRY_EXHAUSTED")

    def _build_url(self, path: str) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        return f"{self._base_url}/api{normalized}"


class AsyncHTTPClient:
    """Asynchronous HTTP transport using httpx."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)
        logger.debug("AsyncClient initialized base_url=%s timeout=%s max_retries=%s", self._base_url, timeout, max_retries)

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        body: Any | None = None,
        query: dict[str, str] | None = None,
        options: RequestOptions | None = None,
    ) -> Any:
        url = self._build_url(path)
        max_retries = (options and options.max_retries) or self._max_retries
        idem_key = (
            (options and options.idempotency_key)
            or (str(uuid.uuid4()) if method in _MUTATING_METHODS else None)
        )
        headers = _build_headers(self._api_key, body is not None, idem_key)
        start = time.monotonic()
        logger.debug("%s %s", method, path)

        for attempt in range(max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    url,
                    json=body if body is not None else None,
                    params=query,
                    headers=headers,
                )

                duration_ms = (time.monotonic() - start) * 1000

                if response.is_success:
                    logger.debug("%s %s -> %d (%.0fms)", method, path, response.status_code, duration_ms)
                    if response.status_code == 204:
                        return None
                    return response.json()

                if _should_retry(response.status_code) and attempt < max_retries:
                    retry_after = _parse_retry_after(response)
                    delay = retry_after if retry_after is not None else _jittered_delay(attempt)
                    logger.debug("%s %s -> %d, retrying in %.0fms (attempt %d)", method, path, response.status_code, delay * 1000, attempt + 1)
                    await asyncio.sleep(delay)
                    continue

                logger.debug("%s %s -> %d (failed, %.0fms)", method, path, response.status_code, duration_ms)
                raise _parse_error(response)

            except APIError:
                raise
            except httpx.TimeoutException:
                if attempt < max_retries:
                    delay = _jittered_delay(attempt)
                    logger.debug("%s %s -> timeout, retrying in %.0fms (attempt %d)", method, path, delay * 1000, attempt + 1)
                    await asyncio.sleep(delay)
                    continue
                logger.debug("%s %s -> timeout (failed)", method, path)
                raise APIError(
                    f"Request timed out after {self._timeout}s", 408, "TIMEOUT"
                ) from None
            except httpx.HTTPError as exc:
                if attempt < max_retries:
                    delay = _jittered_delay(attempt)
                    logger.debug("%s %s -> network error, retrying in %.0fms (attempt %d)", method, path, delay * 1000, attempt + 1)
                    await asyncio.sleep(delay)
                    continue
                logger.debug("%s %s -> network error (failed)", method, path)
                raise APIError(str(exc), 0, "NETWORK_ERROR") from exc

        raise APIError("Request failed after retries", 0, "RETRY_EXHAUSTED")

    def _build_url(self, path: str) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        return f"{self._base_url}/api{normalized}"
