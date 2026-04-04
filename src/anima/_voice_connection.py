"""Bidirectional WebSocket connection for real-time voice call control."""

from __future__ import annotations

import json
import threading
from typing import Any, Callable

try:
    import websocket as _ws  # websocket-client

    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False


class VoiceConnection:
    """Real-time voice call control over WebSocket.

    Send commands (call.create, call.speak, call.hangup) and receive events
    (call.started, call.transcription, call.ended).

    Usage::

        conn = anima.calls.connect()
        conn.on_message(lambda msg: print(msg["type"], msg.get("data")))
        conn.create_call("+15551234567")
        # ... handle events ...
        conn.close()
    """

    def __init__(self, ws_url: str) -> None:
        if not HAS_WEBSOCKET:
            raise ImportError(
                "websocket-client is required for voice connections. "
                "Install it with: pip install websocket-client"
            )
        self._ws_url = ws_url
        self._ws: Any = None
        self._thread: threading.Thread | None = None
        self._closed = False
        self._message_handlers: list[Callable[[dict[str, Any]], None]] = []
        self._error_handlers: list[Callable[[Exception], None]] = []
        self._connected_handlers: list[Callable[[], None]] = []
        self._disconnected_handlers: list[Callable[[], None]] = []
        self._connect()

    def on_message(self, handler: Callable[[dict[str, Any]], None]) -> VoiceConnection:
        self._message_handlers.append(handler)
        return self

    def on_error(self, handler: Callable[[Exception], None]) -> VoiceConnection:
        self._error_handlers.append(handler)
        return self

    def on_connected(self, handler: Callable[[], None]) -> VoiceConnection:
        self._connected_handlers.append(handler)
        return self

    def on_disconnected(self, handler: Callable[[], None]) -> VoiceConnection:
        self._disconnected_handlers.append(handler)
        return self

    def send(self, msg_type: str, data: dict[str, Any] | None = None) -> None:
        """Send a raw message to the voice WebSocket."""
        if self._ws:
            payload: dict[str, Any] = {"type": msg_type}
            if data:
                payload["data"] = data
            self._ws.send(json.dumps(payload))

    def create_call(
        self,
        to: str,
        *,
        tier: str | None = None,
        greeting: str | None = None,
        from_number: str | None = None,
    ) -> None:
        """Create an outbound call."""
        data: dict[str, Any] = {"to": to}
        if tier:
            data["tier"] = tier
        if greeting:
            data["greeting"] = greeting
        if from_number:
            data["fromNumber"] = from_number
        self.send("call.create", data)

    def speak(self, call_id: str, text: str) -> None:
        """Send text for TTS playback."""
        self.send("call.speak", {"callId": call_id, "text": text})

    def cancel_speak(self, call_id: str) -> None:
        """Cancel in-progress speech."""
        self.send("call.speak.cancel", {"callId": call_id})

    def hangup(self, call_id: str) -> None:
        """Hang up a call."""
        self.send("call.hangup", {"callId": call_id})

    def accept(self, call_id: str) -> None:
        """Accept an inbound call."""
        self.send("call.accept", {"callId": call_id})

    def reject(self, call_id: str) -> None:
        """Reject an inbound call."""
        self.send("call.reject", {"callId": call_id})

    def hold(self, call_id: str) -> None:
        """Place a call on hold."""
        self.send("call.hold", {"callId": call_id})

    def resume(self, call_id: str) -> None:
        """Resume a held call."""
        self.send("call.resume", {"callId": call_id})

    def dtmf(self, call_id: str, digits: str) -> None:
        """Send DTMF tone(s)."""
        self.send("call.dtmf", {"callId": call_id, "digits": digits})

    def close(self) -> None:
        """Close the connection."""
        self._closed = True
        if self._ws:
            self._ws.close()
            self._ws = None

    def _connect(self) -> None:
        if self._closed:
            return

        ws_app = _ws.WebSocketApp(
            self._ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws = ws_app
        self._thread = threading.Thread(target=ws_app.run_forever, daemon=True)
        self._thread.start()

    def _on_open(self, ws: Any) -> None:
        for handler in self._connected_handlers:
            handler()

    def _on_message(self, ws: Any, raw: str) -> None:
        try:
            msg = json.loads(raw)
            for handler in self._message_handlers:
                handler(msg)
        except (json.JSONDecodeError, TypeError):
            pass

    def _on_error(self, ws: Any, error: Exception) -> None:
        for handler in self._error_handlers:
            handler(error)

    def _on_close(self, ws: Any, close_status_code: Any = None, close_msg: Any = None) -> None:
        for handler in self._disconnected_handlers:
            handler()
