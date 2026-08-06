"""Pydantic v2 models and enums matching the Node SDK types.ts."""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, Literal, TypeVar, Union

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Tier(str, Enum):
    """Organization subscription tier.

    Mirrors ``TierSchema`` in the anima contracts and the Prisma ``Tier`` enum.
    Because pydantic validates enum members, a value missing here is not a
    cosmetic gap: parsing an organization on that tier raises ValidationError.
    STARTER was missing while DEVELOPER and SCALE — which the API cannot
    return — were present, so every STARTER org failed to parse.
    """

    FREE = "FREE"
    STARTER = "STARTER"
    GROWTH = "GROWTH"
    ENTERPRISE = "ENTERPRISE"


class AgentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class PhoneProvider(str, Enum):
    TELNYX = "TELNYX"


class TenDlcStatus(str, Enum):
    PENDING = "PENDING"
    REGISTERED = "REGISTERED"
    REJECTED = "REJECTED"
    NOT_REQUIRED = "NOT_REQUIRED"


class MessageChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    MMS = "MMS"
    VOICE = "VOICE"


class MessageDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class MessageStatus(str, Enum):
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"
    BLOCKED = "BLOCKED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class VerificationMethod(str, Enum):
    DNS_TXT = "DNS_TXT"
    DNS_CNAME = "DNS_CNAME"


class DomainStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"
    VERIFYING = "VERIFYING"
    VERIFIED = "VERIFIED"
    INVALID = "INVALID"
    FAILED = "FAILED"


class DomainRecordStatus(str, Enum):
    MISSING = "MISSING"
    INVALID = "INVALID"
    VALID = "VALID"


class CredentialType(str, Enum):
    LOGIN = "login"
    SECURE_NOTE = "secure_note"
    CARD = "card"
    IDENTITY = "identity"
    OAUTH_TOKEN = "oauth_token"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"


class RevealPolicy(str, Enum):
    """Governs a credential's plaintext reveal paths.

    BROKERED refuses reveal and export on every key type — including the org
    master key — so the secret is only usable through ``use_credential``
    (recovery = rotation).
    """

    STANDARD = "standard"
    BROKERED = "brokered"


class CredentialRequestStatus(str, Enum):
    PENDING = "PENDING"
    FULFILLED = "FULFILLED"
    EXPIRED = "EXPIRED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"


class WebhookEventType(str, Enum):
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    MESSAGE_FAILED = "message.failed"
    MESSAGE_BOUNCED = "message.bounced"
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"
    PHONE_PROVISIONED = "phone.provisioned"
    PHONE_RELEASED = "phone.released"


class SecurityEventType(str, Enum):
    PII_DETECTED = "PII_DETECTED"
    INJECTION_DETECTED = "INJECTION_DETECTED"
    RATE_LIMITED = "RATE_LIMITED"
    BLOCKED = "BLOCKED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SecuritySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PolicyAction(str, Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ALWAYS_DECLINE = "ALWAYS_DECLINE"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    REVERSED = "REVERSED"
    EXPIRED = "EXPIRED"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class VaultCustomFieldType(str, Enum):
    TEXT = "text"
    HIDDEN = "hidden"
    BOOLEAN = "boolean"


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


class CursorPagination(BaseModel):
    next_cursor: str | None = Field(None, alias="nextCursor")
    has_more: bool = Field(alias="hasMore")

    model_config = {"populate_by_name": True}


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    pagination: CursorPagination

    model_config = {"populate_by_name": True}


class CursorPage(BaseModel, Generic[T]):
    """A list response that carries its cursor FLAT rather than nested.

    Roughly a third of the API's list endpoints answer ``{items, nextCursor}``
    instead of ``{items, pagination: {nextCursor, hasMore}}`` -- audit logs,
    anomaly alerts and rules, compliance controls/reports/dsars, A2A tasks.
    Validating those against :class:`PaginatedResponse` raises, because
    ``pagination`` is simply not there. That is not a hypothetical: every one
    of those methods raised on every call until 2026-08-04.

    Neither envelope is "the standard" -- the split is 23 to 24 across the
    contracts -- so the SDK models both rather than pretending the API is
    uniform.

    ``pagination`` is exposed as a derived property so this stays a drop-in for
    code written against ``PaginatedResponse``: ``page.items`` and
    ``page.pagination.next_cursor`` both keep working, and the auto-paginating
    iterators need no special case.
    """

    items: list[T]
    next_cursor: str | None = Field(None, alias="nextCursor")
    # Only some of these endpoints report a total, and they disagree on the
    # name (audit logs say totalCount, registry search says total). None means
    # the endpoint did not send one -- never "zero results".
    total_count: int | None = Field(None, alias="totalCount")

    model_config = {"populate_by_name": True}

    @property
    def pagination(self) -> CursorPagination:
        """The nested shape, derived.

        ``has_more`` is not sent by these endpoints; a null ``nextCursor`` is
        how they say "no more pages", so it is derived rather than guessed.
        """
        return CursorPagination(
            next_cursor=self.next_cursor,
            has_more=self.next_cursor is not None,
        )


class DateRange(BaseModel):
    from_: str | None = Field(None, alias="from")
    to: str | None = None

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------


class OrganizationOutput(BaseModel):
    id: str
    name: str
    slug: str
    clerk_org_id: str | None = Field(None, alias="clerkOrgId")
    tier: Tier
    master_key: str = Field(alias="masterKey")
    settings: dict[str, Any]
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Email / Phone identities
# ---------------------------------------------------------------------------


