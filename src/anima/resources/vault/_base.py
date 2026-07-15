from __future__ import annotations

from ..._http import AsyncHTTPClient, HTTPClient


class _SyncVaultBase:
    """Carries the sync HTTP client shared by every sync vault sub-resource mixin."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client


class _AsyncVaultBase:
    """Carries the async HTTP client shared by every async vault sub-resource mixin."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client
