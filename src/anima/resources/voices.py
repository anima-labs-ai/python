from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient


def _to_query(
    *,
    tier: str | None = None,
    gender: str | None = None,
    language: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if tier is not None:
        params["tier"] = tier
    if gender is not None:
        params["gender"] = gender
    if language is not None:
        params["language"] = language
    return params or None


class VoicesResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list(
        self,
        *,
        tier: str | None = None,
        gender: str | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """List available voices, optionally filtered by tier, gender, or language."""
        return self._client.request(
            "GET",
            "/voice/catalog",
            query=_to_query(tier=tier, gender=gender, language=language),
        )


class AsyncVoicesResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        tier: str | None = None,
        gender: str | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """List available voices, optionally filtered by tier, gender, or language."""
        return await self._client.request(
            "GET",
            "/voice/catalog",
            query=_to_query(tier=tier, gender=gender, language=language),
        )
