"""Pydantic v2 models and enums matching the Node SDK types.ts."""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, Literal, TypeVar, Union

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Tier(str, Enum):
    FREE = "FREE"
    DEVELOPER = "DEVELOPER"
    GROWTH = "GROWTH"
    SCALE = "SCALE"
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
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class AttachmentDownloadOutput(BaseModel):
    url: str
    expires_at: str = Field(alias="expiresAt")

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
    status: str
    credential_count: int = Field(alias="credentialCount")
    last_sync_at: str | None = Field(None, alias="lastSyncAt")
    created_at: str = Field(alias="createdAt")

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


class SecurityScanWarning(BaseModel):
    rule_id: str = Field(alias="ruleId")
    severity: SecuritySeverity
    description: str
    match: str | None = None

    model_config = {"populate_by_name": True}


class SecurityScanOutput(BaseModel):
    blocked: bool
    warnings: list[SecurityScanWarning]
    summary: str


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


class VerifiableCredential(BaseModel):
    id: str
    type: str
    issuer: str
    subject: str
    issuance_date: str = Field(alias="issuanceDate")
    expiration_date: str | None = Field(None, alias="expirationDate")
    credential_subject: dict[str, Any] = Field(alias="credentialSubject")
    proof: dict[str, Any]

    model_config = {"populate_by_name": True}


class VerifyCredentialOutput(BaseModel):
    valid: bool
    credential: VerifiableCredential | None = None
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
# Wallet
# ---------------------------------------------------------------------------


class WalletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"


class WalletOutput(BaseModel):
    id: str
    agent_id: str = Field(alias="agentId")
    address: str
    currency: str
    balance: float
    status: WalletStatus
    spend_limit_daily: float | None = Field(None, alias="spendLimitDaily")
    spend_limit_monthly: float | None = Field(None, alias="spendLimitMonthly")
    metadata: dict[str, Any]
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class WalletPayOutput(BaseModel):
    transaction_id: str = Field(alias="transactionId")
    from_: str = Field(alias="from")
    to: str
    amount: float
    currency: str
    status: str
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class X402FetchOutput(BaseModel):
    status: int
    headers: dict[str, str]
    body: str
    payment_amount: float | None = Field(None, alias="paymentAmount")
    transaction_id: str | None = Field(None, alias="transactionId")

    model_config = {"populate_by_name": True}


class WalletTransactionOutput(BaseModel):
    id: str
    wallet_id: str = Field(alias="walletId")
    type: str
    amount: float
    currency: str
    from_: str | None = Field(None, alias="from")
    to: str | None = None
    memo: str | None = None
    status: str
    metadata: dict[str, Any] | None = None
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Pods
# ---------------------------------------------------------------------------


class PodStatus(str, Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    CREATING = "CREATING"
    ERROR = "ERROR"


class PodResourceSpec(BaseModel):
    cpu: str | None = None
    memory: str | None = None
    storage: str | None = None


class PodOutput(BaseModel):
    id: str
    agent_id: str = Field(alias="agentId")
    name: str
    image: str
    status: PodStatus
    resources: PodResourceSpec
    env: dict[str, str]
    metadata: dict[str, Any]
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class PodUsageOutput(BaseModel):
    pod_id: str = Field(alias="podId")
    cpu_usage: float = Field(alias="cpuUsage")
    memory_usage: float = Field(alias="memoryUsage")
    storage_usage: float = Field(alias="storageUsage")
    network_in: float = Field(alias="networkIn")
    network_out: float = Field(alias="networkOut")
    uptime_seconds: int = Field(alias="uptimeSeconds")
    measured_at: str = Field(alias="measuredAt")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# A2A (Agent-to-Agent Protocol)
# ---------------------------------------------------------------------------


class A2ATaskStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    WORKING = "WORKING"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"


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
    API_KEY = "api_key"
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"


class AuditResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


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


class ComplianceControlStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    FAILED = "failed"


class DsarStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ComplianceControlOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    framework: ComplianceFramework
    control_id: str = Field(alias="controlId")
    title: str
    description: str
    category: str
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
    type: str
    status: str
    title: str
    summary: str | None = None
    data: dict[str, Any] | None = None
    generated_at: str = Field(alias="generatedAt")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class ComplianceReportDownloadOutput(BaseModel):
    url: str
    format: str
    expires_at: str = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class ComplianceFrameworkSummary(BaseModel):
    total_controls: int = Field(alias="totalControls")
    implemented: int
    verified: int
    failed: int
    not_started: int = Field(alias="notStarted")
    score: float

    model_config = {"populate_by_name": True}


class ComplianceDashboardOutput(BaseModel):
    org_id: str = Field(alias="orgId")
    frameworks: dict[str, ComplianceFrameworkSummary]
    overall_score: float = Field(alias="overallScore")
    recent_activity: list[ComplianceReportOutput] = Field(alias="recentActivity")

    model_config = {"populate_by_name": True}


class DsarOutput(BaseModel):
    id: str
    org_id: str = Field(alias="orgId")
    subject_email: str = Field(alias="subjectEmail")
    request_type: str = Field(alias="requestType")
    status: DsarStatus
    description: str | None = None
    metadata: dict[str, Any] | None = None
    completed_at: str | None = Field(None, alias="completedAt")
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


class VoiceProvider(str, Enum):
    TELNYX = "telnyx"
    ELEVENLABS = "elevenlabs"
    AWS_POLLY = "aws-polly"


class CallDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class Voice(BaseModel):
    id: str
    name: str
    provider: VoiceProvider
    tier: VoiceTier
    gender: VoiceGender | None = None
    language: str
    accent: str | None = None
    style: str | None = None
    age_range: str | None = Field(None, alias="ageRange")
    description: str | None = None
    preview_url: str | None = Field(None, alias="previewUrl")

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
