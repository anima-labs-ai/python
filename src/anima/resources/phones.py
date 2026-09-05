from __future__ import annotations

from typing import Any, cast

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import (
    PaginatedResponse,
    PhoneIdentityListItem,
    PhoneIdentityOutput,
    PhoneProvisionOutput,
    SmsSuppression,
    SmsThreadDetail,
    SmsThreadList,
    SmsThreadStatList,
    SmsUnsuppressOutput,
)


def _to_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    agent_id: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if agent_id is not None:
        params["agentId"] = agent_id
    return params or None


def _to_search_query(
    *,
    country_code: str | None = None,
    area_code: str | None = None,
    capabilities: list[str] | None = None,
    limit: int | None = None,
) -> dict[str, Any] | None:
    params: dict[str, Any] = {}
    if country_code is not None:
        params["countryCode"] = country_code
    if area_code is not None:
        params["areaCode"] = area_code
    if capabilities is not None:
        params["capabilities[]"] = capabilities
    if limit is not None:
        params["limit"] = str(limit)
    return params or None


def _to_identities_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    query: str | None = None,
    agent_id: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if query is not None:
        params["query"] = query
    if agent_id is not None:
        params["agentId"] = agent_id
    return params or None


def _to_threads_query(
    *,
    agent_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    unread: bool | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if agent_id is not None:
        params["agentId"] = agent_id
    if limit is not None:
        params["limit"] = str(limit)
    if offset is not None:
        params["offset"] = str(offset)
    # `is not None`, not truthiness: an explicit ``unread=False`` is the "All"
    # filter and ``offset=0`` is the first page. The API treats absent and
    # false alike today -- the handler gates on ``params.unread ? ...`` -- so
    # this keeps the request faithful to the call rather than fixing a live bug.
    if unread is not None:
        params["unread"] = "true" if unread else "false"
    return params or None


def _to_suppressions_query(
    *,
    cursor: str | None = None,
    limit: int | None = None,
    phone_number: str | None = None,
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if cursor is not None:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = str(limit)
    if phone_number is not None:
        params["phoneNumber"] = phone_number
    return params or None


class PhonesResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def search(
        self,
        *,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self._client.request(
                "GET",
                "/phone/search",
                query=_to_search_query(
                    country_code=country_code,
                    area_code=area_code,
                    capabilities=capabilities,
                    limit=limit,
                ),
                options=options,
            ),
        )

    def provision(
        self,
        *,
        agent_id: str,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> PhoneProvisionOutput:
        body: dict[str, Any] = {"agentId": agent_id}
        if country_code is not None:
            body["countryCode"] = country_code
        if area_code is not None:
            body["areaCode"] = area_code
        if capabilities is not None:
            body["capabilities"] = capabilities
        return PhoneProvisionOutput.model_validate(
            self._client.request("POST", "/phone/provision", body, options=options)
        )

    def list(
        self,
        *,
        agent_id: str,
        options: RequestOptions | None = None,
    ) -> list[PhoneIdentityOutput]:
        raw = self._client.request(
            "GET", "/phone/numbers", query={"agentId": agent_id}, options=options
        )
        return [PhoneIdentityOutput.model_validate(item) for item in raw["items"]]

    def release(
        self,
        *,
        agent_id: str,
        phone_number: str,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self._client.request(
                "POST",
                "/phone/release",
                {"agentId": agent_id, "phoneNumber": phone_number},
                options=options,
            ),
        )

    def list_identities(
        self,
        *,
        query: str | None = None,
        agent_id: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[PhoneIdentityListItem]:
        """Every number in the organization, with the agent that owns each.

        The org-wide sibling of :meth:`list`, which answers "what does this
        agent own" and is naturally small. This one answers "what does the org
        own" and is not, so it pages.
        """

        def _fetch(**kw: Any) -> PaginatedResponse[PhoneIdentityListItem]:
            raw = self._client.request(
                "GET",
                "/phone/identities",
                query=_to_identities_query(**kw),
                options=options,
            )
            return PaginatedResponse[PhoneIdentityListItem].model_validate(raw)

        return SyncPageIterator(_fetch, cursor=cursor, limit=limit, query=query, agent_id=agent_id)

    def list_sms_threads(
        self,
        *,
        agent_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        unread: bool | None = None,
        options: RequestOptions | None = None,
    ) -> SmsThreadList:
        """SMS conversations, newest activity first.

        Offset-paged, so this returns a page rather than an iterator: advance
        with ``offset`` and stop when ``has_more`` is false.
        """
        return SmsThreadList.model_validate(
            self._client.request(
                "GET",
                "/phone/sms/threads",
                query=_to_threads_query(
                    agent_id=agent_id, limit=limit, offset=offset, unread=unread
                ),
                options=options,
            )
        )

    def get_sms_thread(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SmsThreadDetail:
        """One conversation with its message history.

        ``thread_id`` comes from :meth:`list_sms_threads` or
        ``MessageOutput.thread_id``.
        """
        query = {"limit": str(limit)} if limit is not None else None
        return SmsThreadDetail.model_validate(
            self._client.request(
                "GET", f"/phone/sms/threads/{thread_id}", query=query, options=options
            )
        )

    def sms_thread_stats(
        self,
        *,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> SmsThreadStatList:
        """Per-agent conversation totals for an SMS overview.

        An aggregate, so it is both correct and cheaper than counting a page of
        :meth:`list_sms_threads` client-side -- that approach makes every number
        a lower bound once the org exceeds one page, with nothing saying so.
        """
        query = {"agentId": agent_id} if agent_id is not None else None
        return SmsThreadStatList.model_validate(
            self._client.request("GET", "/phone/sms/stats", query=query, options=options)
        )

    def list_sms_suppressions(
        self,
        *,
        phone_number: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[SmsSuppression]:
        """Recipients that SMS sends are refused for. Master-key only."""

        def _fetch(**kw: Any) -> PaginatedResponse[SmsSuppression]:
            raw = self._client.request(
                "GET",
                "/phone/sms-suppressions",
                query=_to_suppressions_query(**kw),
                options=options,
            )
            return PaginatedResponse[SmsSuppression].model_validate(raw)

        return SyncPageIterator(_fetch, cursor=cursor, limit=limit, phone_number=phone_number)

    def unsuppress_sms(
        self,
        *,
        phone_number: str,
        options: RequestOptions | None = None,
    ) -> SmsUnsuppressOutput:
        """Remove every SMS suppression for a number in this org. Master-key only.

        Use sparingly: a suppression records the recipient's own STOP, so
        reversing one is an org-owner decision, never an agent's. The
        recipient-driven lift is texting START, which needs no call here.
        """
        return SmsUnsuppressOutput.model_validate(
            self._client.request(
                "POST", "/phone/sms-unsuppress", {"phoneNumber": phone_number}, options=options
            )
        )


class AsyncPhonesResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def search(
        self,
        *,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client.request(
                "GET",
                "/phone/search",
                query=_to_search_query(
                    country_code=country_code,
                    area_code=area_code,
                    capabilities=capabilities,
                    limit=limit,
                ),
                options=options,
            ),
        )

    async def provision(
        self,
        *,
        agent_id: str,
        country_code: str | None = None,
        area_code: str | None = None,
        capabilities: list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> PhoneProvisionOutput:
        body: dict[str, Any] = {"agentId": agent_id}
        if country_code is not None:
            body["countryCode"] = country_code
        if area_code is not None:
            body["areaCode"] = area_code
        if capabilities is not None:
            body["capabilities"] = capabilities
        return PhoneProvisionOutput.model_validate(
            await self._client.request("POST", "/phone/provision", body, options=options)
        )

    async def list(
        self,
        *,
        agent_id: str,
        options: RequestOptions | None = None,
    ) -> list[PhoneIdentityOutput]:
        raw = await self._client.request(
            "GET", "/phone/numbers", query={"agentId": agent_id}, options=options
        )
        return [PhoneIdentityOutput.model_validate(item) for item in raw["items"]]

    async def release(
        self,
        *,
        agent_id: str,
        phone_number: str,
        options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            await self._client.request(
                "POST",
                "/phone/release",
                {"agentId": agent_id, "phoneNumber": phone_number},
                options=options,
            ),
        )

    def list_identities(
        self,
        *,
        query: str | None = None,
        agent_id: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[PhoneIdentityListItem]:
        """Every number in the organization, with the agent that owns each.

        The org-wide sibling of :meth:`list`, which answers "what does this
        agent own" and is naturally small. This one answers "what does the org
        own" and is not, so it pages.
        """

        async def _fetch(**kw: Any) -> PaginatedResponse[PhoneIdentityListItem]:
            raw = await self._client.request(
                "GET",
                "/phone/identities",
                query=_to_identities_query(**kw),
                options=options,
            )
            return PaginatedResponse[PhoneIdentityListItem].model_validate(raw)

        return AsyncPageIterator(_fetch, cursor=cursor, limit=limit, query=query, agent_id=agent_id)

    async def list_sms_threads(
        self,
        *,
        agent_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        unread: bool | None = None,
        options: RequestOptions | None = None,
    ) -> SmsThreadList:
        """SMS conversations, newest activity first.

        Offset-paged, so this returns a page rather than an iterator: advance
        with ``offset`` and stop when ``has_more`` is false.
        """
        return SmsThreadList.model_validate(
            await self._client.request(
                "GET",
                "/phone/sms/threads",
                query=_to_threads_query(
                    agent_id=agent_id, limit=limit, offset=offset, unread=unread
                ),
                options=options,
            )
        )

    async def get_sms_thread(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SmsThreadDetail:
        """One conversation with its message history.

        ``thread_id`` comes from :meth:`list_sms_threads` or
        ``MessageOutput.thread_id``.
        """
        query = {"limit": str(limit)} if limit is not None else None
        return SmsThreadDetail.model_validate(
            await self._client.request(
                "GET", f"/phone/sms/threads/{thread_id}", query=query, options=options
            )
        )

    async def sms_thread_stats(
        self,
        *,
        agent_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> SmsThreadStatList:
        """Per-agent conversation totals for an SMS overview.

        An aggregate, so it is both correct and cheaper than counting a page of
        :meth:`list_sms_threads` client-side -- that approach makes every number
        a lower bound once the org exceeds one page, with nothing saying so.
        """
        query = {"agentId": agent_id} if agent_id is not None else None
        return SmsThreadStatList.model_validate(
            await self._client.request("GET", "/phone/sms/stats", query=query, options=options)
        )

    def list_sms_suppressions(
        self,
        *,
        phone_number: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[SmsSuppression]:
        """Recipients that SMS sends are refused for. Master-key only."""

        async def _fetch(**kw: Any) -> PaginatedResponse[SmsSuppression]:
            raw = await self._client.request(
                "GET",
                "/phone/sms-suppressions",
                query=_to_suppressions_query(**kw),
                options=options,
            )
            return PaginatedResponse[SmsSuppression].model_validate(raw)

        return AsyncPageIterator(_fetch, cursor=cursor, limit=limit, phone_number=phone_number)

    async def unsuppress_sms(
        self,
        *,
        phone_number: str,
        options: RequestOptions | None = None,
    ) -> SmsUnsuppressOutput:
        """Remove every SMS suppression for a number in this org. Master-key only.

        Use sparingly: a suppression records the recipient's own STOP, so
        reversing one is an org-owner decision, never an agent's. The
        recipient-driven lift is texting START, which needs no call here.
        """
        return SmsUnsuppressOutput.model_validate(
            await self._client.request(
                "POST", "/phone/sms-unsuppress", {"phoneNumber": phone_number}, options=options
            )
        )