class EmailIdentityOutput(BaseModel):
    id: str
    email: str
    domain: str
    local_part: str = Field(alias="localPart")
    is_primary: bool = Field(alias="isPrimary")
    verified: bool
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class InboxOutput(BaseModel):
    id: str
    email: str
    domain: str
    local_part: str = Field(alias="localPart")
    display_name: str | None = Field(None, alias="displayName")
    agent_id: str | None = Field(None, alias="agentId")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class PhoneCapabilities(BaseModel):
    sms: bool
    mms: bool
    voice: bool


class PhoneIdentityOutput(BaseModel):
    id: str
    phone_number: str = Field(alias="phoneNumber")
    provider: PhoneProvider
    provider_id: str | None = Field(None, alias="providerId")
    capabilities: PhoneCapabilities
    ten_dlc_status: TenDlcStatus = Field(alias="tenDlcStatus")
    is_primary: bool = Field(alias="isPrimary")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


class AgentOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    name: str
    slug: str
    status: AgentStatus
    api_key_prefix: str | None = Field(None, alias="apiKeyPrefix")
    metadata: dict[str, Any]
    email_identities: list[EmailIdentityOutput] = Field(alias="emailIdentities")
    phone_identities: list[PhoneIdentityOutput] = Field(alias="phoneIdentities")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


class AttachmentOutput(BaseModel):
    id: str
    filename: str
    mime_type: str = Field(alias="mimeType")
    size_bytes: int = Field(alias="sizeBytes")
    storage_key: str = Field(alias="storageKey")
    url: str | None = None
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class MessageOutput(BaseModel):
    id: str
    agent_id: str = Field(alias="agentId")
    channel: MessageChannel
    direction: MessageDirection
    status: MessageStatus
    from_address: str = Field(alias="fromAddress")
    to_address: str = Field(alias="toAddress")
    subject: str | None = None
    body: str
    body_html: str | None = Field(None, alias="bodyHtml")
    headers: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    thread_id: str | None = Field(None, alias="threadId")
    in_reply_to: str | None = Field(None, alias="inReplyTo")
    external_id: str | None = Field(None, alias="externalId")
    sent_at: str | None = Field(None, alias="sentAt")
    received_at: str | None = Field(None, alias="receivedAt")
    attachments: list[AttachmentOutput]
    #: Workflow labels on this message. Always contains exactly one of the
    #: system labels ``unread`` or ``read``; may also contain ``archived``,
    #: ``spam`` (the inbound spam verdict) and any labels you add. Change them
    #: with ``messages.update_labels()``. Defaults to empty so a client on this
    #: version keeps parsing messages served by an API that predates B3.
    labels: list[str] = Field(default_factory=list)
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class AttachmentDownloadOutput(BaseModel):
    url: str
    expires_at: str = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class SemanticSearchResult(BaseModel):
    """A message matched by semantic (embedding) search, ranked by similarity."""

    id: str
    content: str
    similarity: float
    channel: str
    direction: str
    agent_id: str = Field(alias="agentId")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Email drafts
# ---------------------------------------------------------------------------


class EmailDraftOutput(BaseModel):
    """A composed-but-not-sent email owned by an agent.

    Unlike a :class:`MessageOutput`, a draft may be incomplete (no recipients,
    subject, or body yet) and has no thread/status/delivery state. Sending a
    draft converts it into a Message and deletes the draft row.
    """

    id: str
    agent_id: str = Field(alias="agentId")
    org_id: str = Field(alias="orgId")
    from_identity_id: str | None = Field(None, alias="fromIdentityId")
    to: list[str]
    cc: list[str]
    bcc: list[str]
    subject: str | None = None
    body: str | None = None
    body_html: str | None = Field(None, alias="bodyHtml")
    in_reply_to: str | None = Field(None, alias="inReplyTo")
    references: list[str]
    metadata: dict[str, Any] | None = None
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Domains
# ---------------------------------------------------------------------------


class DomainStatusRecord(BaseModel):
    type: str
    name: str
    value: str
    priority: int | None = None
    status: DomainRecordStatus


class DomainOutput(BaseModel):
    id: str
    domain: str
    status: DomainStatus
    verified: bool
    verification_cooldown_until: str | None = Field(None, alias="verificationCooldownUntil")
    verification_token: str = Field(alias="verificationToken")
    verification_method: VerificationMethod = Field(alias="verificationMethod")
    dkim_selector: str | None = Field(None, alias="dkimSelector")
    dkim_public_key: str | None = Field(None, alias="dkimPublicKey")
    spf_configured: bool = Field(alias="spfConfigured")
    dmarc_configured: bool = Field(alias="dmarcConfigured")
    mx_configured: bool = Field(alias="mxConfigured")
    feedback_enabled: bool = Field(alias="feedbackEnabled")
    records: list[DomainStatusRecord] | None = None
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class DomainDnsRecord(BaseModel):
    name: str
    value: str


class DomainDnsRecordWithPriority(BaseModel):
    name: str
    value: str
    priority: int


class DomainMailFromConfig(BaseModel):
    name: str
    mx: DomainDnsRecordWithPriority
    spf: str


class DomainDnsRecordsOutput(BaseModel):
    txt: DomainDnsRecord
    mail_from: DomainMailFromConfig = Field(alias="mailFrom")
    dkim: list[DomainDnsRecord]
    mx: DomainDnsRecordWithPriority
    spf: str
    dmarc: str

    model_config = {"populate_by_name": True}


