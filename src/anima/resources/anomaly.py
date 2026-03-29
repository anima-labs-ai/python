from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import (
    AgentBaselineOutput,
    AnomalyAlertOutput,
    AnomalyRuleOutput,
    PaginatedResponse,
    QuarantineOutput,
)


class AnomalyResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def list_alerts(
        self,
        *,
        org_id: str,
        agent_id: str | None = None,
        metric: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[AnomalyAlertOutput]:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        if metric is not None:
            query["metric"] = metric
        if severity is not None:
            query["severity"] = severity
        if status is not None:
            query["status"] = status
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request("GET", f"/v1/orgs/{org_id}/anomaly/alerts", query=query)
        return PaginatedResponse[AnomalyAlertOutput].model_validate(raw)

    def acknowledge_alert(self, *, org_id: str, alert_id: str) -> AnomalyAlertOutput:
        return AnomalyAlertOutput.model_validate(
            self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/alerts/{alert_id}/acknowledge",
            )
        )

    def resolve_alert(self, *, org_id: str, alert_id: str) -> AnomalyAlertOutput:
        return AnomalyAlertOutput.model_validate(
            self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/alerts/{alert_id}/resolve",
            )
        )

    def list_rules(
        self,
        *,
        org_id: str,
        metric: str | None = None,
        enabled: bool | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[AnomalyRuleOutput]:
        query: dict[str, str] = {}
        if metric is not None:
            query["metric"] = metric
        if enabled is not None:
            query["enabled"] = str(enabled).lower()
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = self._client.request("GET", f"/v1/orgs/{org_id}/anomaly/rules", query=query)
        return PaginatedResponse[AnomalyRuleOutput].model_validate(raw)

    def create_rule(
        self,
        *,
        org_id: str,
        name: str,
        metric: str,
        condition: str,
        threshold: float,
        severity: str,
        quarantine_action: str | None = None,
        cooldown_minutes: int | None = None,
        enabled: bool | None = None,
    ) -> AnomalyRuleOutput:
        payload: dict[str, Any] = {
            "name": name,
            "metric": metric,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
        }
        if quarantine_action is not None:
            payload["quarantineAction"] = quarantine_action
        if cooldown_minutes is not None:
            payload["cooldownMinutes"] = cooldown_minutes
        if enabled is not None:
            payload["enabled"] = enabled
        return AnomalyRuleOutput.model_validate(
            self._client.request("POST", f"/v1/orgs/{org_id}/anomaly/rules", payload)
        )

    def update_rule(
        self,
        *,
        org_id: str,
        rule_id: str,
        name: str | None = None,
        threshold: float | None = None,
        severity: str | None = None,
        quarantine_action: str | None = None,
        cooldown_minutes: int | None = None,
        enabled: bool | None = None,
    ) -> AnomalyRuleOutput:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if threshold is not None:
            payload["threshold"] = threshold
        if severity is not None:
            payload["severity"] = severity
        if quarantine_action is not None:
            payload["quarantineAction"] = quarantine_action
        if cooldown_minutes is not None:
            payload["cooldownMinutes"] = cooldown_minutes
        if enabled is not None:
            payload["enabled"] = enabled
        return AnomalyRuleOutput.model_validate(
            self._client.request("PATCH", f"/v1/orgs/{org_id}/anomaly/rules/{rule_id}", payload)
        )

    def delete_rule(self, *, org_id: str, rule_id: str) -> None:
        self._client.request("DELETE", f"/v1/orgs/{org_id}/anomaly/rules/{rule_id}")

    def get_baseline(self, *, org_id: str, agent_id: str) -> AgentBaselineOutput:
        return AgentBaselineOutput.model_validate(
            self._client.request("GET", f"/v1/orgs/{org_id}/anomaly/baselines/{agent_id}")
        )

    def quarantine(
        self,
        *,
        org_id: str,
        agent_id: str,
        level: str,
        reason: str | None = None,
    ) -> QuarantineOutput:
        payload: dict[str, Any] = {"level": level}
        if reason is not None:
            payload["reason"] = reason
        return QuarantineOutput.model_validate(
            self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/quarantine/{agent_id}",
                payload,
            )
        )

    def release_quarantine(self, *, org_id: str, agent_id: str) -> QuarantineOutput:
        return QuarantineOutput.model_validate(
            self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/quarantine/{agent_id}/release",
            )
        )


class AsyncAnomalyResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def list_alerts(
        self,
        *,
        org_id: str,
        agent_id: str | None = None,
        metric: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[AnomalyAlertOutput]:
        query: dict[str, str] = {}
        if agent_id is not None:
            query["agentId"] = agent_id
        if metric is not None:
            query["metric"] = metric
        if severity is not None:
            query["severity"] = severity
        if status is not None:
            query["status"] = status
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request("GET", f"/v1/orgs/{org_id}/anomaly/alerts", query=query)
        return PaginatedResponse[AnomalyAlertOutput].model_validate(raw)

    async def acknowledge_alert(self, *, org_id: str, alert_id: str) -> AnomalyAlertOutput:
        return AnomalyAlertOutput.model_validate(
            await self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/alerts/{alert_id}/acknowledge",
            )
        )

    async def resolve_alert(self, *, org_id: str, alert_id: str) -> AnomalyAlertOutput:
        return AnomalyAlertOutput.model_validate(
            await self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/alerts/{alert_id}/resolve",
            )
        )

    async def list_rules(
        self,
        *,
        org_id: str,
        metric: str | None = None,
        enabled: bool | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> PaginatedResponse[AnomalyRuleOutput]:
        query: dict[str, str] = {}
        if metric is not None:
            query["metric"] = metric
        if enabled is not None:
            query["enabled"] = str(enabled).lower()
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = str(limit)
        raw = await self._client.request("GET", f"/v1/orgs/{org_id}/anomaly/rules", query=query)
        return PaginatedResponse[AnomalyRuleOutput].model_validate(raw)

    async def create_rule(
        self,
        *,
        org_id: str,
        name: str,
        metric: str,
        condition: str,
        threshold: float,
        severity: str,
        quarantine_action: str | None = None,
        cooldown_minutes: int | None = None,
        enabled: bool | None = None,
    ) -> AnomalyRuleOutput:
        payload: dict[str, Any] = {
            "name": name,
            "metric": metric,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
        }
        if quarantine_action is not None:
            payload["quarantineAction"] = quarantine_action
        if cooldown_minutes is not None:
            payload["cooldownMinutes"] = cooldown_minutes
        if enabled is not None:
            payload["enabled"] = enabled
        return AnomalyRuleOutput.model_validate(
            await self._client.request("POST", f"/v1/orgs/{org_id}/anomaly/rules", payload)
        )

    async def update_rule(
        self,
        *,
        org_id: str,
        rule_id: str,
        name: str | None = None,
        threshold: float | None = None,
        severity: str | None = None,
        quarantine_action: str | None = None,
        cooldown_minutes: int | None = None,
        enabled: bool | None = None,
    ) -> AnomalyRuleOutput:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if threshold is not None:
            payload["threshold"] = threshold
        if severity is not None:
            payload["severity"] = severity
        if quarantine_action is not None:
            payload["quarantineAction"] = quarantine_action
        if cooldown_minutes is not None:
            payload["cooldownMinutes"] = cooldown_minutes
        if enabled is not None:
            payload["enabled"] = enabled
        return AnomalyRuleOutput.model_validate(
            await self._client.request(
                "PATCH", f"/v1/orgs/{org_id}/anomaly/rules/{rule_id}", payload
            )
        )

    async def delete_rule(self, *, org_id: str, rule_id: str) -> None:
        await self._client.request("DELETE", f"/v1/orgs/{org_id}/anomaly/rules/{rule_id}")

    async def get_baseline(self, *, org_id: str, agent_id: str) -> AgentBaselineOutput:
        return AgentBaselineOutput.model_validate(
            await self._client.request("GET", f"/v1/orgs/{org_id}/anomaly/baselines/{agent_id}")
        )

    async def quarantine(
        self,
        *,
        org_id: str,
        agent_id: str,
        level: str,
        reason: str | None = None,
    ) -> QuarantineOutput:
        payload: dict[str, Any] = {"level": level}
        if reason is not None:
            payload["reason"] = reason
        return QuarantineOutput.model_validate(
            await self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/quarantine/{agent_id}",
                payload,
            )
        )

    async def release_quarantine(self, *, org_id: str, agent_id: str) -> QuarantineOutput:
        return QuarantineOutput.model_validate(
            await self._client.request(
                "POST",
                f"/v1/orgs/{org_id}/anomaly/quarantine/{agent_id}/release",
            )
        )
