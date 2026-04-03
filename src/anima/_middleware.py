"""Webhook middleware for popular Python web frameworks."""

from __future__ import annotations

from typing import Any, Callable

from ._types import WebhookEvent
from ._webhooks import construct_webhook_event


def fastapi_webhook_dependency(secret: str) -> Callable[..., Any]:
    """Create a FastAPI dependency that verifies webhook signatures.

    Usage::

        from anima import fastapi_webhook_dependency

        webhook_dep = fastapi_webhook_dependency("whsec_...")

        @app.post("/webhooks")
        async def handle(event: WebhookEvent = Depends(webhook_dep)):
            print(event.type, event.data)
    """

    async def dependency(request: Any) -> WebhookEvent:
        # Import here to avoid hard dependency on FastAPI/Starlette
        from starlette.requests import Request as StarletteRequest

        req: StarletteRequest = request
        body = await req.body()
        signature = req.headers.get("anima-signature") or req.headers.get("x-anima-signature")
        if not signature:
            # Import here to avoid hard dependency
            from starlette.exceptions import HTTPException

            raise HTTPException(status_code=400, detail="Missing webhook signature header")

        return construct_webhook_event(body, signature, secret)

    # Annotate for FastAPI's dependency injection
    try:
        from starlette.requests import Request as StarletteRequest

        dependency.__annotations__ = {"request": StarletteRequest, "return": WebhookEvent}
    except ImportError:
        pass

    return dependency
