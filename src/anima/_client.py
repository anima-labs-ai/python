"""Sync and async Anima API client classes."""

from __future__ import annotations

from types import TracebackType

from ._http import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncHTTPClient,
    HTTPClient,
)
from ._webhooks import construct_webhook_event, verify_webhook_signature
from .resources.addresses import AddressesResource, AsyncAddressesResource
from .resources.agents import AgentsResource, AsyncAgentsResource
from .resources.cards import AsyncCardsResource, CardsResource
from .resources.domains import AsyncDomainsResource, DomainsResource
from .resources.emails import AsyncEmailsResource, EmailsResource
from .resources.events import AsyncEventsResource, EventsResource
from .resources.identity import AsyncIdentityResource, IdentityResource
from .resources.messages import AsyncMessagesResource, MessagesResource
from .resources.organizations import AsyncOrganizationsResource, OrganizationsResource
from .resources.phones import AsyncPhonesResource, PhonesResource
from .resources.pods import AsyncPodsResource, PodsResource
from .resources.registry import AsyncRegistryResource, RegistryResource
from .resources.security import AsyncSecurityResource, SecurityResource
from .resources.vault import AsyncVaultResource, VaultResource
from .resources.wallet import AsyncWalletResource, WalletResource
from .resources.webhooks import AsyncWebhooksResource, WebhooksResource
from .resources.a2a import A2AResource, AsyncA2AResource


class Anima:
    """Synchronous Anima API client.

    Usage::

        client = Anima(api_key="sk-...")
        agent = client.agents.get("agent_id")
        client.close()

    Or as a context manager::

        with Anima(api_key="sk-...") as client:
            agent = client.agents.get("agent_id")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.addresses = AddressesResource(self._http)
        self.agents = AgentsResource(self._http)
        self.cards = CardsResource(self._http)
        self.domains = DomainsResource(self._http)
        self.emails = EmailsResource(self._http)
        self.events = EventsResource(self._http)
        self.identity = IdentityResource(self._http)
        self.messages = MessagesResource(self._http)
        self.organizations = OrganizationsResource(self._http)
        self.phones = PhonesResource(self._http)
        self.pods = PodsResource(self._http)
        self.registry = RegistryResource(self._http)
        self.security = SecurityResource(self._http)
        self.vault = VaultResource(self._http)
        self.wallet = WalletResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.a2a = A2AResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> Anima:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    @staticmethod
    def verify_webhook_signature(
        payload: str | bytes,
        signature_header: str,
        secret: str,
        tolerance_seconds: int = 300,
    ) -> bool:
        """Verify an incoming webhook signature."""
        return verify_webhook_signature(
            payload, signature_header, secret, tolerance_seconds
        )

    @staticmethod
    def construct_webhook_event(
        payload: str | bytes,
        signature_header: str,
        secret: str,
        tolerance_seconds: int = 300,
    ) -> WebhookEvent:  # noqa: F821
        """Verify and parse an incoming webhook payload into a WebhookEvent."""
        return construct_webhook_event(
            payload, signature_header, secret, tolerance_seconds
        )


class AsyncAnima:
    """Asynchronous Anima API client.

    Usage::

        client = AsyncAnima(api_key="sk-...")
        agent = await client.agents.get("agent_id")
        await client.close()

    Or as an async context manager::

        async with AsyncAnima(api_key="sk-...") as client:
            agent = await client.agents.get("agent_id")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._http = AsyncHTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.addresses = AsyncAddressesResource(self._http)
        self.agents = AsyncAgentsResource(self._http)
        self.cards = AsyncCardsResource(self._http)
        self.domains = AsyncDomainsResource(self._http)
        self.emails = AsyncEmailsResource(self._http)
        self.events = AsyncEventsResource(self._http)
        self.identity = AsyncIdentityResource(self._http)
        self.messages = AsyncMessagesResource(self._http)
        self.organizations = AsyncOrganizationsResource(self._http)
        self.phones = AsyncPhonesResource(self._http)
        self.pods = AsyncPodsResource(self._http)
        self.registry = AsyncRegistryResource(self._http)
        self.security = AsyncSecurityResource(self._http)
        self.vault = AsyncVaultResource(self._http)
        self.wallet = AsyncWalletResource(self._http)
        self.webhooks = AsyncWebhooksResource(self._http)
        self.a2a = AsyncA2AResource(self._http)

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.close()

    async def __aenter__(self) -> AsyncAnima:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    @staticmethod
    def verify_webhook_signature(
        payload: str | bytes,
        signature_header: str,
        secret: str,
        tolerance_seconds: int = 300,
    ) -> bool:
        """Verify an incoming webhook signature."""
        return verify_webhook_signature(
            payload, signature_header, secret, tolerance_seconds
        )

    @staticmethod
    def construct_webhook_event(
        payload: str | bytes,
        signature_header: str,
        secret: str,
        tolerance_seconds: int = 300,
    ) -> WebhookEvent:  # noqa: F821
        """Verify and parse an incoming webhook payload into a WebhookEvent."""
        return construct_webhook_event(
            payload, signature_header, secret, tolerance_seconds
        )
