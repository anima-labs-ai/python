"""Tests for auto-pagination iterators."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from anima._pagination import AsyncPageIterator, SyncPageIterator
from anima._types import CursorPagination, PaginatedResponse


def _page(items: list[int], next_cursor: str | None) -> PaginatedResponse[int]:
    return PaginatedResponse[int](
        items=items,
        pagination=CursorPagination(
            next_cursor=next_cursor,
            has_more=next_cursor is not None,
        ),
    )


class TestSyncPageIterator:
    def test_items_returns_first_page(self) -> None:
        it = SyncPageIterator(lambda **kw: _page([1, 2, 3], None))
        assert it.items == [1, 2, 3]
        assert it.pagination.has_more is False

    def test_iter_single_page(self) -> None:
        it = SyncPageIterator(lambda **kw: _page([10, 20], None))
        assert list(it) == [10, 20]

    def test_iter_multi_page(self) -> None:
        calls: list[dict[str, Any]] = []

        def fetch(**kw: Any) -> PaginatedResponse[int]:
            calls.append(kw)
            cursor = kw.get("cursor")
            if cursor is None:
                return _page([1, 2], "c1")
            if cursor == "c1":
                return _page([3, 4], "c2")
            return _page([5], None)

        it = SyncPageIterator(fetch)
        assert list(it) == [1, 2, 3, 4, 5]
        assert len(calls) == 3

    def test_empty_page(self) -> None:
        it = SyncPageIterator(lambda **kw: _page([], None))
        assert list(it) == []

    def test_single_item(self) -> None:
        it = SyncPageIterator(lambda **kw: _page([42], None))
        assert list(it) == [42]

    def test_many_pages_one_item_each(self) -> None:
        counter = {"n": 0}

        def fetch(**kw: Any) -> PaginatedResponse[int]:
            counter["n"] += 1
            n = counter["n"]
            return _page([n], f"c{n}" if n < 5 else None)

        assert list(SyncPageIterator(fetch)) == [1, 2, 3, 4, 5]

    def test_cursor_passed_correctly(self) -> None:
        cursors: list[str | None] = []

        def fetch(**kw: Any) -> PaginatedResponse[int]:
            cursors.append(kw.get("cursor"))
            if kw.get("cursor") is None:
                return _page([1], "abc")
            return _page([2], None)

        list(SyncPageIterator(fetch))
        assert cursors == [None, "abc"]

    def test_kwargs_preserved(self) -> None:
        captured: list[dict[str, Any]] = []

        def fetch(**kw: Any) -> PaginatedResponse[int]:
            captured.append(kw)
            if kw.get("cursor") is None:
                return _page([1], "next")
            return _page([2], None)

        list(SyncPageIterator(fetch, limit=10, org_id="org_1"))
        assert captured[0]["limit"] == 10
        assert captured[0]["org_id"] == "org_1"
        assert captured[1]["limit"] == 10
        assert captured[1]["cursor"] == "next"


class TestAsyncPageIterator:
    def test_await_first_page(self) -> None:
        async def run() -> None:
            async def fetch(**kw: Any) -> PaginatedResponse[int]:
                return _page([1, 2], None)

            page = await AsyncPageIterator(fetch)
            assert page.items == [1, 2]
            assert page.pagination.has_more is False

        asyncio.run(run())

    def test_aiter_single_page(self) -> None:
        async def run() -> list[int]:
            async def fetch(**kw: Any) -> PaginatedResponse[int]:
                return _page([10, 20], None)

            return [item async for item in AsyncPageIterator(fetch)]

        assert asyncio.run(run()) == [10, 20]

    def test_aiter_multi_page(self) -> None:
        async def run() -> list[int]:
            calls: list[dict[str, Any]] = []

            async def fetch(**kw: Any) -> PaginatedResponse[int]:
                calls.append(kw)
                cursor = kw.get("cursor")
                if cursor is None:
                    return _page([1, 2], "c1")
                if cursor == "c1":
                    return _page([3], None)
                return _page([], None)

            items = [item async for item in AsyncPageIterator(fetch)]
            assert len(calls) == 2
            return items

        assert asyncio.run(run()) == [1, 2, 3]

    def test_aiter_empty(self) -> None:
        async def run() -> list[int]:
            async def fetch(**kw: Any) -> PaginatedResponse[int]:
                return _page([], None)

            return [item async for item in AsyncPageIterator(fetch)]

        assert asyncio.run(run()) == []

    def test_error_propagation(self) -> None:
        async def run() -> None:
            call_count = {"n": 0}

            async def fetch(**kw: Any) -> PaginatedResponse[int]:
                call_count["n"] += 1
                if call_count["n"] == 1:
                    return _page([1], "next")
                raise ValueError("page 2 failed")

            items: list[int] = []
            with pytest.raises(ValueError, match="page 2 failed"):
                async for item in AsyncPageIterator(fetch):
                    items.append(item)
            assert items == [1]

        asyncio.run(run())
