from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions
from .._types import (
    ComplianceControlOutput,
    ComplianceDashboardOutput,
    ComplianceReportDownloadOutput,
    ComplianceReportOutput,
    DsarOutput,
    PaginatedResponse,
    SeedFrameworkOutput,
)


class ComplianceResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list_controls(
        self,
        *,
        org_id: str,
        framework: str | None = None,
        category: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[ComplianceControlOutput]:
        query: dict[str, str] = {}
        if framework is not None:
            query["framework"] = framework
        if category is not None:
            query["category"] = category
        if status is not None:
            query["status"] = status
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/v1/orgs/{org_id}/compliance/controls", query=query, options=options
        )
        return PaginatedResponse[ComplianceControlOutput].model_validate(raw)

    def get_control(
        self, *, org_id: str, control_id: str, options: RequestOptions | None = None
    ) -> ComplianceControlOutput:
        return ComplianceControlOutput.model_validate(
            self._client.request(
                "GET", f"/v1/orgs/{org_id}/compliance/controls/{control_id}", options=options
            )
        )

    def update_control_status(
        self,
        *,
        org_id: str,
        control_id: str,
        status: str,
        owner: str | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceControlOutput:
        payload: dict[str, Any] = {"status": status}
        if owner is not None:
            payload["owner"] = owner
        return ComplianceControlOutput.model_validate(
            self._client.request(
                "PATCH",
                f"/v1/orgs/{org_id}/compliance/controls/{control_id}",
                payload,
                options=options,
            )
        )

    def seed_framework(
        self, *, org_id: str, framework: str, options: RequestOptions | None = None
    ) -> SeedFrameworkOutput:
        return SeedFrameworkOutput.model_validate(
            self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/compliance/seed",
                {"framework": framework},
                options=options,
            )
        )

    def generate_report(
        self,
        *,
        org_id: str,
        type: str,
        from_: str | None = None,
        to: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceReportOutput:
        payload: dict[str, Any] = {"type": type}
        if from_ is not None:
            payload["from"] = from_
        if to is not None:
            payload["to"] = to
        if metadata is not None:
            payload["metadata"] = metadata
        return ComplianceReportOutput.model_validate(
            self._client.request(
                "POST", f"/v1/orgs/{org_id}/compliance/reports", payload, options=options
            )
        )

    def list_reports(
        self,
        *,
        org_id: str,
        type: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[ComplianceReportOutput]:
        query: dict[str, str] = {}
        if type is not None:
            query["type"] = type
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/v1/orgs/{org_id}/compliance/reports", query=query, options=options
        )
        return PaginatedResponse[ComplianceReportOutput].model_validate(raw)

    def get_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> ComplianceReportOutput:
        return ComplianceReportOutput.model_validate(
            self._client.request(
                "GET", f"/v1/orgs/{org_id}/compliance/reports/{report_id}", options=options
            )
        )

    def download_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> ComplianceReportDownloadOutput:
        return ComplianceReportDownloadOutput.model_validate(
            self._client.request(
                "GET",
                f"/v1/orgs/{org_id}/compliance/reports/{report_id}/download",
                options=options,
            )
        )

    def get_dashboard(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ComplianceDashboardOutput:
        return ComplianceDashboardOutput.model_validate(
            self._client.request("GET", f"/v1/orgs/{org_id}/compliance/dashboard", options=options)
        )

    def create_dsar(
        self,
        *,
        org_id: str,
        subject_email: str,
        request_type: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        payload: dict[str, Any] = {
            "subjectEmail": subject_email,
            "requestType": request_type,
        }
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return DsarOutput.model_validate(
            self._client.request(
                "POST", f"/v1/orgs/{org_id}/compliance/dsars", payload, options=options
            )
        )

    def list_dsars(
        self,
        *,
        org_id: str,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[DsarOutput]:
        query: dict[str, str] = {}
        if status is not None:
            query["status"] = status
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/v1/orgs/{org_id}/compliance/dsars", query=query, options=options
        )
        return PaginatedResponse[DsarOutput].model_validate(raw)

    def complete_dsar(
        self,
        *,
        org_id: str,
        dsar_id: str,
        notes: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        payload: dict[str, Any] = {}
        if notes is not None:
            payload["notes"] = notes
        if metadata is not None:
            payload["metadata"] = metadata
        return DsarOutput.model_validate(
            self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/compliance/dsars/{dsar_id}/complete",
                payload,
                options=options,
            )
        )


class AsyncComplianceResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_controls(
        self,
        *,
        org_id: str,
        framework: str | None = None,
        category: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[ComplianceControlOutput]:
        query: dict[str, str] = {}
        if framework is not None:
            query["framework"] = framework
        if category is not None:
            query["category"] = category
        if status is not None:
            query["status"] = status
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/v1/orgs/{org_id}/compliance/controls", query=query, options=options
        )
        return PaginatedResponse[ComplianceControlOutput].model_validate(raw)

    async def get_control(
        self, *, org_id: str, control_id: str, options: RequestOptions | None = None
    ) -> ComplianceControlOutput:
        return ComplianceControlOutput.model_validate(
            await self._client.request(
                "GET", f"/v1/orgs/{org_id}/compliance/controls/{control_id}", options=options
            )
        )

    async def update_control_status(
        self,
        *,
        org_id: str,
        control_id: str,
        status: str,
        owner: str | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceControlOutput:
        payload: dict[str, Any] = {"status": status}
        if owner is not None:
            payload["owner"] = owner
        return ComplianceControlOutput.model_validate(
            await self._client.request(
                "PATCH",
                f"/v1/orgs/{org_id}/compliance/controls/{control_id}",
                payload,
                options=options,
            )
        )

    async def seed_framework(
        self, *, org_id: str, framework: str, options: RequestOptions | None = None
    ) -> SeedFrameworkOutput:
        return SeedFrameworkOutput.model_validate(
            await self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/compliance/seed",
                {"framework": framework},
                options=options,
            )
        )

    async def generate_report(
        self,
        *,
        org_id: str,
        type: str,
        from_: str | None = None,
        to: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceReportOutput:
        payload: dict[str, Any] = {"type": type}
        if from_ is not None:
            payload["from"] = from_
        if to is not None:
            payload["to"] = to
        if metadata is not None:
            payload["metadata"] = metadata
        return ComplianceReportOutput.model_validate(
            await self._client.request(
                "POST", f"/v1/orgs/{org_id}/compliance/reports", payload, options=options
            )
        )

    async def list_reports(
        self,
        *,
        org_id: str,
        type: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[ComplianceReportOutput]:
        query: dict[str, str] = {}
        if type is not None:
            query["type"] = type
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/v1/orgs/{org_id}/compliance/reports", query=query, options=options
        )
        return PaginatedResponse[ComplianceReportOutput].model_validate(raw)

    async def get_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> ComplianceReportOutput:
        return ComplianceReportOutput.model_validate(
            await self._client.request(
                "GET", f"/v1/orgs/{org_id}/compliance/reports/{report_id}", options=options
            )
        )

    async def download_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> ComplianceReportDownloadOutput:
        return ComplianceReportDownloadOutput.model_validate(
            await self._client.request(
                "GET",
                f"/v1/orgs/{org_id}/compliance/reports/{report_id}/download",
                options=options,
            )
        )

    async def get_dashboard(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ComplianceDashboardOutput:
        return ComplianceDashboardOutput.model_validate(
            await self._client.request(
                "GET", f"/v1/orgs/{org_id}/compliance/dashboard", options=options
            )
        )

    async def create_dsar(
        self,
        *,
        org_id: str,
        subject_email: str,
        request_type: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        payload: dict[str, Any] = {
            "subjectEmail": subject_email,
            "requestType": request_type,
        }
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return DsarOutput.model_validate(
            await self._client.request(
                "POST", f"/v1/orgs/{org_id}/compliance/dsars", payload, options=options
            )
        )

    async def list_dsars(
        self,
        *,
        org_id: str,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> PaginatedResponse[DsarOutput]:
        query: dict[str, str] = {}
        if status is not None:
            query["status"] = status
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/v1/orgs/{org_id}/compliance/dsars", query=query, options=options
        )
        return PaginatedResponse[DsarOutput].model_validate(raw)

    async def complete_dsar(
        self,
        *,
        org_id: str,
        dsar_id: str,
        notes: str | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        payload: dict[str, Any] = {}
        if notes is not None:
            payload["notes"] = notes
        if metadata is not None:
            payload["metadata"] = metadata
        return DsarOutput.model_validate(
            await self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/compliance/dsars/{dsar_id}/complete",
                payload,
                options=options,
            )
        )
