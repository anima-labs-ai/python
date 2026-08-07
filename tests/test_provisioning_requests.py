def test_generic_rows_parse():
    """A GENERIC row must deserialize.

    This is a regression test for a shipped break, not a feature: the enum had
    only VAULT and PHONE_NUMBER, so once the server began filing GENERIC rows
    for master-gated operations, `provisioning_requests.list()` raised a
    ValidationError for any org whose agent had ever hit a gate. The whole
    listing failed, not just the one row.
    """
    from anima._types import ProvisionableResource, ProvisioningRequest

    row = ProvisioningRequest.model_validate(
        {
            "requestId": "req_1",
            "agentId": "agent_1",
            "agentName": "Agent",
            "resource": "GENERIC",
            "reason": "Agent attempted vault.provision, which requires master authority.",
            "status": "PENDING",
            "options": None,
            "expiresAt": "2026-01-01T00:00:00Z",
            "decidedAt": None,
            "decidedNote": None,
            "provisionedId": None,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    assert row.resource is ProvisionableResource.GENERIC


def test_permission_detail_parses():
    """A GENERIC row carries what the agent was actually refused."""
    from anima._types import ProvisioningRequest

    row = ProvisioningRequest.model_validate(
        {
            "requestId": "req_1",
            "agentId": "agent_1",
            "agentName": "Agent",
            "resource": "GENERIC",
            "reason": "Agent attempted agent.delete, which requires master authority.",
            "status": "PENDING",
            "options": None,
            "permission": {
                "procedurePath": "agent.delete",
                "readOnly": False,
                "argumentPreview": {"agentId": "agent_abc"},
            },
            "expiresAt": "2026-01-01T00:00:00Z",
            "decidedAt": None,
            "decidedNote": None,
            "provisionedId": None,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    assert row.permission is not None
    assert row.permission.procedure_path == "agent.delete"
    assert row.permission.read_only is False
    assert row.permission.argument_preview == {"agentId": "agent_abc"}


def test_resource_request_has_no_permission_detail():
    """Null, not absent-and-broken, on a plain resource request."""
    from anima._types import ProvisioningRequest

    row = ProvisioningRequest.model_validate(
        {
            "requestId": "req_2",
            "agentId": "agent_1",
            "agentName": "Agent",
            "resource": "VAULT",
            "reason": "needs a vault",
            "status": "PENDING",
            "options": None,
            "permission": None,
            "expiresAt": "2026-01-01T00:00:00Z",
            "decidedAt": None,
            "decidedNote": None,
            "provisionedId": None,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    assert row.permission is None


def test_both_clients_forward_the_grant(mock_http):
    """Sync AND async. The async one is the reason this test exists.

    The first pass at this added ``grant`` to the sync ``approve`` only, and
    the unit test covered ``_decide_body`` — which both clients share and which
    was never the broken part. So the suite stayed green while
    ``AsyncProvisioningRequestsResource.approve`` went on dropping the grant
    silently, leaving every async caller unable to approve a permission
    request at all. Testing the resource methods, not the body builder, is
    what closes that.
    """
    import asyncio
    from unittest.mock import AsyncMock

    from anima.resources.provisioning_requests import (
        AsyncProvisioningRequestsResource,
        ProvisioningRequestsResource,
    )

    row = {
        "requestId": "req_1",
        "agentId": "agent_1",
        "agentName": "Agent",
        "resource": "GENERIC",
        "reason": "x",
        "status": "APPROVED",
        "options": None,
        "permission": None,
        "expiresAt": "2026-01-01T00:00:00Z",
        "decidedAt": None,
        "decidedNote": None,
        "provisionedId": "perm_1",
        "createdAt": "2026-01-01T00:00:00Z",
    }

    mock_http.request.return_value = row
    ProvisioningRequestsResource(mock_http).approve("req_1", grant="always")
    assert mock_http.request.call_args[0][2] == {"requestId": "req_1", "grant": "always"}

    async_http = AsyncMock()
    async_http.request.return_value = row
    asyncio.run(AsyncProvisioningRequestsResource(async_http).approve("req_1", grant="always"))
    assert async_http.request.call_args[0][2] == {"requestId": "req_1", "grant": "always"}


def test_approve_sends_the_grant():
    """Approving a permission request without a grant is a 422 server-side.

    Before this, `approve` accepted only a note, so the Python SDK could not
    approve a permission request at all — the one thing an owner most needs to
    do with one.
    """
    from anima._types import PermissionGrantKind
    from anima.resources.provisioning_requests import _decide_body

    assert _decide_body("req_1", None, PermissionGrantKind.ALWAYS) == {
        "requestId": "req_1",
        "grant": "always",
    }
    # A plain string is accepted too, so callers are not forced through the enum.
    assert _decide_body("req_1", "ok", "once") == {
        "requestId": "req_1",
        "note": "ok",
        "grant": "once",
    }
    # Omitted entirely for a resource request, which the API rejects a grant on.
    assert _decide_body("req_1", None) == {"requestId": "req_1"}
