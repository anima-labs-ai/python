from __future__ import annotations

from typing import Any

from .._http import AsyncHTTPClient, HTTPClient
from .._types import PodOutput, PodUsageOutput


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


def _build_create_body(
    *,
    agent_id: str,
    name: str,
    image: str,
    resources: dict[str, str] | None = None,
    env: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "agentId": agent_id,
        "name": name,
        "image": image,
    }
    if resources is not None:
        body["resources"] = resources
    if env is not None:
        body["env"] = env
    if metadata is not None:
        body["metadata"] = metadata
    return body


def _build_update_body(
    *,
    name: str | None = None,
    resources: dict[str, str] | None = None,
    env: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if name is not None:
        body["name"] = name
    if resources is not None:
        body["resources"] = resources
    if env is not None:
        body["env"] = env
    if metadata is not None:
        body["metadata"] = metadata
    return body


class PodsResource:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        agent_id: str,
        name: str,
        image: str,
        resources: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PodOutput:
        body = _build_create_body(
            agent_id=agent_id,
            name=name,
            image=image,
            resources=resources,
            env=env,
            metadata=metadata,
        )
        return PodOutput.model_validate(
            self._client.request("POST", "/pods", body)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> list[PodOutput]:
        raw = self._client.request(
            "GET", "/pods", query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id)
        )
        return [PodOutput.model_validate(item) for item in raw["items"]]

    def get(self, pod_id: str) -> PodOutput:
        return PodOutput.model_validate(
            self._client.request("GET", f"/pods/{pod_id}")
        )

    def update(
        self,
        pod_id: str,
        *,
        name: str | None = None,
        resources: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PodOutput:
        body = _build_update_body(
            name=name, resources=resources, env=env, metadata=metadata
        )
        return PodOutput.model_validate(
            self._client.request("PUT", f"/pods/{pod_id}", body)
        )

    def delete(self, pod_id: str) -> None:
        self._client.request("DELETE", f"/pods/{pod_id}")

    def usage(self, pod_id: str) -> PodUsageOutput:
        return PodUsageOutput.model_validate(
            self._client.request("GET", f"/pods/{pod_id}/usage")
        )


class AsyncPodsResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        agent_id: str,
        name: str,
        image: str,
        resources: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PodOutput:
        body = _build_create_body(
            agent_id=agent_id,
            name=name,
            image=image,
            resources=resources,
            env=env,
            metadata=metadata,
        )
        return PodOutput.model_validate(
            await self._client.request("POST", "/pods", body)
        )

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        agent_id: str | None = None,
    ) -> list[PodOutput]:
        raw = await self._client.request(
            "GET", "/pods", query=_to_query(cursor=cursor, limit=limit, agent_id=agent_id)
        )
        return [PodOutput.model_validate(item) for item in raw["items"]]

    async def get(self, pod_id: str) -> PodOutput:
        return PodOutput.model_validate(
            await self._client.request("GET", f"/pods/{pod_id}")
        )

    async def update(
        self,
        pod_id: str,
        *,
        name: str | None = None,
        resources: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PodOutput:
        body = _build_update_body(
            name=name, resources=resources, env=env, metadata=metadata
        )
        return PodOutput.model_validate(
            await self._client.request("PUT", f"/pods/{pod_id}", body)
        )

    async def delete(self, pod_id: str) -> None:
        await self._client.request("DELETE", f"/pods/{pod_id}")

    async def usage(self, pod_id: str) -> PodUsageOutput:
        return PodUsageOutput.model_validate(
            await self._client.request("GET", f"/pods/{pod_id}/usage")
        )
