"""Auto-pagination iterators for cursor-based list endpoints.

Sync usage:
    for agent in anima.agents.list():
        print(agent)

Async usage:
    async for agent in async_anima.agents.list():
        print(agent)

Single-page access (backwards compatible):
    page = anima.agents.list()
    print(page.items)           # first page items
    print(page.pagination)      # cursor info
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, Callable, Generic, TypeVar

from ._types import CursorPagination, PaginatedResponse

T = TypeVar("T")


class SyncPageIterator(Generic[T]):
    """Lazy auto-paginating iterator over cursor-based list endpoints (sync)."""

    def __init__(
        self,
        fetch_page: Callable[..., PaginatedResponse[T]],
        **initial_kwargs: Any,
    ) -> None:
        self._fetch_page = fetch_page
        self._initial_kwargs = initial_kwargs
        self._first_page: PaginatedResponse[T] | None = None

    def _ensure_first_page(self) -> PaginatedResponse[T]:
        if self._first_page is None:
            self._first_page = self._fetch_page(**self._initial_kwargs)
        return self._first_page

    @property
    def items(self) -> list[T]:
        """First page items (backwards compatible)."""
        return self._ensure_first_page().items

    @property
    def pagination(self) -> CursorPagination:
        """First page pagination info (backwards compatible)."""
        return self._ensure_first_page().pagination

    def __iter__(self) -> Iterator[T]:
        """Iterate over all items across all pages."""
        page = self._ensure_first_page()
        while True:
            yield from page.items
            if not page.pagination.has_more or not page.pagination.next_cursor:
                break
            page = self._fetch_page(
                **{**self._initial_kwargs, "cursor": page.pagination.next_cursor},
            )


class AsyncPageIterator(Generic[T]):
    """Lazy auto-paginating iterator over cursor-based list endpoints (async)."""

    def __init__(
        self,
        fetch_page: Callable[..., Any],  # returns Awaitable[PaginatedResponse[T]]
        **initial_kwargs: Any,
    ) -> None:
        self._fetch_page = fetch_page
        self._initial_kwargs = initial_kwargs
        self._first_page: PaginatedResponse[T] | None = None

    async def _ensure_first_page(self) -> PaginatedResponse[T]:
        if self._first_page is None:
            self._first_page = await self._fetch_page(**self._initial_kwargs)
        return self._first_page

    @property
    def items(self) -> list[T]:
        """First page items — only available after awaiting."""
        if self._first_page is None:
            raise RuntimeError("Must await the first page before accessing .items")
        return self._first_page.items

    @property
    def pagination(self) -> CursorPagination:
        """First page pagination — only available after awaiting."""
        if self._first_page is None:
            raise RuntimeError("Must await the first page before accessing .pagination")
        return self._first_page.pagination

    def __await__(self):
        """Allow `page = await anima.agents.list()` for single-page access."""
        return self._ensure_first_page().__await__()

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over all items across all pages."""
        page = await self._ensure_first_page()
        while True:
            for item in page.items:
                yield item
            if not page.pagination.has_more or not page.pagination.next_cursor:
                break
            page = await self._fetch_page(
                **{**self._initial_kwargs, "cursor": page.pagination.next_cursor},
            )
