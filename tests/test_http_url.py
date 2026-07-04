"""Regression tests for HTTP URL construction — the /v1 version prefix.

The Anima API serves every route under /v1. Resource modules pass BARE paths
(e.g. "/agents"); the published 0.3.0 SDK omitted the prefix, so every such
call returned 404 "Route not found". The prefix now lives in exactly one
place — ``HTTPClient._build_url`` — mirroring the server. These tests guard it.
"""

from __future__ import annotations

from anima._client import Anima


class TestBuildUrlVersionPrefix:
    def test_prepends_v1_to_bare_path(self) -> None:
        with Anima(api_key="sk-test", base_url="https://api.example.com") as client:
            build = client._http._build_url
            assert build("/agents") == "https://api.example.com/v1/agents"
            # A path missing its leading slash is still normalized under /v1.
            assert (
                build("orgs/o1/security/events")
                == "https://api.example.com/v1/orgs/o1/security/events"
            )

    def test_trailing_slash_base_has_no_double_slash(self) -> None:
        with Anima(api_key="sk-test", base_url="https://api.example.com/") as client:
            assert client._http._build_url("/agents") == "https://api.example.com/v1/agents"
