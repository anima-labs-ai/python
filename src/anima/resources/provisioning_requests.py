"""Ask the organization owner to provision something an agent cannot.

``vault.provision`` and ``phones.provision`` are both master-gated, and an
agent key is never given master authority -- so for an agent, these are the
only routes to a vault (after sign-up) or a phone number at all.

The authority split is enforced server-side, not here: ``create``, ``list``,
``get`` and ``cancel`` work with an agent key; ``approve`` and ``decline``
answer 403 without a master credential. An agent can open the conversation and
withdraw from it, never conclude it.
"""

from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._pagination import AsyncPageIterator, SyncPageIterator
from .._types import (
    CreateProvisioningRequestResult,
    PaginatedResponse,
    PermissionGrantKind,
    ProvisionableResource,
    ProvisioningRequest,
    ProvisioningRequestStatus,
)

_BASE = "/provisioning-requests"


def _list_query(
    cursor: str | None,
    limit: int | None,
    agent_id: str | None,
    status: ProvisioningRequestStatus | str | None,
    resource: ProvisionableResource | str | None,
) -> dict[str, Any] | None:
    query: dict[str, Any] = {}
    if cursor is not None:
        query["cursor"] = cursor
    if limit is not None:
        query["limit"] = limit
    if agent_id is not None:
        query["agentId"] = agent_id
    if status is not None:
        # Enum unwrapping happens in _http._encode_query.
        query["status"] = status
    if resource is not None:
        query["resource"] = resource
    return query or None


def _create_body(
    resource: ProvisionableResource | str,
    reason: str,
    agent_id: str | None,
    country_code: str | None,
    area_code: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "resource": resource.value if isinstance(resource, ProvisionableResource) else resource,
        "reason": reason,
    }
    if agent_id is not None:
        body["agentId"] = agent_id
    options: dict[str, Any] = {}
    if country_code is not None:
        options["countryCode"] = country_code
    if area_code is not None:
        options["areaCode"] = area_code
    if options:
        body["options"] = options
    return body


def _decide_body(
    request_id: str,
    note: str | None,
    grant: PermissionGrantKind | str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"requestId": request_id}
    if note is not None:
        body["note"] = note
    if grant is not None:
        body["grant"] = grant.value if isinstance(grant, PermissionGrantKind) else grant
    return body


class ProvisioningRequestsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        resource: ProvisionableResource | str,
        reason: str,
        agent_id: str | None = None,
        country_code: str | None = None,
        area_code: str | None = None,
        options: RequestOptions | None = None,
    ) -> CreateProvisioningRequestResult:
        """File a request and best-effort notify the owner by email.

        ``reason`` is shown verbatim to the owner -- an unexplained ask is not
        a decidable one. Check ``email_sent`` on the result: False does not
        mean the request failed, but no human was told.

        Filing an identical request while one is already pending returns the
        existing one rather than stacking duplicates in the owner's queue, so
        retrying after a timeout is safe.
        """
        return CreateProvisioningRequestResult.model_validate(
            self._client.request(
                "POST",
                _BASE,
                _create_body(resource, reason, agent_id, country_code, area_code),
                options=options,
            )
        )

    def list(
        self,
        *,
        agent_id: str | None = None,
        status: ProvisioningRequestStatus | str | None = None,
        resource: ProvisionableResource | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> SyncPageIterator[ProvisioningRequest]:
        """List requests, newest first.

        Agents see only their own; org credentials see the whole org.
        """

        def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            agent_id: str | None = agent_id,
            status: ProvisioningRequestStatus | str | None = status,
            resource: ProvisionableResource | str | None = resource,
        ) -> PaginatedResponse[ProvisioningRequest]:
            raw = self._client.request(
                "GET",
                _BASE,
                query=_list_query(cursor, limit, agent_id, status, resource),
                options=options,
            )
            return PaginatedResponse[ProvisioningRequest].model_validate(raw)

        return SyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            agent_id=agent_id,
            status=status,
            resource=resource,
        )

    def get(self, request_id: str, *, options: RequestOptions | None = None) -> ProvisioningRequest:
        return ProvisioningRequest.model_validate(
            self._client.request("GET", f"{_BASE}/{request_id}", options=options)
        )

    def approve(
        self,
        request_id: str,
        *,
        note: str | None = None,
        grant: PermissionGrantKind | str | None = None,
        options: RequestOptions | None = None,
    ) -> ProvisioningRequest:
        """Approve and provision. Requires a master credential.

        ``grant`` is REQUIRED for a GENERIC (permission) request and rejected
        on a resource request. Approving a permission request without it fails
        with a 422: there is no default, because "once" and "always" are very
        different commitments and guessing between them is not the SDK's call.

        Provisioning happens before the request is marked APPROVED, so a
        failure (plan too low, no numbers available, provider down) leaves it
        PENDING -- fix the cause and approve again.
        """
        return ProvisioningRequest.model_validate(
            self._client.request(
                "POST",
                f"{_BASE}/{request_id}/approve",
                _decide_body(request_id, note, grant),
                options=options,
            )
        )

    def decline(
        self,
        request_id: str,
        *,
        note: str | None = None,
        options: RequestOptions | None = None,
    ) -> ProvisioningRequest:
        """Decline. Requires a master credential.

        Soft -- the agent may ask again, so pass a ``note`` saying what would
        change your mind.
        """
        return ProvisioningRequest.model_validate(
            self._client.request(
                "POST",
                f"{_BASE}/{request_id}/decline",
                _decide_body(request_id, note),
                options=options,
            )
        )

    def cancel(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> ProvisioningRequest:
        """Withdraw your own pending request. Works with an agent key."""
        return ProvisioningRequest.model_validate(
            self._client.request(
                "POST", f"{_BASE}/{request_id}/cancel", {"requestId": request_id}, options=options
            )
        )


class AsyncProvisioningRequestsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        resource: ProvisionableResource | str,
        reason: str,
        agent_id: str | None = None,
        country_code: str | None = None,
        area_code: str | None = None,
        options: RequestOptions | None = None,
    ) -> CreateProvisioningRequestResult:
        """File a request and best-effort notify the owner by email.

        ``reason`` is shown verbatim to the owner -- an unexplained ask is not
        a decidable one. Check ``email_sent`` on the result: False does not
        mean the request failed, but no human was told.

        Filing an identical request while one is already pending returns the
        existing one rather than stacking duplicates in the owner's queue, so
        retrying after a timeout is safe.
        """
        return CreateProvisioningRequestResult.model_validate(
            await self._client.request(
                "POST",
                _BASE,
                _create_body(resource, reason, agent_id, country_code, area_code),
                options=options,
            )
        )

    def list(
        self,
        *,
        agent_id: str | None = None,
        status: ProvisioningRequestStatus | str | None = None,
        resource: ProvisionableResource | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncPageIterator[ProvisioningRequest]:
        """List requests, newest first.

        Agents see only their own; org credentials see the whole org.
        """

        async def _fetch(
            cursor: str | None = cursor,
            limit: int | None = limit,
            agent_id: str | None = agent_id,
            status: ProvisioningRequestStatus | str | None = status,
            resource: ProvisionableResource | str | None = resource,
        ) -> PaginatedResponse[ProvisioningRequest]:
            raw = await self._client.request(
                "GET",
                _BASE,
                query=_list_query(cursor, limit, agent_id, status, resource),
                options=options,
            )
            return PaginatedResponse[ProvisioningRequest].model_validate(raw)

        return AsyncPageIterator(
            _fetch,
            cursor=cursor,
            limit=limit,
            agent_id=agent_id,
            status=status,
            resource=resource,
        )

    async def get(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> ProvisioningRequest:
        return ProvisioningRequest.model_validate(
            await self._client.request("GET", f"{_BASE}/{request_id}", options=options)
        )

    async def approve(
        self,
        request_id: str,
        *,
        note: str | None = None,
        grant: PermissionGrantKind | str | None = None,
        options: RequestOptions | None = None,
    ) -> ProvisioningRequest:
        """Approve and provision. Requires a master credential.

        ``grant`` is REQUIRED for a GENERIC (permission) request and rejected
        on a resource request. Approving a permission request without it fails
        with a 422: there is no default, because "once" and "always" are very
        different commitments and guessing between them is not the SDK's call.

        Provisioning happens before the request is marked APPROVED, so a
        failure (plan too low, no numbers available, provider down) leaves it
        PENDING -- fix the cause and approve again.
        """
        return ProvisioningRequest.model_validate(
            await self._client.request(
                "POST",
                f"{_BASE}/{request_id}/approve",
                _decide_body(request_id, note, grant),
                options=options,
            )
        )

    async def decline(
        self,
        request_id: str,
        *,
        note: str | None = None,
        options: RequestOptions | None = None,
    ) -> ProvisioningRequest:
        """Decline. Requires a master credential.

        Soft -- the agent may ask again, so pass a ``note`` saying what would
        change your mind.
        """
        return ProvisioningRequest.model_validate(
            await self._client.request(
                "POST",
                f"{_BASE}/{request_id}/decline",
                _decide_body(request_id, note),
                options=options,
            )
        )

    async def cancel(
        self, request_id: str, *, options: RequestOptions | None = None
    ) -> ProvisioningRequest:
        """Withdraw your own pending request. Works with an agent key."""
        return ProvisioningRequest.model_validate(
            await self._client.request(
                "POST", f"{_BASE}/{request_id}/cancel", {"requestId": request_id}, options=options
            )
        )
