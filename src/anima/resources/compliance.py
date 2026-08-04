from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient, RequestOptions, unwrap_enum
from .._types import (
    ComplianceControlCategory,
    ComplianceControlOutput,
    ComplianceControlStatus,
    ComplianceDashboardOutput,
    ComplianceFramework,
    ComplianceReportFormat,
    ComplianceReportOutput,
    ComplianceReportStatus,
    ComplianceReportType,
    CursorPage,
    DsarOutput,
    DsarStatus,
    DsarType,
    ExportReportOutput,
    ListTemplatesOutput,
    SeedFrameworkOutput,
)

# Query params are unwrapped centrally by _http._encode_query (httpx
# stringifies an Enum as "DsarType.ACCESS" where json.dumps gets it right).
# This alias is for JSON bodies, which do not pass through that path.
_value = unwrap_enum


class ComplianceResource:
    """Compliance controls, reports, and data-subject requests.

    Every route here is org-scoped and requires a master key (``mk_*``).
    """

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list_controls(
        self,
        *,
        org_id: str,
        framework: ComplianceFramework | str | None = None,
        category: ComplianceControlCategory | str | None = None,
        status: ComplianceControlStatus | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[ComplianceControlOutput]:
        query: dict[str, str] = {}
        if framework is not None:
            query["framework"] = _value(framework)
        if category is not None:
            query["category"] = _value(category)
        if status is not None:
            query["status"] = _value(status)
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/orgs/{org_id}/compliance/controls", query=query, options=options
        )
        return CursorPage[ComplianceControlOutput].model_validate(raw)

    def get_control(
        self, *, org_id: str, control_id: str, options: RequestOptions | None = None
    ) -> ComplianceControlOutput:
        return ComplianceControlOutput.model_validate(
            self._client.request(
                "GET", f"/orgs/{org_id}/compliance/controls/{control_id}", options=options
            )
        )

    def update_control_status(
        self,
        *,
        org_id: str,
        control_id: str,
        status: ComplianceControlStatus | str,
        owner: str | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceControlOutput:
        payload: dict[str, Any] = {"status": _value(status)}
        if owner is not None:
            payload["owner"] = owner
        return ComplianceControlOutput.model_validate(
            self._client.request(
                "PATCH",
                f"/orgs/{org_id}/compliance/controls/{control_id}",
                payload,
                options=options,
            )
        )

    def seed_framework(
        self,
        *,
        org_id: str,
        framework: ComplianceFramework | str,
        options: RequestOptions | None = None,
    ) -> SeedFrameworkOutput:
        return SeedFrameworkOutput.model_validate(
            self._client.request(
                "POST",
                f"/orgs/{org_id}/compliance/seed",
                {"framework": _value(framework)},
                options=options,
            )
        )

    def list_templates(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ListTemplatesOutput:
        return ListTemplatesOutput.model_validate(
            self._client.request("GET", f"/orgs/{org_id}/compliance/templates", options=options)
        )

    def generate_report(
        self,
        *,
        org_id: str,
        type: ComplianceReportType | str,
        title: str | None = None,
        description: str | None = None,
        format: ComplianceReportFormat | str | None = None,
        generated_by: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
        parameters: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceReportOutput:
        payload: dict[str, Any] = {"type": _value(type)}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if format is not None:
            payload["format"] = _value(format)
        if generated_by is not None:
            payload["generatedBy"] = generated_by
        if period_start is not None:
            payload["periodStart"] = period_start
        if period_end is not None:
            payload["periodEnd"] = period_end
        if parameters is not None:
            payload["parameters"] = parameters
        return ComplianceReportOutput.model_validate(
            self._client.request(
                "POST", f"/orgs/{org_id}/compliance/reports", payload, options=options
            )
        )

    def list_reports(
        self,
        *,
        org_id: str,
        type: ComplianceReportType | str | None = None,
        status: ComplianceReportStatus | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[ComplianceReportOutput]:
        query: dict[str, str] = {}
        if type is not None:
            query["type"] = _value(type)
        if status is not None:
            query["status"] = _value(status)
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/orgs/{org_id}/compliance/reports", query=query, options=options
        )
        return CursorPage[ComplianceReportOutput].model_validate(raw)

    def get_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> ComplianceReportOutput:
        return ComplianceReportOutput.model_validate(
            self._client.request(
                "GET", f"/orgs/{org_id}/compliance/reports/{report_id}", options=options
            )
        )

    def export_report(
        self,
        *,
        org_id: str,
        report_id: str,
        format: ComplianceReportFormat | str | None = None,
        options: RequestOptions | None = None,
    ) -> ExportReportOutput:
        """Export a generated report; the bytes come back inline.

        Replaces ``download_report``, which issued a GET to a ``/download``
        sub-path the API does not serve.
        """
        payload: dict[str, Any] = {}
        if format is not None:
            payload["format"] = _value(format)
        return ExportReportOutput.model_validate(
            self._client.request(
                "POST",
                f"/orgs/{org_id}/compliance/reports/{report_id}/export",
                payload,
                options=options,
            )
        )

    def delete_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> None:
        self._client.request(
            "DELETE", f"/orgs/{org_id}/compliance/reports/{report_id}", options=options
        )

    def get_dashboard(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ComplianceDashboardOutput:
        return ComplianceDashboardOutput.model_validate(
            self._client.request("GET", f"/orgs/{org_id}/compliance/dashboard", options=options)
        )

    def create_dsar(
        self,
        *,
        org_id: str,
        type: DsarType | str,
        subject_email: str,
        subject_name: str | None = None,
        subject_id: str | None = None,
        description: str | None = None,
        due_in_days: int | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        """Open a data-subject request.

        The API field is ``type``. This used to send ``requestType``, which was
        rejected outright.
        """
        payload: dict[str, Any] = {"type": _value(type), "subjectEmail": subject_email}
        if subject_name is not None:
            payload["subjectName"] = subject_name
        if subject_id is not None:
            payload["subjectId"] = subject_id
        if description is not None:
            payload["description"] = description
        if due_in_days is not None:
            payload["dueInDays"] = due_in_days
        if metadata is not None:
            payload["metadata"] = metadata
        return DsarOutput.model_validate(
            self._client.request(
                "POST", f"/orgs/{org_id}/compliance/dsars", payload, options=options
            )
        )

    def list_dsars(
        self,
        *,
        org_id: str,
        status: DsarStatus | str | None = None,
        type: DsarType | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[DsarOutput]:
        query: dict[str, str] = {}
        if status is not None:
            query["status"] = _value(status)
        if type is not None:
            query["type"] = _value(type)
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request(
            "GET", f"/orgs/{org_id}/compliance/dsars", query=query, options=options
        )
        return CursorPage[DsarOutput].model_validate(raw)

    def get_dsar(
        self, *, org_id: str, dsar_id: str, options: RequestOptions | None = None
    ) -> DsarOutput:
        return DsarOutput.model_validate(
            self._client.request(
                "GET", f"/orgs/{org_id}/compliance/dsars/{dsar_id}", options=options
            )
        )

    def update_dsar_status(
        self,
        *,
        org_id: str,
        dsar_id: str,
        status: DsarStatus | str,
        processed_by: str | None = None,
        response: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        """Move a DSAR along its lifecycle.

        Replaces ``complete_dsar``, which POSTed to a ``/complete`` sub-path
        that does not exist; the API models this as a PATCH carrying the status.
        """
        payload: dict[str, Any] = {"status": _value(status)}
        if processed_by is not None:
            payload["processedBy"] = processed_by
        if response is not None:
            payload["response"] = response
        return DsarOutput.model_validate(
            self._client.request(
                "PATCH",
                f"/orgs/{org_id}/compliance/dsars/{dsar_id}",
                payload,
                options=options,
            )
        )


class AsyncComplianceResource:
    """Async twin of :class:`ComplianceResource`."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_controls(
        self,
        *,
        org_id: str,
        framework: ComplianceFramework | str | None = None,
        category: ComplianceControlCategory | str | None = None,
        status: ComplianceControlStatus | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[ComplianceControlOutput]:
        query: dict[str, str] = {}
        if framework is not None:
            query["framework"] = _value(framework)
        if category is not None:
            query["category"] = _value(category)
        if status is not None:
            query["status"] = _value(status)
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/orgs/{org_id}/compliance/controls", query=query, options=options
        )
        return CursorPage[ComplianceControlOutput].model_validate(raw)

    async def get_control(
        self, *, org_id: str, control_id: str, options: RequestOptions | None = None
    ) -> ComplianceControlOutput:
        return ComplianceControlOutput.model_validate(
            await self._client.request(
                "GET", f"/orgs/{org_id}/compliance/controls/{control_id}", options=options
            )
        )

    async def update_control_status(
        self,
        *,
        org_id: str,
        control_id: str,
        status: ComplianceControlStatus | str,
        owner: str | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceControlOutput:
        payload: dict[str, Any] = {"status": _value(status)}
        if owner is not None:
            payload["owner"] = owner
        return ComplianceControlOutput.model_validate(
            await self._client.request(
                "PATCH",
                f"/orgs/{org_id}/compliance/controls/{control_id}",
                payload,
                options=options,
            )
        )

    async def seed_framework(
        self,
        *,
        org_id: str,
        framework: ComplianceFramework | str,
        options: RequestOptions | None = None,
    ) -> SeedFrameworkOutput:
        return SeedFrameworkOutput.model_validate(
            await self._client.request(
                "POST",
                f"/orgs/{org_id}/compliance/seed",
                {"framework": _value(framework)},
                options=options,
            )
        )

    async def list_templates(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ListTemplatesOutput:
        return ListTemplatesOutput.model_validate(
            await self._client.request(
                "GET", f"/orgs/{org_id}/compliance/templates", options=options
            )
        )

    async def generate_report(
        self,
        *,
        org_id: str,
        type: ComplianceReportType | str,
        title: str | None = None,
        description: str | None = None,
        format: ComplianceReportFormat | str | None = None,
        generated_by: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
        parameters: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> ComplianceReportOutput:
        payload: dict[str, Any] = {"type": _value(type)}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if format is not None:
            payload["format"] = _value(format)
        if generated_by is not None:
            payload["generatedBy"] = generated_by
        if period_start is not None:
            payload["periodStart"] = period_start
        if period_end is not None:
            payload["periodEnd"] = period_end
        if parameters is not None:
            payload["parameters"] = parameters
        return ComplianceReportOutput.model_validate(
            await self._client.request(
                "POST", f"/orgs/{org_id}/compliance/reports", payload, options=options
            )
        )

    async def list_reports(
        self,
        *,
        org_id: str,
        type: ComplianceReportType | str | None = None,
        status: ComplianceReportStatus | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[ComplianceReportOutput]:
        query: dict[str, str] = {}
        if type is not None:
            query["type"] = _value(type)
        if status is not None:
            query["status"] = _value(status)
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/orgs/{org_id}/compliance/reports", query=query, options=options
        )
        return CursorPage[ComplianceReportOutput].model_validate(raw)

    async def get_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> ComplianceReportOutput:
        return ComplianceReportOutput.model_validate(
            await self._client.request(
                "GET", f"/orgs/{org_id}/compliance/reports/{report_id}", options=options
            )
        )

    async def export_report(
        self,
        *,
        org_id: str,
        report_id: str,
        format: ComplianceReportFormat | str | None = None,
        options: RequestOptions | None = None,
    ) -> ExportReportOutput:
        """Export a generated report; the bytes come back inline."""
        payload: dict[str, Any] = {}
        if format is not None:
            payload["format"] = _value(format)
        return ExportReportOutput.model_validate(
            await self._client.request(
                "POST",
                f"/orgs/{org_id}/compliance/reports/{report_id}/export",
                payload,
                options=options,
            )
        )

    async def delete_report(
        self, *, org_id: str, report_id: str, options: RequestOptions | None = None
    ) -> None:
        await self._client.request(
            "DELETE", f"/orgs/{org_id}/compliance/reports/{report_id}", options=options
        )

    async def get_dashboard(
        self, *, org_id: str, options: RequestOptions | None = None
    ) -> ComplianceDashboardOutput:
        return ComplianceDashboardOutput.model_validate(
            await self._client.request(
                "GET", f"/orgs/{org_id}/compliance/dashboard", options=options
            )
        )

    async def create_dsar(
        self,
        *,
        org_id: str,
        type: DsarType | str,
        subject_email: str,
        subject_name: str | None = None,
        subject_id: str | None = None,
        description: str | None = None,
        due_in_days: int | None = None,
        metadata: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        """Open a data-subject request. The API field is ``type``."""
        payload: dict[str, Any] = {"type": _value(type), "subjectEmail": subject_email}
        if subject_name is not None:
            payload["subjectName"] = subject_name
        if subject_id is not None:
            payload["subjectId"] = subject_id
        if description is not None:
            payload["description"] = description
        if due_in_days is not None:
            payload["dueInDays"] = due_in_days
        if metadata is not None:
            payload["metadata"] = metadata
        return DsarOutput.model_validate(
            await self._client.request(
                "POST", f"/orgs/{org_id}/compliance/dsars", payload, options=options
            )
        )

    async def list_dsars(
        self,
        *,
        org_id: str,
        status: DsarStatus | str | None = None,
        type: DsarType | str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        options: RequestOptions | None = None,
    ) -> CursorPage[DsarOutput]:
        query: dict[str, str] = {}
        if status is not None:
            query["status"] = _value(status)
        if type is not None:
            query["type"] = _value(type)
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request(
            "GET", f"/orgs/{org_id}/compliance/dsars", query=query, options=options
        )
        return CursorPage[DsarOutput].model_validate(raw)

    async def get_dsar(
        self, *, org_id: str, dsar_id: str, options: RequestOptions | None = None
    ) -> DsarOutput:
        return DsarOutput.model_validate(
            await self._client.request(
                "GET", f"/orgs/{org_id}/compliance/dsars/{dsar_id}", options=options
            )
        )

    async def update_dsar_status(
        self,
        *,
        org_id: str,
        dsar_id: str,
        status: DsarStatus | str,
        processed_by: str | None = None,
        response: dict[str, Any] | None = None,
        options: RequestOptions | None = None,
    ) -> DsarOutput:
        """Move a DSAR along its lifecycle. PATCH, not POST to ``/complete``."""
        payload: dict[str, Any] = {"status": _value(status)}
        if processed_by is not None:
            payload["processedBy"] = processed_by
        if response is not None:
            payload["response"] = response
        return DsarOutput.model_validate(
            await self._client.request(
                "PATCH",
                f"/orgs/{org_id}/compliance/dsars/{dsar_id}",
                payload,
                options=options,
            )
        )
