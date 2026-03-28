# Anima Python SDK

[![PyPI version](https://img.shields.io/pypi/v/anima-labs.svg)](https://pypi.org/project/anima-labs/)
[![Python versions](https://img.shields.io/pypi/pyversions/anima-labs.svg)](https://pypi.org/project/anima-labs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for the [Anima API](https://anima.email) -- unified agent identity infrastructure for email, phone, cards, and vault.

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
| `send_email(*, agent_id, to, subject, body, cc?, bcc?, body_html?, headers?, metadata?)` | Send an email |
| `send_sms(*, agent_id, to, body, media_urls?, metadata?)` | Send an SMS |
| `get(message_id)` | Get a message by ID |
| `list(*, cursor?, limit?, agent_id?, thread_id?, channel?, direction?, date_from?, date_to?)` | List messages with filters |
| `search(query, *, agent_id?, channel?, direction?, status?, date_from?, date_to?, cursor?, limit?)` | Full-text search messages |
| `upload_attachment(message_id, *, filename, mime_type, size_bytes)` | Upload an attachment |
| `get_attachment_url(attachment_id)` | Get a download URL for an attachment |

### `client.emails`

| Method | Description |
|--------|-------------|
| `list(*, cursor?, limit?, agent_id?)` | List emails with pagination |
| `upload_attachment(message_id, *, filename, mime_type, size_bytes)` | Upload an email attachment |
| `get_attachment_url(attachment_id)` | Get a download URL for an attachment |

### `client.phones`

| Method | Description |
|--------|-------------|
| `provision(*, agent_id, country_code?, area_code?, capabilities?)` | Provision a phone number |
| `get(phone_id)` | Get phone details |
| `list(*, cursor?, limit?, agent_id?)` | List phone numbers |
| `release(phone_id)` | Release a phone number |
| `update_config(phone_id, *, is_primary?, ten_dlc_status?, metadata?)` | Update phone configuration |

### `client.cards`

| Method | Description |
|--------|-------------|
| `create(*, agent_id, card_type?, currency?, label?, spend_limit_daily?, spend_limit_monthly?, spend_limit_per_auth?)` | Create a virtual card |
| `get(card_id)` | Get card details |
| `list(*, agent_id?, status?, cursor?, limit?)` | List cards |
| `update(card_id, *, label?, spend_limit_daily?, spend_limit_monthly?, spend_limit_per_auth?)` | Update card settings |
| `delete(card_id)` | Delete a card |
| `freeze(card_id)` | Freeze a card |
| `unfreeze(card_id)` | Unfreeze a card |
| `create_policy(card_id, *, name, priority, action, ...)` | Create a spending policy |
| `list_policies(card_id)` | List spending policies |
| `update_policy(policy_id, *, name?, priority?, action?, ...)` | Update a spending policy |
| `delete_policy(policy_id)` | Delete a spending policy |
| `list_transactions(*, card_id?, status?, cursor?, limit?)` | List card transactions |
| `get_transaction(transaction_id)` | Get a transaction by ID |
| `kill_switch(*, agent_id?, active)` | Activate or deactivate the kill switch |
| `list_approvals(*, card_id?, status?, cursor?, limit?)` | List pending approvals |
| `decide_approval(approval_id, decision)` | Approve or decline a transaction |

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
| `create_credential(*, agent_id, type, name, notes?, login?, card?, identity?, fields?, favorite?)` | Store a new credential |
| `update_credential(credential_id, *, name?, notes?, login?, card?, identity?, fields?, favorite?)` | Update a credential |
| `delete_credential(credential_id)` | Delete a credential |
| `search(*, agent_id, search, type?)` | Search credentials |
| `generate_password(*, length?, uppercase?, lowercase?, numbers?, symbols?)` | Generate a secure password |
| `get_totp(credential_id)` | Get a TOTP code |
| `status(agent_id)` | Get vault status |
| `sync(agent_id)` | Force vault sync |

### `client.security`

| Method | Description |
|--------|-------------|
| `scan_content(*, org_id, channel, body, agent_id?, subject?, metadata?)` | Scan content for threats |
| `list_events(*, org_id, agent_id?, type?, severity?, cursor?, limit?)` | List security events |

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
| `create(*, url, events, description?, active?)` | Register a webhook endpoint |
| `get(webhook_id)` | Get webhook details |
| `list(*, cursor?, limit?)` | List webhooks |
| `update(webhook_id, *, url?, events?, description?, active?)` | Update a webhook |
| `delete(webhook_id)` | Delete a webhook |
| `test(webhook_id, *, event?)` | Send a test event |
| `list_deliveries(webhook_id, *, cursor?, limit?)` | List delivery attempts |

## Webhook verification

Verify incoming webhook signatures to ensure authenticity:

```python
from anima import Anima, AnimaError

payload = request.body          # raw request body (str or bytes)
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
| `base_url` | `https://api.anima.com` | API base URL |
| `timeout` | `30.0` | Request timeout in seconds |
| `max_retries` | `3` | Max automatic retries on transient errors |

```python
client = Anima(
    api_key="sk-...",
    base_url="https://api.anima.email",  # custom endpoint
    timeout=60.0,
    max_retries=5,
)
```

## Requirements

- Python 3.9+
- [`httpx`](https://www.python-httpx.org/) >= 0.27
- [`pydantic`](https://docs.pydantic.dev/) >= 2.0

## Documentation

Full API documentation is available at [docs.anima.email](https://docs.anima.email).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
