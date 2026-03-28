"""Sync and async real-time event streaming over WebSocket."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from types import TracebackType
from typing import Any, Callable

from .._http import AsyncHTTPClient, HTTPClient
from .._types import AnimaEvent

logger = logging.getLogger("anima.events")

_PING_INTERVAL_S = 30.0
_INITIAL_RECONNECT_DELAY_S = 1.0
_MAX_RECONNECT_DELAY_S = 30.0
_RECONNECT_BACKOFF_FACTOR = 2.0

EventCallback = Callable[[AnimaEvent], None]
ErrorCallback = Callable[[Exception], None]
VoidCallback = Callable[[], None]


def _build_ws_url(base_url: str, api_key: str) -> str:
    """Convert an HTTP base URL to a WebSocket URL for the events endpoint."""
    ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
    ws_url = ws_url.rstrip("/")
    return f"{ws_url}/ws/events?token={api_key}"


class EventStream:
    """Synchronous real-time event stream backed by a background thread.

    Supports subscribing to channel patterns, automatic reconnection with
    exponential backoff, and ping/pong keepalive.

    Usage::

        stream = client.events.connect(channels=["email.*"])
        stream.on_event(lambda e: print(e))
        # ... later
        stream.close()

    Or as a context manager::

        with client.events.connect(channels=["email.*"]) as stream:
            stream.on_event(lambda e: print(e))
            time.sleep(60)
    """

    def __init__(self, ws_url: str, channels: list[str] | None = None) -> None:
        self._ws_url = ws_url
        self._initial_channels = list(channels or [])
        self._subscribed_channels: set[str] = set(self._initial_channels)
        self._last_event_id: str | None = None

        self._event_callbacks: list[EventCallback] = []
        self._error_callbacks: list[ErrorCallback] = []
        self._connected_callbacks: list[VoidCallback] = []
        self._disconnected_callbacks: list[VoidCallback] = []

        self._closed = False
        self._reconnect_delay = _INITIAL_RECONNECT_DELAY_S

        self._ws: Any = None  # websocket.WebSocketApp
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        self._connect()

    # -- Public API ----------------------------------------------------------

    def on_event(self, callback: EventCallback) -> EventStream:
        """Register a callback for incoming events."""
        self._event_callbacks.append(callback)
        return self

    def on_error(self, callback: ErrorCallback) -> EventStream:
        """Register a callback for errors."""
        self._error_callbacks.append(callback)
        return self

    def on_connected(self, callback: VoidCallback) -> EventStream:
        """Register a callback for connection establishment."""
        self._connected_callbacks.append(callback)
        return self

    def on_disconnected(self, callback: VoidCallback) -> EventStream:
        """Register a callback for disconnection."""
        self._disconnected_callbacks.append(callback)
        return self

    def subscribe(self, channels: list[str]) -> None:
        """Subscribe to additional channels."""
        with self._lock:
            for ch in channels:
                self._subscribed_channels.add(ch)
        self._send_subscribe(channels)

    def unsubscribe(self, channels: list[str]) -> None:
        """Unsubscribe from channels."""
        with self._lock:
            for ch in channels:
                self._subscribed_channels.discard(ch)
        self._send({"type": "unsubscribe", "channels": channels})

    def close(self) -> None:
        """Close the connection and stop reconnecting."""
        self._closed = True
        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:
                pass
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5)

    def __enter__(self) -> EventStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    # -- Internal ------------------------------------------------------------

    def _connect(self) -> None:
        if self._closed:
            return

        try:
            import websocket  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "The 'websocket-client' package is required for event streaming. "
                "Install it with: pip install 'anima-labs[events]' or pip install websocket-client"
            ) from exc

        ws = websocket.WebSocketApp(
            self._ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_ws_error,
            on_close=self._on_close,
        )
        self._ws = ws

        thread = threading.Thread(
            target=ws.run_forever,
            kwargs={"ping_interval": _PING_INTERVAL_S},
            daemon=True,
        )
        thread.start()
        self._thread = thread

    def _on_open(self, ws: Any) -> None:
        self._reconnect_delay = _INITIAL_RECONNECT_DELAY_S
        with self._lock:
            channels = list(self._subscribed_channels)
        if channels:
            self._send_subscribe(channels)
        for cb in self._connected_callbacks:
            try:
                cb()
            except Exception:
                logger.exception("Error in connected callback")

    def _on_message(self, ws: Any, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return

        msg_type = msg.get("type")
        if msg_type == "event":
            event = AnimaEvent(
                id=msg["id"],
                event_type=msg["eventType"],
                agent_id=msg.get("agentId"),
                org_id=msg["orgId"],
                timestamp=msg["timestamp"],
                data=msg.get("data", {}),
            )
            self._last_event_id = event.id
            for cb in self._event_callbacks:
                try:
                    cb(event)
                except Exception:
                    logger.exception("Error in event callback")
        elif msg_type == "error":
            err = Exception(f"[{msg.get('code')}] {msg.get('message')}")
            for cb in self._error_callbacks:
                try:
                    cb(err)
                except Exception:
                    logger.exception("Error in error callback")

    def _on_ws_error(self, ws: Any, error: Exception) -> None:
        for cb in self._error_callbacks:
            try:
                cb(error)
            except Exception:
                logger.exception("Error in error callback")

    def _on_close(self, ws: Any, close_status_code: int | None, close_msg: str | None) -> None:
        for cb in self._disconnected_callbacks:
            try:
                cb()
            except Exception:
                logger.exception("Error in disconnected callback")
        self._schedule_reconnect()

    def _schedule_reconnect(self) -> None:
        if self._closed:
            return
        delay = self._reconnect_delay
        self._reconnect_delay = min(
            self._reconnect_delay * _RECONNECT_BACKOFF_FACTOR,
            _MAX_RECONNECT_DELAY_S,
        )
        timer = threading.Timer(delay, self._connect)
        timer.daemon = True
        timer.start()

    def _send_subscribe(self, channels: list[str]) -> None:
        msg: dict[str, Any] = {"type": "subscribe", "channels": channels}
        if self._last_event_id is not None:
            msg["lastEventId"] = self._last_event_id
        self._send(msg)

    def _send(self, data: dict[str, Any]) -> None:
        try:
            if self._ws is not None:
                self._ws.send(json.dumps(data))
        except Exception:
            pass


class AsyncEventStream:
    """Asynchronous real-time event stream using the ``websockets`` library.

    Supports subscribing to channel patterns, automatic reconnection with
    exponential backoff, and ping/pong keepalive.

    Usage::

        stream = await client.events.connect(channels=["email.*"])
        stream.on_event(lambda e: print(e))
        # ... later
        await stream.close()

    Or as an async context manager::

        async with await client.events.connect(channels=["email.*"]) as stream:
            stream.on_event(lambda e: print(e))
            await asyncio.sleep(60)
    """

    def __init__(self, ws_url: str, channels: list[str] | None = None) -> None:
        self._ws_url = ws_url
        self._initial_channels = list(channels or [])
        self._subscribed_channels: set[str] = set(self._initial_channels)
        self._last_event_id: str | None = None

        self._event_callbacks: list[EventCallback] = []
        self._error_callbacks: list[ErrorCallback] = []
        self._connected_callbacks: list[VoidCallback] = []
        self._disconnected_callbacks: list[VoidCallback] = []

        self._closed = False
        self._reconnect_delay = _INITIAL_RECONNECT_DELAY_S
        self._ws: Any = None
        self._listen_task: asyncio.Task[None] | None = None
        self._ping_task: asyncio.Task[None] | None = None

    async def start(self) -> AsyncEventStream:
        """Open the connection. Called automatically by ``AsyncEventsResource.connect``."""
        await self._connect()
        return self

    # -- Public API ----------------------------------------------------------

    def on_event(self, callback: EventCallback) -> AsyncEventStream:
        """Register a callback for incoming events."""
        self._event_callbacks.append(callback)
        return self

    def on_error(self, callback: ErrorCallback) -> AsyncEventStream:
        """Register a callback for errors."""
        self._error_callbacks.append(callback)
        return self

    def on_connected(self, callback: VoidCallback) -> AsyncEventStream:
        """Register a callback for connection establishment."""
        self._connected_callbacks.append(callback)
        return self

    def on_disconnected(self, callback: VoidCallback) -> AsyncEventStream:
        """Register a callback for disconnection."""
        self._disconnected_callbacks.append(callback)
        return self

    async def subscribe(self, channels: list[str]) -> None:
        """Subscribe to additional channels."""
        for ch in channels:
            self._subscribed_channels.add(ch)
        await self._send_subscribe(channels)

    async def unsubscribe(self, channels: list[str]) -> None:
        """Unsubscribe from channels."""
        for ch in channels:
            self._subscribed_channels.discard(ch)
        await self._send({"type": "unsubscribe", "channels": channels})

    async def close(self) -> None:
        """Close the connection and stop reconnecting."""
        self._closed = True
        if self._ping_task is not None:
            self._ping_task.cancel()
            self._ping_task = None
        if self._listen_task is not None:
            self._listen_task.cancel()
            self._listen_task = None
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

    async def __aenter__(self) -> AsyncEventStream:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    # -- Internal ------------------------------------------------------------

    async def _connect(self) -> None:
        if self._closed:
            return

        try:
            import websockets  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "The 'websockets' package is required for async event streaming. "
                "Install it with: pip install 'anima-labs[events]' or pip install websockets"
            ) from exc

        try:
            self._ws = await websockets.connect(self._ws_url)
            self._reconnect_delay = _INITIAL_RECONNECT_DELAY_S

            # Subscribe to all channels
            channels = list(self._subscribed_channels)
            if channels:
                await self._send_subscribe(channels)

            for cb in self._connected_callbacks:
                try:
                    cb()
                except Exception:
                    logger.exception("Error in connected callback")

            # Start background tasks
            self._listen_task = asyncio.ensure_future(self._listen_loop())
            self._ping_task = asyncio.ensure_future(self._ping_loop())

        except Exception as exc:
            for cb in self._error_callbacks:
                try:
                    cb(exc)
                except Exception:
                    logger.exception("Error in error callback")
            await self._schedule_reconnect()

    async def _listen_loop(self) -> None:
        try:
            async for raw in self._ws:
                try:
                    msg = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue

                msg_type = msg.get("type")
                if msg_type == "event":
                    event = AnimaEvent(
                        id=msg["id"],
                        event_type=msg["eventType"],
                        agent_id=msg.get("agentId"),
                        org_id=msg["orgId"],
                        timestamp=msg["timestamp"],
                        data=msg.get("data", {}),
                    )
                    self._last_event_id = event.id
                    for cb in self._event_callbacks:
                        try:
                            cb(event)
                        except Exception:
                            logger.exception("Error in event callback")
                elif msg_type == "error":
                    err = Exception(f"[{msg.get('code')}] {msg.get('message')}")
                    for cb in self._error_callbacks:
                        try:
                            cb(err)
                        except Exception:
                            logger.exception("Error in error callback")
        except asyncio.CancelledError:
            return
        except Exception:
            pass

        # Connection dropped
        for cb in self._disconnected_callbacks:
            try:
                cb()
            except Exception:
                logger.exception("Error in disconnected callback")
        await self._schedule_reconnect()

    async def _ping_loop(self) -> None:
        try:
            while not self._closed:
                await asyncio.sleep(_PING_INTERVAL_S)
                await self._send({"type": "ping"})
        except asyncio.CancelledError:
            return
        except Exception:
            pass

    async def _schedule_reconnect(self) -> None:
        if self._closed:
            return
        delay = self._reconnect_delay
        self._reconnect_delay = min(
            self._reconnect_delay * _RECONNECT_BACKOFF_FACTOR,
            _MAX_RECONNECT_DELAY_S,
        )
        await asyncio.sleep(delay)
        await self._connect()

    async def _send_subscribe(self, channels: list[str]) -> None:
        msg: dict[str, Any] = {"type": "subscribe", "channels": channels}
        if self._last_event_id is not None:
            msg["lastEventId"] = self._last_event_id
        await self._send(msg)

    async def _send(self, data: dict[str, Any]) -> None:
        try:
            if self._ws is not None:
                await self._ws.send(json.dumps(data))
        except Exception:
            pass


class EventsResource:
    """Synchronous resource for real-time event streaming."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def connect(self, *, channels: list[str] | None = None) -> EventStream:
        """Open a real-time event stream.

        Args:
            channels: Optional list of channel patterns to subscribe to on connect.

        Returns:
            An ``EventStream`` instance.
        """
        ws_url = _build_ws_url(self._client._base_url, self._client._api_key)
        return EventStream(ws_url, channels)


class AsyncEventsResource:
    """Asynchronous resource for real-time event streaming."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def connect(self, *, channels: list[str] | None = None) -> AsyncEventStream:
        """Open a real-time event stream.

        Args:
            channels: Optional list of channel patterns to subscribe to on connect.

        Returns:
            An ``AsyncEventStream`` instance.
        """
        ws_url = _build_ws_url(self._client._base_url, self._client._api_key)
        stream = AsyncEventStream(ws_url, channels)
        await stream.start()
        return stream
