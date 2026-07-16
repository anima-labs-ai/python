"""Tests for DomainsResource (add / get / list / update / delete / verify /
dns_records / deliverability / zone_file).

Custom-domain setup is the first thing a paying customer does before their
agents can send from their own domain. These tests pin the wire contract the
live API serves under /v1/domains: exact paths, the verify body quirk
(domainId required in the body, id in the path), and that DNS/deliverability
outputs parse into typed models the customer can act on.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from anima._http import AsyncHTTPClient
from anima._types import (
    DeliverabilityStatsOutput,
    DomainDnsRecordsOutput,
    DomainOutput,
    DomainRecordStatus,
    DomainStatus,
    DomainZoneFileOutput,
    VerificationMethod,
)
from anima.resources.domains import AsyncDomainsResource, DomainsResource

from .conftest import (
    DOMAIN_DELIVERABILITY_RAW,
    DOMAIN_DNS_RECORDS_RAW,
    DOMAIN_RAW,
    DOMAIN_ZONE_FILE_RAW,
)


class TestDomainsAdd:
    def test_add(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DOMAIN_RAW
        result = DomainsResource(mock_http).add(domain="mail.example.com")

        mock_http.request.assert_called_once_with(
            "POST", "/domains", {"domain": "mail.example.com"}, options=None
        )
        assert isinstance(result, DomainOutput)
        assert result.id == "dom_001"
        assert result.domain == "mail.example.com"
        assert result.status is DomainStatus.PENDING
        assert result.verified is False
        assert result.verification_method is VerificationMethod.DNS_TXT

    def test_add_parses_verification_records(self, mock_http: MagicMock) -> None:
        """The records array is what a customer pastes into their DNS panel —
        it must round-trip with per-record status."""
        mock_http.request.return_value = DOMAIN_RAW
        result = DomainsResource(mock_http).add(domain="mail.example.com")

        assert result.records is not None
        record = result.records[0]
        assert record.type == "TXT"
        assert record.value == "anima-verify-tok123"
        assert record.status is DomainRecordStatus.MISSING


class TestDomainsGet:
    def test_get(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DOMAIN_RAW
        result = DomainsResource(mock_http).get("dom_001")

        mock_http.request.assert_called_once_with("GET", "/domains/dom_001", options=None)
        assert isinstance(result, DomainOutput)
        assert result.id == "dom_001"


class TestDomainsList:
    def test_list_unwraps_items(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"items": [DOMAIN_RAW]}
        result = DomainsResource(mock_http).list()

        mock_http.request.assert_called_once_with("GET", "/domains", options=None)
        assert len(result) == 1
        assert isinstance(result[0], DomainOutput)

    def test_list_empty(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"items": []}
        assert DomainsResource(mock_http).list() == []


class TestDomainsUpdate:
    def test_update_feedback_enabled(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {**DOMAIN_RAW, "feedbackEnabled": True}
        result = DomainsResource(mock_http).update("dom_001", feedback_enabled=True)

        mock_http.request.assert_called_once_with(
            "PATCH", "/domains/dom_001", {"feedbackEnabled": True}, options=None
        )
        assert result.feedback_enabled is True

    def test_update_omits_unset_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DOMAIN_RAW
        DomainsResource(mock_http).update("dom_001")

        payload = mock_http.request.call_args[0][2]
        assert payload == {}


class TestDomainsDelete:
    def test_delete(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"success": True}
        result = DomainsResource(mock_http).delete("dom_001")

        mock_http.request.assert_called_once_with("DELETE", "/domains/dom_001", options=None)
        assert result is None


class TestDomainsVerify:
    def test_verify_sends_domain_id_in_body(self, mock_http: MagicMock) -> None:
        """The contract's VerifyDomainInput requires `domainId` in the BODY
        even though the domain id is already in the path — dropping it makes
        the server 400. `id` is also sent for the path-param merge."""
        mock_http.request.return_value = {**DOMAIN_RAW, "status": "VERIFYING"}
        result = DomainsResource(mock_http).verify("dom_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/domains/dom_001/verify",
            {"id": "dom_001", "domainId": "dom_001"},
            options=None,
        )
        assert result.status is DomainStatus.VERIFYING


class TestDomainsDnsRecords:
    def test_dns_records(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DOMAIN_DNS_RECORDS_RAW
        result = DomainsResource(mock_http).dns_records("dom_001")

        mock_http.request.assert_called_once_with(
            "GET", "/domains/dom_001/dns-records", options=None
        )
        assert isinstance(result, DomainDnsRecordsOutput)
        assert result.txt.value == "anima-verify-tok123"
        assert result.mail_from.mx.priority == 10
        assert result.dkim[0].name.startswith("anima._domainkey.")
        assert result.dmarc.startswith("v=DMARC1")


class TestDomainsDeliverability:
    def test_deliverability(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DOMAIN_DELIVERABILITY_RAW
        result = DomainsResource(mock_http).deliverability("dom_001")

        mock_http.request.assert_called_once_with(
            "GET", "/domains/dom_001/deliverability", options=None
        )
        assert isinstance(result, DeliverabilityStatsOutput)
        assert result.sent == 100
        assert result.bounce_rate == pytest.approx(0.02)
        assert result.is_healthy is True


class TestDomainsZoneFile:
    def test_zone_file(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DOMAIN_ZONE_FILE_RAW
        result = DomainsResource(mock_http).zone_file("dom_001")

        mock_http.request.assert_called_once_with("GET", "/domains/dom_001/zone-file", options=None)
        assert isinstance(result, DomainZoneFileOutput)
        assert "mail.example.com" in result.zone_file


class TestAsyncDomains:
    @pytest.mark.asyncio
    async def test_add(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = DOMAIN_RAW
        result = await AsyncDomainsResource(mock_http).add(domain="mail.example.com")

        mock_http.request.assert_called_once_with(
            "POST", "/domains", {"domain": "mail.example.com"}, options=None
        )
        assert isinstance(result, DomainOutput)

    @pytest.mark.asyncio
    async def test_get(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = DOMAIN_RAW
        result = await AsyncDomainsResource(mock_http).get("dom_001")

        mock_http.request.assert_called_once_with("GET", "/domains/dom_001", options=None)
        assert result.id == "dom_001"

    @pytest.mark.asyncio
    async def test_list(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = {"items": [DOMAIN_RAW]}
        result = await AsyncDomainsResource(mock_http).list()

        assert len(result) == 1
        assert isinstance(result[0], DomainOutput)

    @pytest.mark.asyncio
    async def test_update(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = DOMAIN_RAW
        await AsyncDomainsResource(mock_http).update("dom_001", feedback_enabled=False)

        mock_http.request.assert_called_once_with(
            "PATCH", "/domains/dom_001", {"feedbackEnabled": False}, options=None
        )

    @pytest.mark.asyncio
    async def test_delete(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = {"success": True}
        result = await AsyncDomainsResource(mock_http).delete("dom_001")

        mock_http.request.assert_called_once_with("DELETE", "/domains/dom_001", options=None)
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_sends_domain_id_in_body(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = DOMAIN_RAW
        await AsyncDomainsResource(mock_http).verify("dom_001")

        mock_http.request.assert_called_once_with(
            "POST",
            "/domains/dom_001/verify",
            {"id": "dom_001", "domainId": "dom_001"},
            options=None,
        )

    @pytest.mark.asyncio
    async def test_dns_records(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = DOMAIN_DNS_RECORDS_RAW
        result = await AsyncDomainsResource(mock_http).dns_records("dom_001")

        assert isinstance(result, DomainDnsRecordsOutput)

    @pytest.mark.asyncio
    async def test_deliverability(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = DOMAIN_DELIVERABILITY_RAW
        result = await AsyncDomainsResource(mock_http).deliverability("dom_001")

        assert isinstance(result, DeliverabilityStatsOutput)

    @pytest.mark.asyncio
    async def test_zone_file(self) -> None:
        mock_http = AsyncMock(spec=AsyncHTTPClient)
        mock_http.request.return_value = DOMAIN_ZONE_FILE_RAW
        result = await AsyncDomainsResource(mock_http).zone_file("dom_001")

        assert isinstance(result, DomainZoneFileOutput)


class TestClientWiring:
    def test_sync_client_exposes_domains(self) -> None:
        from anima import Anima

        client = Anima(api_key="sk-test")
        try:
            assert isinstance(client.domains, DomainsResource)
        finally:
            client.close()

    @pytest.mark.asyncio
    async def test_async_client_exposes_domains(self) -> None:
        from anima import AsyncAnima

        client = AsyncAnima(api_key="sk-test")
        try:
            assert isinstance(client.domains, AsyncDomainsResource)
        finally:
            await client.close()
