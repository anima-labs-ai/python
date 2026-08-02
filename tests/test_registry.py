"""Tests for RegistryResource, centred on DID path encoding.

``lookup``, ``update`` and ``unlist`` all interpolate a DID into the path. DIDs
contain colons, which are legal in a path segment -- so raw interpolation looks
fine and works for the common case. It breaks on the one that matters: a
``did:web`` carrying a port percent-encodes that colon, so the DID string
itself contains ``%3A``. Interpolated raw, the server decodes it back to ``:``
and looks up a DIFFERENT DID.

This SDK was interpolating raw. There was no registry test file in any of the
three SDKs, which is why nobody noticed that node encoded and python and go
did not -- the same DID produced three different URLs.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from urllib.parse import unquote

import pytest

from anima._http import AsyncHTTPClient
from anima.resources.registry import AsyncRegistryResource, RegistryResource

#: A did:web with a port -- the spec percent-encodes the colon before it.
DID_WITH_PORT = "did:web:localhost%3A3000:agents:a1"
PLAIN_DID = "did:web:agents.useanima.sh:org1:agent123"
PLAIN_ENCODED = "did%3Aweb%3Aagents.useanima.sh%3Aorg1%3Aagent123"

AGENT_RAW = {
    "did": PLAIN_DID,
    "agentId": "agent_001",
    "name": "Test",
    "description": None,
    "category": None,
    "capabilities": [],
    "endpoints": {},
    "metadata": {},
    "verified": False,
    "createdAt": "2026-08-01T00:00:00Z",
    "updatedAt": "2026-08-01T00:00:00Z",
}


def _sent_path(mock_http: MagicMock) -> str:
    """The path the SDK actually sent, as the server's router would see it."""
    return str(mock_http.request.call_args[0][1])


class TestDidPathEncoding:
    def test_lookup_encodes_the_did(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        RegistryResource(mock_http).lookup(PLAIN_DID)

        assert _sent_path(mock_http) == f"/registry/agents/{PLAIN_ENCODED}"

    def test_update_encodes_the_did(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        RegistryResource(mock_http).update(PLAIN_DID, name="x")

        assert _sent_path(mock_http) == f"/registry/agents/{PLAIN_ENCODED}"

    def test_unlist_encodes_the_did(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = None
        RegistryResource(mock_http).unlist(PLAIN_DID)

        assert _sent_path(mock_http) == f"/registry/agents/{PLAIN_ENCODED}"

    def test_percent_encoded_port_survives_the_round_trip(self, mock_http: MagicMock) -> None:
        """``%3A`` must reach the server as ``%253A``.

        Otherwise it decodes to ``:`` and resolves
        ``did:web:localhost:3000:agents:a1`` -- a DID nobody registered.
        """
        mock_http.request.return_value = AGENT_RAW
        RegistryResource(mock_http).lookup(DID_WITH_PORT)

        path = _sent_path(mock_http)
        assert "%253A3000" in path
        assert unquote(path.removeprefix("/registry/agents/")) == DID_WITH_PORT

    def test_a_slash_cannot_split_the_path(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = AGENT_RAW
        RegistryResource(mock_http).lookup("did:web:a/b")

        path = _sent_path(mock_http)
        assert path == "/registry/agents/did%3Aweb%3Aa%2Fb"
        assert len(path.split("/")) == 4

    @pytest.mark.asyncio()
    async def test_async_mirror_encodes_too(self) -> None:
        client = AsyncMock(spec=AsyncHTTPClient)
        client.request.return_value = AGENT_RAW
        await AsyncRegistryResource(client).lookup(DID_WITH_PORT)

        assert "%253A3000" in str(client.request.call_args[0][1])
