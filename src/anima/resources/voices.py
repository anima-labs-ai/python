from __future__ import annotations

from typing import Any, cast

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import Voice


def _to_query(
    *,
    gender: str | None = None,
    language: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
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
        gender: str | None = None,
        language: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """List available voices, optionally filtered by gender or language."""
        raw = self._client.request(
            "GET",
            "/voice/catalog",
            query=_to_query(gender=gender, language=language),
            options=options,
        )
        if isinstance(raw, dict) and "voices" in raw:
            raw["voices"] = [Voice.model_validate(v) for v in raw["voices"]]
        return cast(dict[str, Any], raw)


class AsyncVoicesResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        gender: str | None = None,
        language: str | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        """List available voices, optionally filtered by gender or language."""
        raw = await self._client.request(
            "GET",
            "/voice/catalog",
            query=_to_query(gender=gender, language=language),
            options=options,
        )
        if isinstance(raw, dict) and "voices" in raw:
            raw["voices"] = [Voice.model_validate(v) for v in raw["voices"]]
        return cast(dict[str, Any], raw)
