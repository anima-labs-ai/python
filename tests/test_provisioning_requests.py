

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
