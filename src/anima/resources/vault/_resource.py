from __future__ import annotations

from .credentials import _AsyncCredentialsMixin, _SyncCredentialsMixin
from .identities import _AsyncIdentitiesMixin, _SyncIdentitiesMixin
from .requests import _AsyncCredentialRequestsMixin, _SyncCredentialRequestsMixin
from .sharing import _AsyncSharingMixin, _SyncSharingMixin
from .tokens import _AsyncTokensMixin, _SyncTokensMixin


class VaultResource(
    _SyncIdentitiesMixin,
    _SyncCredentialsMixin,
    _SyncCredentialRequestsMixin,
    _SyncSharingMixin,
    _SyncTokensMixin,
):
    """Agent credential vault: provision identities, manage credentials, share,
    broker outbound calls (``use_credential``), request secrets from humans, and
    query the audit trail. Each sub-resource surface lives in its own module and
    is composed here so the whole API hangs off ``client.vault``."""


class AsyncVaultResource(
    _AsyncIdentitiesMixin,
    _AsyncCredentialsMixin,
    _AsyncCredentialRequestsMixin,
    _AsyncSharingMixin,
    _AsyncTokensMixin,
):
    """Async mirror of :class:`VaultResource`."""
