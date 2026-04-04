from __future__ import annotations

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import (
    DeliverabilityStatsOutput,
    DomainDnsRecordsOutput,
    DomainOutput,
    DomainZoneFileOutput,
)


class DomainsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def add(self, *, domain: str, options: RequestOptions | None = None) -> DomainOutput:
        return DomainOutput.model_validate(
            self._client.request("POST", "/domains", {"domain": domain}, options=options)
        )

    def get(self, domain_id: str, *, options: RequestOptions | None = None) -> DomainOutput:
        return DomainOutput.model_validate(
            self._client.request("GET", f"/domains/{domain_id}", options=options)
        )

    def list(self, *, options: RequestOptions | None = None) -> list[DomainOutput]:
        raw = self._client.request("GET", "/domains", options=options)
        return [DomainOutput.model_validate(item) for item in raw["items"]]

    def delete(self, domain_id: str, *, options: RequestOptions | None = None) -> None:
        self._client.request("DELETE", f"/domains/{domain_id}", options=options)

    def update(
        self,
        domain_id: str,
        *,
        feedback_enabled: bool | None = None,
        options: RequestOptions | None = None,
    ) -> DomainOutput:
        body: dict[str, object] = {}
        if feedback_enabled is not None:
            body["feedbackEnabled"] = feedback_enabled
        return DomainOutput.model_validate(
            self._client.request("PATCH", f"/domains/{domain_id}", body, options=options)
        )

    def verify(self, domain_id: str, *, options: RequestOptions | None = None) -> DomainOutput:
        return DomainOutput.model_validate(
            self._client.request(
                "POST",
                f"/domains/{domain_id}/verify",
                {"id": domain_id, "domainId": domain_id},
                options=options,
            )
        )

    def dns_records(
        self, domain_id: str, *, options: RequestOptions | None = None
    ) -> DomainDnsRecordsOutput:
        return DomainDnsRecordsOutput.model_validate(
            self._client.request("GET", f"/domains/{domain_id}/dns-records", options=options)
        )

    def deliverability(
        self, domain_id: str, *, options: RequestOptions | None = None
    ) -> DeliverabilityStatsOutput:
        return DeliverabilityStatsOutput.model_validate(
            self._client.request("GET", f"/domains/{domain_id}/deliverability", options=options)
        )

    def zone_file(
        self, domain_id: str, *, options: RequestOptions | None = None
    ) -> DomainZoneFileOutput:
        return DomainZoneFileOutput.model_validate(
            self._client.request("GET", f"/domains/{domain_id}/zone-file", options=options)
        )


class AsyncDomainsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def add(self, *, domain: str, options: RequestOptions | None = None) -> DomainOutput:
        return DomainOutput.model_validate(
            await self._client.request("POST", "/domains", {"domain": domain}, options=options)
        )

    async def get(self, domain_id: str, *, options: RequestOptions | None = None) -> DomainOutput:
        return DomainOutput.model_validate(
            await self._client.request("GET", f"/domains/{domain_id}", options=options)
        )

    async def list(self, *, options: RequestOptions | None = None) -> list[DomainOutput]:
        raw = await self._client.request("GET", "/domains", options=options)
        return [DomainOutput.model_validate(item) for item in raw["items"]]

    async def delete(self, domain_id: str, *, options: RequestOptions | None = None) -> None:
        await self._client.request("DELETE", f"/domains/{domain_id}", options=options)

    async def update(
        self,
        domain_id: str,
        *,
        feedback_enabled: bool | None = None,
        options: RequestOptions | None = None,
    ) -> DomainOutput:
        body: dict[str, object] = {}
        if feedback_enabled is not None:
            body["feedbackEnabled"] = feedback_enabled
        return DomainOutput.model_validate(
            await self._client.request("PATCH", f"/domains/{domain_id}", body, options=options)
        )

    async def verify(
        self, domain_id: str, *, options: RequestOptions | None = None
    ) -> DomainOutput:
        return DomainOutput.model_validate(
            await self._client.request(
                "POST",
                f"/domains/{domain_id}/verify",
                {"id": domain_id, "domainId": domain_id},
                options=options,
            )
        )

    async def dns_records(
        self, domain_id: str, *, options: RequestOptions | None = None
    ) -> DomainDnsRecordsOutput:
        return DomainDnsRecordsOutput.model_validate(
            await self._client.request("GET", f"/domains/{domain_id}/dns-records", options=options)
        )

    async def deliverability(
        self, domain_id: str, *, options: RequestOptions | None = None
    ) -> DeliverabilityStatsOutput:
        return DeliverabilityStatsOutput.model_validate(
            await self._client.request(
                "GET", f"/domains/{domain_id}/deliverability", options=options
            )
        )

    async def zone_file(
        self, domain_id: str, *, options: RequestOptions | None = None
    ) -> DomainZoneFileOutput:
        return DomainZoneFileOutput.model_validate(
            await self._client.request("GET", f"/domains/{domain_id}/zone-file", options=options)
        )