class DomainZoneFileOutput(BaseModel):
    zone_file: str = Field(alias="zoneFile")

    model_config = {"populate_by_name": True}


class DeliverabilityStatsOutput(BaseModel):
    domain: str
    sent: int
    delivered: int
    bounced: int
    complained: int
    bounce_rate: float = Field(alias="bounceRate")
    complaint_rate: float = Field(alias="complaintRate")
    is_healthy: bool = Field(alias="isHealthy")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------


class AddressType(str, Enum):
    BILLING = "BILLING"
    SHIPPING = "SHIPPING"
    MAILING = "MAILING"
    REGISTERED = "REGISTERED"


class AddressOutput(BaseModel):
    id: str
    agent_id: str = Field(alias="agentId")
    type: AddressType
    label: str | None = None
    street1: str
    street2: str | None = None
    city: str
    state: str
    postal_code: str = Field(alias="postalCode")
    country: str
    validated: bool
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class ValidateAddressOutput(BaseModel):
    valid: bool
    normalized_address: AddressOutput | None = Field(None, alias="normalizedAddress")
    errors: list[str]

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Phones
# ---------------------------------------------------------------------------


class PhoneProvisionOutput(BaseModel):
    id: str
    phone_number: str = Field(alias="phoneNumber")
    provider: PhoneProvider
    provider_id: str | None = Field(None, alias="providerId")
    capabilities: PhoneCapabilities
    ten_dlc_status: TenDlcStatus = Field(alias="tenDlcStatus")
    is_primary: bool = Field(alias="isPrimary")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------


class VaultIdentityOutput(BaseModel):
    id: str
    agent_id: str = Field(alias="agentId")
    org_id: str = Field(alias="orgId")
    # Identifiers in the vault backend. None until provisioning completes.
    vault_user_id: str | None = Field(None, alias="vaultUserId")
    vault_org_id: str | None = Field(None, alias="vaultOrgId")
    collection_id: str | None = Field(None, alias="collectionId")
    # One of ACTIVE, LOCKED, ERROR.
    status: str
    credential_count: int = Field(alias="credentialCount")
    last_sync_at: str | None = Field(None, alias="lastSyncAt")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class VaultIdentityListItem(VaultIdentityOutput):
    agent_name: str = Field(alias="agentName")
    agent_slug: str = Field(alias="agentSlug")


class VaultAuditLogEntry(BaseModel):
    """Credential audit entry — never contains secret material."""

    id: str
    credential_id: str = Field(alias="credentialId")
    agent_id: str = Field(alias="agentId")
    org_id: str = Field(alias="orgId")
    # e.g. access, store, delete, share, broker_use, broker_use_denied
    action: str
    actor: str
    ip_address: str | None = Field(None, alias="ipAddress")
    metadata: dict[str, Any] | None = None
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class VaultLoginUri(BaseModel):
    uri: str
    match: str | None = None


class VaultLoginData(BaseModel):
    username: str | None = None
    password: str | None = None
    uris: list[VaultLoginUri] | None = None
    totp: str | None = None


class VaultCardData(BaseModel):
    cardholder_name: str | None = Field(None, alias="cardholderName")
    brand: str | None = None
    number: str | None = None
    exp_month: str | None = Field(None, alias="expMonth")
    exp_year: str | None = Field(None, alias="expYear")
    code: str | None = None

    model_config = {"populate_by_name": True}


class VaultIdentityData(BaseModel):
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    email: str | None = None
    phone: str | None = None
    address1: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = Field(None, alias="postalCode")
    country: str | None = None
    company: str | None = None

    model_config = {"populate_by_name": True}


class VaultCustomField(BaseModel):
    name: str
    value: str
    type: VaultCustomFieldType


class VaultRateLimit(BaseModel):
    requests: int
    window: str  # e.g. "1m", "1h", "1d"


class VaultApiKeyData(BaseModel):
    provider: str
    key: str  # stored encrypted; always read back masked
    prefix: str | None = None
    rate_limit: VaultRateLimit | None = Field(None, alias="rateLimit")
    expires_at: str | None = Field(None, alias="expiresAt")
    scopes: list[str] | None = None
    # Hosts this key may be brokered to via use_credential. Fail-closed:
    # with no hosts the broker refuses every call. After creation only a
    # master key may change this list.
    allowed_hosts: list[str] | None = Field(None, alias="allowedHosts")
    auth_header: str | None = Field(None, alias="authHeader")
    auth_scheme: str | None = Field(None, alias="authScheme")

    model_config = {"populate_by_name": True}


class VaultOAuthTokenData(BaseModel):
    provider: str
    access_token: str = Field(alias="accessToken")  # read back masked
    refresh_token: str | None = Field(None, alias="refreshToken")  # never read back
    token_endpoint: str | None = Field(None, alias="tokenEndpoint")
    client_id: str | None = Field(None, alias="clientId")
    client_secret: str | None = Field(None, alias="clientSecret")
    scopes: list[str] | None = None
    expires_at: str | None = Field(None, alias="expiresAt")
    auto_refresh: bool | None = Field(None, alias="autoRefresh")
    allowed_hosts: list[str] | None = Field(None, alias="allowedHosts")

    model_config = {"populate_by_name": True}


class VaultCertificateData(BaseModel):
    format: str  # "pem" | "p12" | "jks"
    certificate: str
    private_key: str = Field(alias="privateKey")  # read back masked
    chain: list[str] | None = None
    expires_at: str | None = Field(None, alias="expiresAt")

    model_config = {"populate_by_name": True}


