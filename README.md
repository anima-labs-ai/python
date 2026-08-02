# Anima Python SDK

[![PyPI version](https://img.shields.io/pypi/v/anima-labs.svg)](https://pypi.org/project/anima-labs/)
[![Python versions](https://img.shields.io/pypi/pyversions/anima-labs.svg)](https://pypi.org/project/anima-labs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for the [Anima API](https://useanima.sh) -- unified agent identity infrastructure for email, phone, and vault.

## Installation

```bash
pip install anima-labs
```

## Quick start

```python
from anima import Anima

client = Anima(api_key="sk-...")

# Create an agent
agent = client.agents.create(
    org_id="org_123",
    name="Support Bot",
    slug="support-bot",
)

# Send an email
message = client.messages.send_email(
    agent_id=agent.id,
    to=["user@example.com"],
    subject="Hello from Anima",
    body="Your order has been shipped!",
)

print(message.id)
client.close()
```

## Async usage

Every method is available in an async variant via `AsyncAnima`:

```python
import asyncio
from anima import AsyncAnima


async def main():
    async with AsyncAnima(api_key="sk-...") as client:
        agents = await client.agents.list(org_id="org_123")
        for agent in agents.items:
            print(agent.name)


asyncio.run(main())
```

## Resources

Both `Anima` (sync) and `AsyncAnima` have identical resource interfaces. All async methods use `await`.

### `client.agents`

| Method | Description |
|--------|-------------|
| `create(*, org_id, name, slug, email?, provision_phone?, metadata?)` | Create a new agent |
| `get(agent_id)` | Get an agent by ID |
| `list(*, cursor?, limit?, org_id?, status?, query?)` | List agents with pagination |
| `update(agent_id, *, name?, slug?, status?, metadata?)` | Update agent fields |
| `delete(agent_id)` | Delete an agent |
| `rotate_key(agent_id)` | Rotate an agent's API key |

### `client.messages`

| Method | Description |
|--------|-------------|
| `send_email(*, agent_id, to, subject, body, cc?, bcc?, body_html?, attachments?, in_reply_to?, references?, headers?, metadata?)` | Send an email (attachments + threading supported) |
| `send_sms(*, agent_id, to, body, media_urls?, metadata?)` | Send an SMS |
| `get(message_id)` | Get a message by ID |
| `list(*, cursor?, limit?, agent_id?, thread_id?, channel?, direction?, date_from?, date_to?)` | List messages with filters |
| `search(query, *, agent_id?, channel?, direction?, status?, date_from?, date_to?, cursor?, limit?)` | Full-text search messages |
| `semantic_search(query, *, agent_id?, limit?, threshold?)` | Search messages by meaning (vector similarity) |
| `upload_attachment(message_id, *, filename, mime_type, size_bytes)` | Upload an attachment |
| `get_attachment_url(attachment_id)` | Get a download URL for an attachment |

Semantic search ranks messages by meaning, not keywords — results carry a
`similarity` score (0-1):

```python
results = client.messages.semantic_search("unpaid invoices from suppliers", limit=5)
for r in results:
    print(f"{r.similarity:.2f} {r.channel} {r.content[:60]}")
```

Sending with an attachment (dict in the API wire shape — exactly one of `content` (base64) or `url`):

```python
message = client.messages.send_email(
    agent_id=agent.id,
    to=["user@example.com"],
    subject="Your invoice",
    body="Invoice attached.",
    attachments=[
        {"filename": "invoice.pdf", "contentType": "application/pdf", "content": pdf_base64},
    ],
)
```

### `client.inboxes`

| Method | Description |
|--------|-------------|
| `create(*, username?, domain?, display_name?, agent_id?)` | Create an inbox (address generated when omitted) |
| `get(inbox_id)` | Get an inbox by ID |
| `list(*, cursor?, limit?, query?)` | List inboxes with pagination |
| `update(inbox_id, *, display_name?, agent_id?)` | Update inbox fields |
| `delete(inbox_id)` | Delete an inbox |

### `client.emails`

| Method | Description |
|--------|-------------|
| `list(*, cursor?, limit?, agent_id?)` | List emails with pagination |
| `upload_attachment(message_id, *, filename, mime_type, size_bytes)` | Upload an email attachment |
| `get_attachment_url(attachment_id)` | Get a download URL for an attachment |

### `client.emails.drafts`

Composed-but-not-sent emails owned by an agent. Drafts may be incomplete (no
recipients, subject, or body yet); `send` atomically converts a draft into a
delivered message and deletes the draft.

| Method | Description |
|--------|-------------|
| `create(*, agent_id, from_identity_id?, to?, cc?, bcc?, subject?, body?, body_html?, in_reply_to?, references?, metadata?)` | Create a draft (only `agent_id` required) |
| `get(draft_id)` | Get a draft by ID |
| `list(*, cursor?, limit?, agent_id?)` | List drafts with pagination |
| `send(draft_id)` | Send the draft — returns the new `MessageOutput` |
| `delete(draft_id)` | Discard a draft — returns its final state |

```python
draft = client.emails.drafts.create(
    agent_id=agent.id,
    to=["user@example.com"],
    subject="Quarterly report",
    body="Numbers attached below.",
)
message = client.emails.drafts.send(draft.id)  # draft is deleted server-side
```

### `client.phones`

| Method | Description |
|--------|-------------|
| `provision(*, agent_id, country_code?, area_code?, capabilities?)` | Provision a phone number |
| `get(phone_id)` | Get phone details |
| `list(*, cursor?, limit?, agent_id?)` | List phone numbers |
| `release(phone_id)` | Release a phone number |
| `update_config(phone_id, *, is_primary?, ten_dlc_status?, metadata?)` | Update phone configuration |

### `client.voices`

Browse the multilingual voice catalog (English, Spanish, French, German, Italian, Japanese, Dutch, and more). Each voice carries descriptive metadata and a vendor-neutral `sample_url` preview.

| Method | Description |
|--------|-------------|
| `list(*, language?, gender?)` | List catalog voices, optionally filtered by language or gender |

```python
# Only Spanish voices
result = client.voices.list(language="es")
for voice in result["voices"]:
    print(voice.id, voice.name, voice.language, voice.descriptors)
    if voice.sample_url:  # vendor-neutral preview served from the API host
        print("preview:", voice.sample_url)
```

### `client.domains`

| Method | Description |
|--------|-------------|
| `add(*, domain)` | Add a custom domain |
| `get(domain_id)` | Get domain details |
| `list()` | List all domains |
| `delete(domain_id)` | Remove a domain |
| `update(domain_id, *, feedback_enabled?)` | Update domain settings |
| `verify(domain_id)` | Trigger domain verification |
| `dns_records(domain_id)` | Get required DNS records |
| `deliverability(domain_id)` | Get deliverability statistics |
| `zone_file(domain_id)` | Export the domain zone file |

### `client.vault`

| Method | Description |
|--------|-------------|
| `provision(*, agent_id)` | Provision a vault for an agent |
| `deprovision(*, agent_id)` | Deprovision an agent's vault |
| `list_credentials(*, agent_id, type?)` | List stored credentials |
| `get_credential(credential_id)` | Get a credential by ID |
| `create_credential(*, agent_id, type, name, notes?, login?, card?, identity?, fields?, favorite?, generate_password?)` | Store a new credential. `generate_password={...}` has the vault mint the login password server-side — stored, never returned (masked ref only) |
| `update_credential(credential_id, *, name?, notes?, login?, card?, identity?, fields?, favorite?)` | Update a credential |
| `delete_credential(credential_id)` | Delete a credential |
| `search(*, agent_id, search, type?)` | Search credentials |
| `generate_password(*, length?, uppercase?, lowercase?, numbers?, symbols?)` | Generate a secure password |
| `get_totp(credential_id)` | Get a TOTP code |
| `status(agent_id)` | Get vault status |
| `sync(agent_id)` | Force vault sync |

### `client.extension`

| Method | Description |
|--------|-------------|
| `connect(*, agent_id?, ttl?)` | Mint a one-time connect handoff for a headless browser-extension worker. With a master key pass `agent_id`; with an agent key omit it. `ttl` is `"15m"`, `"1h"`, or `"session"`. Returns a `connect_url` (no secret). |

```python
handoff = client.extension.connect(agent_id="agent_123", ttl="15m")
print(handoff.connect_url)  # open in the extension worker to complete the handshake
```

### `client.security`

| Method | Description |
|--------|-------------|
| `get_scanner_status(*, org_id)` | Whether AI scanning is running, and why not if it isn't |
| `list_events(*, org_id, agent_id?, type?, severity?, cursor?, limit?)` | List security events |

Content scanning is not a call you make — it runs inside the send paths, so a
blocked message surfaces as an error from `emails.send` / `messages.send`.

### `client.organizations`

| Method | Description |
|--------|-------------|
| `create(*, name, slug, clerk_org_id?, tier?, settings?)` | Create an organization |
| `get(org_id)` | Get organization details |
| `list(*, cursor?, limit?, query?)` | List organizations |
| `update(org_id, *, name?, slug?, clerk_org_id?, tier?, settings?)` | Update an organization |
| `delete(org_id)` | Delete an organization |
| `rotate_key(org_id)` | Rotate the master API key |

### `client.webhooks`

| Method | Description |
|--------|-------------|
| `create(*, url, events, description?, active?, auth_config?, rate_limit_per_minute?, max_attempts?)` | Register a webhook endpoint |
| `get(webhook_id)` | Get webhook details |
| `list(*, cursor?, limit?)` | List webhooks |
| `update(webhook_id, *, url?, events?, description?, active?, auth_config?, rate_limit_per_minute?, max_attempts?)` | Update a webhook |
| `delete(webhook_id)` | Delete a webhook |
| `test(webhook_id, *, event?)` | Send a test event |
| `list_deliveries(webhook_id, *, cursor?, limit?)` | List delivery attempts |

Configure the auth Anima presents to your endpoint on each delivery (in addition
to the always-on `X-Anima-Signature` HMAC) plus delivery throttling:

```python
from anima import WebhookAuthBearer

webhook = client.webhooks.create(
    url="https://example.com/anima/webhook",
    events=["message.received"],
    # Also: WebhookAuthBasic(username=, password=),
    #       WebhookAuthCustomHeader(header_name=, value=), WebhookAuthNone().
    auth_config=WebhookAuthBearer(token="your-endpoint-token"),
    rate_limit_per_minute=120,  # omit for unlimited
    max_attempts=5,  # 1-10, default 3
)
print(webhook.id, webhook.auth_type)  # -> "wh_..." "BEARER"
```

The credential you set (token / password / header value) is **write-only** — it
is never returned by `get` or `list`. To remove auth on update, pass
`WebhookAuthNone()`.

## Webhook verification

Verify incoming webhook signatures to ensure authenticity:

```python
from anima import Anima, AnimaError

payload = request.body  # raw request body (str or bytes)
sig = request.headers["anima-signature"]
secret = "whsec_..."

# Option 1: verify only
is_valid = Anima.verify_webhook_signature(payload, sig, secret)

# Option 2: verify and parse in one step
try:
    event = Anima.construct_webhook_event(payload, sig, secret)
    print(event.type, event.data)
except AnimaError:
    print("Invalid signature")
```

## Error handling

All API errors raise typed exceptions that subclass `AnimaError`:

```python
from anima import Anima, AuthenticationError, NotFoundError, RateLimitError, APIError

client = Anima(api_key="sk-...")

try:
    agent = client.agents.get("nonexistent")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Agent not found")
except RateLimitError:
    print("Rate limited -- back off and retry")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | *required* | Your Anima API key (`sk-...`) |
| `base_url` | `https://api.useanima.sh` | API base URL |
| `timeout` | `30.0` | Request timeout in seconds |
| `max_retries` | `3` | Max automatic retries on transient errors |

```python
client = Anima(
    api_key="sk-...",
    base_url="https://api.useanima.sh",  # custom endpoint
    timeout=60.0,
    max_retries=5,
)
```

## Requirements

- Python 3.9+
- [`httpx`](https://www.python-httpx.org/) >= 0.27
- [`pydantic`](https://docs.pydantic.dev/) >= 2.0

## Documentation

Full API documentation is available at [docs.useanima.sh](https://docs.useanima.sh).

## Community

Join the [Anima Discord](https://discord.gg/pY3GK59Z9E) to ask questions in `#python-sdk`, share what you're building in `#showcase`, and stay up to date with releases in `#announcements`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
