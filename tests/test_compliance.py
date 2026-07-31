"""Tests for ComplianceResource, pinning it to the API contract.

Every call this resource could make was rejected by the API. The enums were
declared in lowercase against a contract that validates SCREAMING_SNAKE, the
DSAR body was keyed ``requestType`` where the API reads ``type``, and two
routes did not exist at all: reports were fetched from GET
``/reports/{id}/download`` and DSARs closed with POST
``/dsars/{id}/complete``, where the API serves POST ``/reports/{id}/export``
and PATCH ``/dsars/{id}``. The response models were invented to match, so even
a request that had been accepted would have failed to parse.

There was no test file for this resource, which is why none of it surfaced.

The daily drift canary does not cover this case: it fires when the monorepo's
contracts CHANGE, and these values were wrong from the first commit. This is
the complement — it catches the SDK drifting from a contract that stayed put.

Source of truth, at the commit pinned in .anima-ref:
  packages/contracts/src/schemas/compliance.ts
  packages/contracts/src/schemas/compliance-controls.ts
  packages/contracts/src/contracts/compliance.ts
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from anima._types import (
    ComplianceControlCategory,
    ComplianceControlStatus,
    ComplianceFramework,
    ComplianceReportFormat,
    ComplianceReportStatus,
    ComplianceReportType,
    DsarStatus,
    DsarType,
)
from anima.resources.compliance import ComplianceResource

DSAR_RAW: dict[str, Any] = {
    "id": "dsar_001",
    "orgId": "org_1",
    "type": "ACCESS",
    "status": "RECEIVED",
    "subjectEmail": "subject@example.com",
    "subjectName": None,
    "subjectId": None,
    "description": None,
    "requestedAt": "2026-07-31T00:00:00Z",
    "verifiedAt": None,
    "dueAt": "2026-08-30T00:00:00Z",
    "completedAt": None,
    "processedBy": None,
    "response": None,
    "metadata": {},
    "createdAt": "2026-07-31T00:00:00Z",
    "updatedAt": "2026-07-31T00:00:00Z",
}

REPORT_RAW: dict[str, Any] = {
    "id": "rep_001",
    "orgId": "org_1",
    "type": "SOC2_SUMMARY",
    "title": "Q3 SOC 2 summary",
    "description": None,
    "status": "COMPLETED",
    "format": "JSON",
    "parameters": {},
    "content": None,
    "errorMessage": None,
    "generatedBy": None,
    "periodStart": "2026-07-01",
    "periodEnd": "2026-09-30",
    "completedAt": "2026-07-31T00:00:00Z",
    "createdAt": "2026-07-31T00:00:00Z",
    "updatedAt": "2026-07-31T00:00:00Z",
}


class TestComplianceEnums:
    """The API validates these values; a lowercase member is a 400 at runtime."""

    def test_every_enum_member_is_screaming_snake(self) -> None:
        enums = [
            ComplianceFramework,
            ComplianceControlStatus,
            ComplianceControlCategory,
            ComplianceReportType,
            ComplianceReportStatus,
            ComplianceReportFormat,
            DsarType,
            DsarStatus,
        ]
        for enum in enums:
            for member in enum:
                assert member.value == member.value.upper(), (
                    f"{enum.__name__}.{member.name} is {member.value!r}; "
                    "the API only accepts uppercase"
                )

    def test_dsar_types_are_the_five_the_api_accepts(self) -> None:
        assert [m.value for m in DsarType] == [
            "ACCESS",
            "DELETE",
            "RECTIFY",
            "PORTABILITY",
            "RESTRICT",
        ]

    def test_dsar_statuses_match_the_contract(self) -> None:
        assert [m.value for m in DsarStatus] == [
            "RECEIVED",
            "VERIFIED",
            "IN_PROGRESS",
            "COMPLETED",
            "DENIED",
            "OVERDUE",
        ]

    def test_report_types_match_the_contract(self) -> None:
        assert [m.value for m in ComplianceReportType] == [
            "SOC2_SUMMARY",
            "ACTIVITY_REPORT",
            "ACCESS_REVIEW",
            "AUDIT_EXPORT",
            "GDPR_DSAR",
        ]

    def test_control_statuses_match_the_contract(self) -> None:
        assert [m.value for m in ComplianceControlStatus] == [
            "NOT_STARTED",
            "IN_PROGRESS",
            "IMPLEMENTED",
            "VERIFIED",
            "FAILED",
        ]


class TestDsarRoutes:
    def test_create_dsar_sends_type_not_request_type(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DSAR_RAW
        ComplianceResource(mock_http).create_dsar(
            org_id="org_1", type=DsarType.ACCESS, subject_email="subject@example.com"
        )
        method, path = mock_http.request.call_args[0][:2]
        payload = mock_http.request.call_args[0][2]
        assert (method, path) == ("POST", "/orgs/org_1/compliance/dsars")
        assert payload["type"] == "ACCESS"
        assert "requestType" not in payload

    def test_create_dsar_accepts_a_plain_string(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DSAR_RAW
        ComplianceResource(mock_http).create_dsar(
            org_id="org_1", type="DELETE", subject_email="subject@example.com"
        )
        assert mock_http.request.call_args[0][2]["type"] == "DELETE"

    def test_create_dsar_passes_due_in_days(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DSAR_RAW
        ComplianceResource(mock_http).create_dsar(
            org_id="org_1",
            type=DsarType.PORTABILITY,
            subject_email="subject@example.com",
            due_in_days=14,
        )
        assert mock_http.request.call_args[0][2]["dueInDays"] == 14

    def test_update_dsar_status_patches_the_dsar_itself(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DSAR_RAW
        ComplianceResource(mock_http).update_dsar_status(
            org_id="org_1", dsar_id="dsar_001", status=DsarStatus.COMPLETED
        )
        method, path = mock_http.request.call_args[0][:2]
        assert (method, path) == ("PATCH", "/orgs/org_1/compliance/dsars/dsar_001")
        assert mock_http.request.call_args[0][2]["status"] == "COMPLETED"

    def test_get_dsar(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = DSAR_RAW
        result = ComplianceResource(mock_http).get_dsar(org_id="org_1", dsar_id="dsar_001")
        method, path = mock_http.request.call_args[0][:2]
        assert (method, path) == ("GET", "/orgs/org_1/compliance/dsars/dsar_001")
        assert result.type is DsarType.ACCESS
        assert result.due_at == "2026-08-30T00:00:00Z"


class TestReportRoutes:
    def test_export_report_posts_to_export(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "data": "e30=",
            "contentType": "application/json",
            "filename": "soc2.json",
        }
        result = ComplianceResource(mock_http).export_report(
            org_id="org_1", report_id="rep_001", format=ComplianceReportFormat.PDF
        )
        method, path = mock_http.request.call_args[0][:2]
        assert (method, path) == ("POST", "/orgs/org_1/compliance/reports/rep_001/export")
        assert mock_http.request.call_args[0][2]["format"] == "PDF"
        assert result.filename == "soc2.json"

    def test_generate_report_sends_period_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = REPORT_RAW
        ComplianceResource(mock_http).generate_report(
            org_id="org_1",
            type=ComplianceReportType.SOC2_SUMMARY,
            period_start="2026-07-01",
            period_end="2026-09-30",
        )
        payload = mock_http.request.call_args[0][2]
        assert payload["type"] == "SOC2_SUMMARY"
        assert payload["periodStart"] == "2026-07-01"
        assert payload["periodEnd"] == "2026-09-30"
        # `from`/`to` were the old invented field names.
        assert "from" not in payload
        assert "to" not in payload

    def test_report_output_parses_the_real_shape(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = REPORT_RAW
        result = ComplianceResource(mock_http).get_report(org_id="org_1", report_id="rep_001")
        assert result.status is ComplianceReportStatus.COMPLETED
        assert result.format is ComplianceReportFormat.JSON
        assert result.period_start == "2026-07-01"

    def test_delete_report(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = None
        ComplianceResource(mock_http).delete_report(org_id="org_1", report_id="rep_001")
        method, path = mock_http.request.call_args[0][:2]
        assert (method, path) == ("DELETE", "/orgs/org_1/compliance/reports/rep_001")

    def test_list_templates(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "items": [{"type": "SOC2_SUMMARY", "title": "SOC 2", "description": "Controls"}]
        }
        result = ComplianceResource(mock_http).list_templates(org_id="org_1")
        method, path = mock_http.request.call_args[0][:2]
        assert (method, path) == ("GET", "/orgs/org_1/compliance/templates")
        assert result.items[0].type == "SOC2_SUMMARY"


class TestControlRoutes:
    def test_update_control_status_sends_uppercase(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {
            "id": "ctl_1",
            "orgId": "org_1",
            "framework": "SOC2",
            "controlId": "CC6.1",
            "title": "Logical access",
            "description": "Access is restricted",
            "category": "CC6",
            "status": "IMPLEMENTED",
            "owner": None,
            "lastTestedAt": None,
            "nextReviewAt": None,
            "createdAt": "2026-07-31T00:00:00Z",
            "updatedAt": "2026-07-31T00:00:00Z",
        }
        result = ComplianceResource(mock_http).update_control_status(
            org_id="org_1", control_id="CC6.1", status=ComplianceControlStatus.IMPLEMENTED
        )
        method, path = mock_http.request.call_args[0][:2]
        assert (method, path) == ("PATCH", "/orgs/org_1/compliance/controls/CC6.1")
        assert mock_http.request.call_args[0][2]["status"] == "IMPLEMENTED"
        assert result.category is ComplianceControlCategory.CC6