class VaultCredential(BaseModel):
    id: str
    type: CredentialType
    name: str
    notes: str | None = None
    login: VaultLoginData | None = None
    card: VaultCardData | None = None
    identity: VaultIdentityData | None = None
    oauth_token: VaultOAuthTokenData | None = Field(None, alias="oauthToken")
    api_key: VaultApiKeyData | None = Field(None, alias="apiKey")
    certificate: VaultCertificateData | None = None
    fields: list[VaultCustomField] | None = None
    favorite: bool
    reveal_policy: RevealPolicy | None = Field(None, alias="revealPolicy")
    folder_id: str | None = Field(None, alias="folderId")
    organization_id: str | None = Field(None, alias="organizationId")
    collection_ids: list[str] | None = Field(None, alias="collectionIds")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class VaultTotpOutput(BaseModel):
    code: str
    period: int


class VaultStatusOutput(BaseModel):
    server_url: str = Field(alias="serverUrl")
    last_sync: str | None = Field(None, alias="lastSync")
    status: str

    model_config = {"populate_by_name": True}


class VaultShare(BaseModel):
    id: str
    credential_id: str = Field(alias="credentialId")
    source_agent_id: str = Field(alias="sourceAgentId")
    target_agent_id: str = Field(alias="targetAgentId")
    permission: str  # "READ" | "USE" | "MANAGE"
    expires_at: str | None = Field(None, alias="expiresAt")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class VaultTokenOutput(BaseModel):
    token: str
    credential_id: str = Field(alias="credentialId")
    scope: str  # "autofill" | "proxy" | "export"
    expires_at: str = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class VaultRevokeTokensResult(BaseModel):
    success: bool
    revoked: int


class VaultCredentialRequest(BaseModel):
    """A human-in-the-loop credential request (the secret is filled out-of-band)."""

    request_id: str = Field(alias="requestId")
    fill_url: str = Field(alias="fillUrl")
    status: CredentialRequestStatus
    expires_at: str = Field(alias="expiresAt")
    email_sent: bool = Field(alias="emailSent")
    credential_id: str | None = Field(None, alias="credentialId")

    model_config = {"populate_by_name": True}


class VaultCredentialRequestStatusOutput(BaseModel):
    status: CredentialRequestStatus
    credential_id: str | None = Field(None, alias="credentialId")
    # Masked preview (e.g. ****1234) — never the plaintext.
    masked_preview: str | None = Field(None, alias="maskedPreview")

    model_config = {"populate_by_name": True}


class VaultCredentialRequestCancelResult(BaseModel):
    status: CredentialRequestStatus


class VaultCredentialRequestListItem(BaseModel):
    """A credential request in the org-wide list.

    Distinct from :class:`VaultCredentialRequest`, which is what creating one
    returns: this carries the requesting agent, type, reason and createdAt, and
    its ``fill_url`` is present only while PENDING.
    """

    request_id: str = Field(alias="requestId")
    agent_id: str = Field(alias="agentId")
    type: CredentialType
    name: str
    reason: str
    status: CredentialRequestStatus
    # Present only while PENDING -- the URL stops working once filled.
    fill_url: str | None = Field(None, alias="fillUrl")
    credential_id: str | None = Field(None, alias="credentialId")
    expires_at: str = Field(alias="expiresAt")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class UseCredentialOutput(BaseModel):
    """The upstream response from a brokered call, scrubbed of the credential."""

    status: int
    headers: dict[str, str]
    body: str
    # True when the body exceeded the size cap and was cut off.
    truncated: bool


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------


class WebhookOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    url: str
    events: list[WebhookEventType]
    active: bool
    description: str | None = None
    consecutive_failures: int = Field(alias="consecutiveFailures", default=0)
    disabled_reason: str | None = Field(alias="disabledReason", default=None)
    disabled_at: str | None = Field(alias="disabledAt", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    auth_type: Literal["NONE", "BEARER", "BASIC", "CUSTOM_HEADER"] = Field("NONE", alias="authType")
    auth_header_name: str | None = Field(None, alias="authHeaderName")
    rate_limit_per_minute: int | None = Field(None, alias="rateLimitPerMinute")
    max_attempts: int | None = Field(None, alias="maxAttempts")

    model_config = {"populate_by_name": True}


class WebhookTestOutput(BaseModel):
    success: Literal[True]
    delivery_id: str = Field(alias="deliveryId")

    model_config = {"populate_by_name": True}


class WebhookDeliveryOutput(BaseModel):
    id: str
    webhook_id: str = Field(alias="webhookId")
    message_id: str | None = Field(None, alias="messageId")
    event: WebhookEventType
    payload: dict[str, Any]
    status_code: int | None = Field(None, alias="statusCode")
    response_body: str | None = Field(None, alias="responseBody")
    attempts: int
    max_attempts: int = Field(alias="maxAttempts")
    next_attempt_at: str | None = Field(None, alias="nextAttemptAt")
    completed_at: str | None = Field(None, alias="completedAt")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class WebhookEvent(BaseModel):
    """Parsed webhook event payload."""

    id: str | None = None
    type: WebhookEventType
    created_at: str | None = Field(None, alias="createdAt")
    data: dict[str, Any]

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Webhook auth config (input)
#
# Auth the platform presents to your webhook endpoint on each delivery, IN
# ADDITION to the always-on X-Anima-Signature HMAC. Construct one of the
# variants below and pass it as `auth_config` to webhooks.create/update. The
# credential is write-only — it is never returned on reads.
# ---------------------------------------------------------------------------


class WebhookAuthNone(BaseModel):
    """No customer auth header (the HMAC signature is still sent)."""

    type: Literal["none"] = "none"

    model_config = {"populate_by_name": True}


class WebhookAuthBearer(BaseModel):
    """Bearer token, sent as ``Authorization: Bearer <token>``."""

    type: Literal["bearer"] = "bearer"
    token: str

    model_config = {"populate_by_name": True}


class WebhookAuthBasic(BaseModel):
    """HTTP basic auth, sent as ``Authorization: Basic <base64(user:pass)>``."""

    type: Literal["basic"] = "basic"
    username: str
    password: str

    model_config = {"populate_by_name": True}


class WebhookAuthCustomHeader(BaseModel):
    """Custom header, sent as ``<header_name>: <value>``."""

    type: Literal["custom_header"] = "custom_header"
    header_name: str = Field(alias="headerName")
    value: str

    model_config = {"populate_by_name": True}


WebhookAuthConfig = Union[
    WebhookAuthNone,
    WebhookAuthBearer,
    WebhookAuthBasic,
    WebhookAuthCustomHeader,
]
"""Auth the platform presents to your endpoint (in addition to the HMAC signature)."""


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------


# SecurityScanWarning/SecurityScanOutput used to sit here. They typed a
# POST /security/scan endpoint the API has never served -- scanning runs
# inside the send paths, not as a callable route. The security surface that
# does exist is the event feed and the scanner status below.


class AiScannerStatus(BaseModel):
    """Whether the scanner runs on traffic, not merely whether one is configured."""

    active: bool
    provider: str | None = None
    fallback_reason: str | None = Field(None, alias="fallbackReason")

    model_config = {"populate_by_name": True}


class ScannerStatusOutput(BaseModel):
    ai_scanner: AiScannerStatus = Field(alias="aiScanner")

    model_config = {"populate_by_name": True}


class SecurityEventOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    agent_id: str | None = Field(None, alias="agentId")
    message_id: str | None = Field(None, alias="messageId")
    type: SecurityEventType
    severity: SecuritySeverity
    details: dict[str, Any]
    resolved: bool
    resolved_by: str | None = Field(None, alias="resolvedBy")
    resolved_at: str | None = Field(None, alias="resolvedAt")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Real-time Events (WebSocket)
# ---------------------------------------------------------------------------


class AnimaEvent(BaseModel):
    """A real-time event received over WebSocket."""

    id: str
    event_type: str = Field(alias="eventType")
    agent_id: str | None = Field(None, alias="agentId")
    org_id: str = Field(alias="orgId")
    timestamp: str
    data: dict[str, Any]

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Identity (DID / Verifiable Credentials)
# ---------------------------------------------------------------------------


class DidDocument(BaseModel):
    did: str
    agent_id: str = Field(alias="agentId")
    document: dict[str, Any]
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class DidRotateOutput(BaseModel):
    did: str
    agent_id: str = Field(alias="agentId")
    document: dict[str, Any]
    previous_did: str | None = Field(None, alias="previousDid")
    rotated_at: str = Field(alias="rotatedAt")

    model_config = {"populate_by_name": True}


class VerifiableCredentialRecord(BaseModel):
    """The platform's record of an issued credential.

    The signed credential itself is ``jwt_vc``; everything else is Anima's
    bookkeeping (issuance, expiry, revocation).
    """

    id: str
    agent_id: str = Field(alias="agentId")
    org_id: str = Field(alias="orgId")
    type: str
    jwt_vc: str = Field(alias="jwtVc")
    issuer_did: str = Field(alias="issuerDid")
    subject_did: str = Field(alias="subjectDid")
    issued_at: str = Field(alias="issuedAt")
    expires_at: str | None = Field(None, alias="expiresAt")
    revoked: bool
    revoked_at: str | None = Field(None, alias="revokedAt")
    revocation_index: int | None = Field(None, alias="revocationIndex")
    metadata: dict[str, Any] | None = None
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class VerifiableCredentialType(str, Enum):
    """The credential types Anima issues.

    Platform verification events auto-issue EMAIL_VERIFIED/OWNER_BOUND (email
    OTP), PHONE_VERIFIED (number provisioning), and PAYMENT_CAPABLE (paid
    Stripe checkout). Those, plus KYB_COMPLETED, derive the agent card's public
    verification level and are platform-reserved -- asking for them via
    ``identity.issue_credential`` returns 403. Only the org-attestation types
    (ADDRESS_VERIFIED, TRUST_SCORE) are issuable there.
    """

    EMAIL_VERIFIED = "AnimaEmailVerified"
    PHONE_VERIFIED = "AnimaPhoneVerified"
    ADDRESS_VERIFIED = "AnimaAddressVerified"
    KYB_COMPLETED = "AnimaKYBCompleted"
    PAYMENT_CAPABLE = "AnimaPaymentCapable"
    OWNER_BOUND = "AnimaOwnerBound"
    TRUST_SCORE = "AnimaTrustScore"


class VerifyCredentialOutput(BaseModel):
    valid: bool
    # The decoded JWT-VC payload, left opaque: the contract types it as
    # z.record(z.unknown()).nullable() and the value is a JwtVcPayload --
    # {iss, sub, vc, iat, exp, jti}, with the W3C credential under "vc".
    # It was modelled as a flat W3C document, so every field parsed as
    # missing. Non-None for most invalid results too (revoked, expired,
    # bad signature all decode), so branch on `valid`, not on this.
    credential: dict[str, Any] | None = None
    errors: list[str]


class AgentCardOutput(BaseModel):
    did: str
    agent_id: str = Field(alias="agentId")
    name: str
    description: str | None = None
    capabilities: list[str]
    endpoints: dict[str, str]
    metadata: dict[str, Any]
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class RegistryAgentOutput(BaseModel):
    did: str
    name: str
    description: str | None = None
    category: str | None = None
    capabilities: list[str]
    endpoints: dict[str, str]
    metadata: dict[str, Any]
    verified: bool
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Wallet and Pods models used to live here. Both products were removed from
# the API -- there is no /agents/{id}/wallet or /pods route -- so the models
# and their resources went with them.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# A2A (Agent-to-Agent Protocol)
# ---------------------------------------------------------------------------


class A2ATaskStatus(str, Enum):
    # lowercase, because A2ATaskStatusEnum in the contract is
    # ["submitted", "working", "input_required", "completed", "failed",
    # "canceled"]. These were UPPERCASE until 2026-08-04 -- the same
    # casing defect as AuditActorType but in the opposite direction, which is
    # why "just uppercase everything" is not the rule. Note the API spells it
    # "canceled" with one L.
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"


class A2AArtifact(BaseModel):
    name: str
    mime_type: str = Field(alias="mimeType")
    data: str

    model_config = {"populate_by_name": True}


class A2ATaskOutput(BaseModel):
    id: str
    agent_id: str = Field(alias="agentId")
    type: str
    status: A2ATaskStatus
    input: dict[str, Any]
    output: dict[str, Any] | None = None
    artifacts: list[A2AArtifact]
    from_did: str | None = Field(None, alias="fromDid")
    error: str | None = None
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


class AuditActorType(str, Enum):
    # UPPERCASE because AuditActorTypeEnum in the contract is
    # ["API_KEY", "USER", "SYSTEM", "AGENT"]. These were lowercase until
    # 2026-08-04, which made every audit-log read raise in this SDK and fail
    # silently in the node and go ones. Do not "normalise" the casing.
    API_KEY = "API_KEY"
    USER = "USER"
    SYSTEM = "SYSTEM"
    AGENT = "AGENT"


class AuditResult(str, Enum):
    # UPPERCASE -- see AuditActorType above.
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    DENIED = "DENIED"


class AuditLogOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    actor_type: AuditActorType = Field(alias="actorType")
    actor_id: str = Field(alias="actorId")
    action: str
    resource_type: str = Field(alias="resourceType")
    resource_id: str = Field(alias="resourceId")
    result: AuditResult
    ip_address: str | None = Field(None, alias="ipAddress")
    user_agent: str | None = Field(None, alias="userAgent")
    metadata: dict[str, Any] | None = None
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class AuditLogExportOutput(BaseModel):
    url: str
    format: str
    record_count: int = Field(alias="recordCount")
    expires_at: str = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Compliance
# ---------------------------------------------------------------------------


class ComplianceFramework(str, Enum):
    SOC2 = "SOC2"
    GDPR = "GDPR"
    PCI = "PCI"


# Every value below is SCREAMING_SNAKE because that is what the API validates
# against -- packages/contracts/src/schemas/compliance.py{,-controls} in the
# monorepo. These were lowercase, so every compliance request this SDK built
# was rejected. tests/test_compliance.py pins them.
class ComplianceControlStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    IMPLEMENTED = "IMPLEMENTED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class ComplianceControlCategory(str, Enum):
    CC1 = "CC1"
    CC2 = "CC2"
    CC3 = "CC3"
    CC4 = "CC4"
    CC5 = "CC5"
    CC6 = "CC6"
    CC7 = "CC7"
    CC8 = "CC8"
    CC9 = "CC9"
    A1 = "A1"
    PI1 = "PI1"
    C1 = "C1"
    P1 = "P1"


class ComplianceReportType(str, Enum):
    SOC2_SUMMARY = "SOC2_SUMMARY"
    ACTIVITY_REPORT = "ACTIVITY_REPORT"
    ACCESS_REVIEW = "ACCESS_REVIEW"
    AUDIT_EXPORT = "AUDIT_EXPORT"
    GDPR_DSAR = "GDPR_DSAR"


class ComplianceReportStatus(str, Enum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ComplianceReportFormat(str, Enum):
    JSON = "JSON"
    CSV = "CSV"
    PDF = "PDF"


class DsarType(str, Enum):
    ACCESS = "ACCESS"
    DELETE = "DELETE"
    RECTIFY = "RECTIFY"
    PORTABILITY = "PORTABILITY"
    RESTRICT = "RESTRICT"


class DsarStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VERIFIED = "VERIFIED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DENIED = "DENIED"
    OVERDUE = "OVERDUE"


class ComplianceControlOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    framework: ComplianceFramework
    control_id: str = Field(alias="controlId")
    title: str
    description: str
    category: ComplianceControlCategory
    status: ComplianceControlStatus
    owner: str | None = None
    last_tested_at: str | None = Field(None, alias="lastTestedAt")
    next_review_at: str | None = Field(None, alias="nextReviewAt")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class SeedFrameworkOutput(BaseModel):
    controls_created: int = Field(alias="controlsCreated")
    framework: ComplianceFramework

    model_config = {"populate_by_name": True}


class ComplianceReportOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    type: ComplianceReportType
    title: str
    description: str | None = None
    status: ComplianceReportStatus
    format: ComplianceReportFormat
    parameters: dict[str, Any] = Field(default_factory=dict)
    content: dict[str, Any] | None = None
    error_message: str | None = Field(None, alias="errorMessage")
    generated_by: str | None = Field(None, alias="generatedBy")
    period_start: str | None = Field(None, alias="periodStart")
    period_end: str | None = Field(None, alias="periodEnd")
    completed_at: str | None = Field(None, alias="completedAt")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class ExportReportOutput(BaseModel):
    """The export comes back inline. There is no signed download URL."""

    data: str
    content_type: str = Field(alias="contentType")
    filename: str

    model_config = {"populate_by_name": True}


class ComplianceTemplateOutput(BaseModel):
    type: str
    title: str
    description: str


class ListTemplatesOutput(BaseModel):
    items: list[ComplianceTemplateOutput] = Field(default_factory=list)


class DashboardReportSummary(BaseModel):
    id: str
    type: str
    title: str
    status: str
    created_at: str = Field(alias="createdAt")
    completed_at: str | None = Field(None, alias="completedAt")

    model_config = {"populate_by_name": True}


class DashboardDsarSummary(BaseModel):
    id: str
    type: str
    status: str
    subject_email: str = Field(alias="subjectEmail")
    due_at: str = Field(alias="dueAt")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class DashboardReportsSection(BaseModel):
    total: int
    by_type: dict[str, int] = Field(default_factory=dict, alias="byType")
    by_status: dict[str, int] = Field(default_factory=dict, alias="byStatus")
    recent_reports: list[DashboardReportSummary] = Field(
        default_factory=list, alias="recentReports"
    )

    model_config = {"populate_by_name": True}


class DashboardDsarsSection(BaseModel):
    total: int
    by_status: dict[str, int] = Field(default_factory=dict, alias="byStatus")
    by_type: dict[str, int] = Field(default_factory=dict, alias="byType")
    overdue: int = 0
    average_resolution_days: float | None = Field(None, alias="averageResolutionDays")
    recent_requests: list[DashboardDsarSummary] = Field(
        default_factory=list, alias="recentRequests"
    )

    model_config = {"populate_by_name": True}


class ComplianceFrameworkSummary(BaseModel):
    framework: str
    total_controls: int = Field(alias="totalControls")
    implemented_count: int = Field(alias="implementedCount")
    progress: int

    model_config = {"populate_by_name": True}


class DashboardComplianceSection(BaseModel):
    overall_progress: int = Field(alias="overallProgress")
    framework_summaries: list[ComplianceFrameworkSummary] = Field(
        default_factory=list, alias="frameworkSummaries"
    )

    model_config = {"populate_by_name": True}


class ComplianceDashboardOutput(BaseModel):
    reports: DashboardReportsSection
    dsars: DashboardDsarsSection
    compliance: DashboardComplianceSection

    model_config = {"populate_by_name": True}


class DsarOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    type: DsarType
    status: DsarStatus
    subject_email: str = Field(alias="subjectEmail")
    subject_name: str | None = Field(None, alias="subjectName")
    subject_id: str | None = Field(None, alias="subjectId")
    description: str | None = None
    requested_at: str = Field(alias="requestedAt")
    verified_at: str | None = Field(None, alias="verifiedAt")
    due_at: str = Field(alias="dueAt")
    completed_at: str | None = Field(None, alias="completedAt")
    processed_by: str | None = Field(None, alias="processedBy")
    response: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Anomaly Detection
# ---------------------------------------------------------------------------


class AnomalyMetric(str, Enum):
    EMAIL_SEND_RATE = "email_send_rate"
    SMS_SEND_RATE = "sms_send_rate"
    VAULT_ACCESS_RATE = "vault_access_rate"
    API_CALL_RATE = "api_call_rate"
    UNIQUE_RECIPIENTS = "unique_recipients"


class AnomalySeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AnomalyAlertStatus(str, Enum):
    TRIGGERED = "TRIGGERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class AnomalyCondition(str, Enum):
    ZSCORE_GT = "zscore_gt"
    RATE_MULTIPLIER_GT = "rate_multiplier_gt"
    ABSOLUTE_GT = "absolute_gt"
    TIME_VIOLATION = "time_violation"


class QuarantineAction(str, Enum):
    NONE = "NONE"
    SOFT = "SOFT"
    HARD = "HARD"


class QuarantineLevel(str, Enum):
    NONE = "NONE"
    SOFT = "SOFT"
    HARD = "HARD"


class BaselinePeriod(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"


class AnomalyAlertOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    agent_id: str = Field(alias="agentId")
    metric: AnomalyMetric
    severity: AnomalySeverity
    status: AnomalyAlertStatus
    baseline_value: float = Field(alias="baselineValue")
    actual_value: float = Field(alias="actualValue")
    z_score: float = Field(alias="zScore")
    rule_id: str | None = Field(None, alias="ruleId")
    details: dict[str, Any] | None = None
    acknowledged_by: str | None = Field(None, alias="acknowledgedBy")
    acknowledged_at: str | None = Field(None, alias="acknowledgedAt")
    resolved_by: str | None = Field(None, alias="resolvedBy")
    resolved_at: str | None = Field(None, alias="resolvedAt")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class AnomalyRuleOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    name: str
    metric: AnomalyMetric
    condition: AnomalyCondition
    threshold: float
    severity: AnomalySeverity
    quarantine_action: QuarantineAction = Field(alias="quarantineAction")
    cooldown_minutes: int = Field(alias="cooldownMinutes")
    enabled: bool
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class BaselineMetric(BaseModel):
    metric: AnomalyMetric
    period: BaselinePeriod
    mean: float
    stddev: float
    sample_count: int = Field(alias="sampleCount")
    hourly_pattern: dict[str, float] | None = Field(None, alias="hourlyPattern")
    window_start: str = Field(alias="windowStart")
    window_end: str = Field(alias="windowEnd")

    model_config = {"populate_by_name": True}


class AgentBaselineOutput(BaseModel):
    agent_id: str = Field(alias="agentId")
    org_id: str = Field(alias="orgId")
    metrics: list[BaselineMetric]

    model_config = {"populate_by_name": True}


class QuarantineOutput(BaseModel):
    agent_id: str = Field(alias="agentId")
    quarantine_level: QuarantineLevel = Field(alias="quarantineLevel")
    quarantined_at: str | None = Field(None, alias="quarantinedAt")
    reason: str | None = None

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Voice / Calls
# ---------------------------------------------------------------------------


class VoiceTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"


class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class CallDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class Voice(BaseModel):
    """A catalog voice. Vendor-neutral: the underlying provider/model is never
    exposed — only descriptive metadata and a proxied preview URL."""

    id: str
    name: str
    gender: VoiceGender
    accent: str | None = None
    age: str | None = None
    descriptors: list[str]
    use_cases: list[str] = Field(alias="useCases")
    language: str
    #: Vendor-neutral preview URL under the API host — the client never touches
    #: the provider CDN. ``None`` until a sample clip has been generated.
    sample_url: str | None = Field(None, alias="sampleUrl")

    model_config = {"populate_by_name": True}


class CallOutput(BaseModel):
    id: str
    agent_id: str = Field(alias="agentId")
    phone_identity_id: str = Field(alias="phoneIdentityId")
    direction: CallDirection
    tier: VoiceTier
    state: str
    from_number: str = Field(alias="from")
    to: str
    started_at: str = Field(alias="startedAt")
    answered_at: str | None = Field(None, alias="answeredAt")
    ended_at: str | None = Field(None, alias="endedAt")
    end_reason: str | None = Field(None, alias="endReason")
    duration_seconds: float | None = Field(None, alias="durationSeconds")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class CreateCallOutput(BaseModel):
    call_id: str = Field(alias="callId")
    state: str
    from_number: str = Field(alias="from")
    to: str
    tier: str
    direction: str

    model_config = {"populate_by_name": True}


class TranscriptSegment(BaseModel):
    speaker: str
    text: str
    start_time: float = Field(alias="startTime")
    end_time: float = Field(alias="endTime")
    confidence: float
    is_final: bool = Field(alias="isFinal")

    model_config = {"populate_by_name": True}


class CallTranscript(BaseModel):
    call_id: str = Field(alias="callId")
    segments: list[TranscriptSegment]

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Extension (headless connect)
# ---------------------------------------------------------------------------


class ConnectExtensionResult(BaseModel):
    agent_id: str = Field(alias="agentId")
    connect_url: str = Field(alias="connectUrl")
    expires_at: str | None = Field(None, alias="expiresAt")
    exchange_expires_at: str = Field(alias="exchangeExpiresAt")
    policy: str

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Provisioning requests
#
# An agent cannot provision its own vault or phone number -- both endpoints are
# master-gated and an agent key never holds master authority. This is how it
# asks its owner instead: the agent files a request, the owner approves in the
# console, and the resource is created. The agent receives the result, never
# the privilege.
#
# Distinct from a credential request, which collects a SECRET the agent must
# never see. This collects a DECISION.
# ---------------------------------------------------------------------------


class ProvisionableResource(str, Enum):
    VAULT = "VAULT"
    PHONE_NUMBER = "PHONE_NUMBER"
    # Appears on RESPONSES and as a list filter, never on create: a GENERIC row
    # records a master-gated procedure an agent actually attempted, and is
    # written only by the server, which knows the real procedure and arguments.
    # The API refuses a create naming it. Without this member, listing raised a
    # ValidationError for any org whose agent had ever hit a master gate.
    GENERIC = "GENERIC"


class ProvisioningRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ProvisioningOptions(BaseModel):
    """Per-resource options. Only PHONE_NUMBER takes any."""

    country_code: str | None = Field(None, alias="countryCode")
    area_code: str | None = Field(None, alias="areaCode")

    model_config = {"populate_by_name": True}


class ProvisioningRequest(BaseModel):
    """A provisioning request and its current state."""

    request_id: str = Field(alias="requestId")
    agent_id: str = Field(alias="agentId")
    # So the owner knows who is asking, not just an opaque id.
    agent_name: str = Field(alias="agentName")
    resource: ProvisionableResource
    reason: str
    # Lazily expired -- a request past its TTL reads as EXPIRED here even
    # though nothing wrote that transition.
    status: ProvisioningRequestStatus
    options: ProvisioningOptions | None = None
    expires_at: str = Field(alias="expiresAt")
    decided_at: str | None = Field(None, alias="decidedAt")
    # The owner's note, typically why it was declined -- surfaced so a second
    # attempt can address the objection instead of repeating the first.
    decided_note: str | None = Field(None, alias="decidedNote")
    # Vault or phone identity id once APPROVED; None otherwise.
    provisioned_id: str | None = Field(None, alias="provisionedId")
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class CreateProvisioningRequestResult(ProvisioningRequest):
    """What creating a request returns.

    ``email_sent`` False does NOT mean the request failed -- it is live and
    visible in the console either way -- but no human was told, so nothing
    will happen until someone looks.
    """

    email_sent: bool = Field(alias="emailSent")

    model_config = {"populate_by_name": True}
