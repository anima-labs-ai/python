from __future__ import annotations

from .._http import AsyncHTTPClient, HTTPClient
from .._types import (
    DeliverabilityStatsOutput,
    DomainDnsRecordsOutput,
    DomainOutput,
    DomainZoneFileOutput,
)


class DomainsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def add(self, *, domain: str) -> DomainOutput:
        return DomainOutput.model_validate(
            self._client.request("POST", "/domains", {"domain": domain})
        )

    def get(self, domain_id: str) -> DomainOutput:
        return DomainOutput.model_validate(self._client.request("GET", f"/domains/{domain_id}"))

    def list(self) -> list[DomainOutput]:
        raw = self._client.request("GET", "/domains")
        return [DomainOutput.model_validate(item) for item in raw["items"]]

    def delete(self, domain_id: str) -> None:
        self._client.request("DELETE", f"/domains/{domain_id}")

    def update(self, domain_id: str, *, feedback_enabled: bool | None = None) -> DomainOutput:
        body: dict[str, object] = {}
        if feedback_enabled is not None:
            body["feedbackEnabled"] = feedback_enabled
        return DomainOutput.model_validate(
            self._client.request("PATCH", f"/domains/{domain_id}", body)
        )

    def verify(self, domain_id: str) -> DomainOutput:
        return DomainOutput.model_validate(
            self._client.request(
                "POST",
                f"/domains/{domain_id}/verify",
                {"id": domain_id, "domainId": domain_id},
            )
        )

    def dns_records(self, domain_id: str) -> DomainDnsRecordsOutput:
        return DomainDnsRecordsOutput.model_validate(
            self._client.request("GET", f"/domains/{domain_id}/dns-records")
        )

    def deliverability(self, domain_id: str) -> DeliverabilityStatsOutput:
        return DeliverabilityStatsOutput.model_validate(
            self._client.request("GET", f"/domains/{domain_id}/deliverability")
        )

    def zone_file(self, domain_id: str) -> DomainZoneFileOutput:
        return DomainZoneFileOutput.model_validate(
            self._client.request("GET", f"/domains/{domain_id}/zone-file")
        )


class AsyncDomainsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def add(self, *, domain: str) -> DomainOutput:
        return DomainOutput.model_validate(
            await self._client.request("POST", "/domains", {"domain": domain})
        )

    async def get(self, domain_id: str) -> DomainOutput:
        return DomainOutput.model_validate(
            await self._client.request("GET", f"/domains/{domain_id}")
        )

    async def list(self) -> list[DomainOutput]:
        raw = await self._client.request("GET", "/domains")
        return [DomainOutput.model_validate(item) for item in raw["items"]]

    async def delete(self, domain_id: str) -> None:
        await self._client.request("DELETE", f"/domains/{domain_id}")

    async def update(self, domain_id: str, *, feedback_enabled: bool | None = None) -> DomainOutput:
        body: dict[str, object] = {}
        if feedback_enabled is not None:
            body["feedbackEnabled"] = feedback_enabled
        return DomainOutput.model_validate(
            await self._client.request("PATCH", f"/domains/{domain_id}", body)
        )

    async def verify(self, domain_id: str) -> DomainOutput:
        return DomainOutput.model_validate(
            await self._client.request(
                "POST",
                f"/domains/{domain_id}/verify",
                {"id": domain_id, "domainId": domain_id},
            )
        )

    async def dns_records(self, domain_id: str) -> DomainDnsRecordsOutput:
        return DomainDnsRecordsOutput.model_validate(
            await self._client.request("GET", f"/domains/{domain_id}/dns-records")
        )

    async def deliverability(self, domain_id: str) -> DeliverabilityStatsOutput:
        return DeliverabilityStatsOutput.model_validate(
            await self._client.request("GET", f"/domains/{domain_id}/deliverability")
        )

    async def zone_file(self, domain_id: str) -> DomainZoneFileOutput:
        return DomainZoneFileOutput.model_validate(
            await self._client.request("GET", f"/domains/{domain_id}/zone-file")
        )
