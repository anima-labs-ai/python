"""Tests for VoicesResource with mocked HTTP."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from anima._types import Voice
from anima.resources.voices import VoicesResource

from .conftest import mock_http  # noqa: F401 – used via fixture name

# ---------------------------------------------------------------------------
# Raw API response fixtures
# ---------------------------------------------------------------------------

VOICE_RAW: dict[str, Any] = {
    "id": "voice_aria",
    "name": "Aria",
    "provider": "elevenlabs",
    "tier": "premium",
    "gender": "female",
    "language": "en-US",
    "accent": "American",
    "style": "conversational",
    "ageRange": "25-35",
    "description": "Natural, warm conversational voice",
    "previewUrl": "https://cdn.example.com/aria.mp3",
}

VOICE_BASIC_RAW: dict[str, Any] = {
    "id": "voice_telnyx_default",
    "name": "Telnyx Default",
    "provider": "telnyx",
    "tier": "basic",
    "language": "en-US",
}

CATALOG_RAW: dict[str, Any] = {
    "voices": [VOICE_RAW, VOICE_BASIC_RAW],
}


class TestVoicesList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CATALOG_RAW
        resource = VoicesResource(mock_http)
        result = resource.list()

        mock_http.request.assert_called_once_with(
            "GET", "/voice/catalog", query=None, options=None
        )
        assert len(result["voices"]) == 2
        assert isinstance(result["voices"][0], Voice)

    def test_list_with_tier_filter(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"voices": [VOICE_RAW]}
        resource = VoicesResource(mock_http)
        resource.list(tier="premium")

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["tier"] == "premium"

    def test_list_with_all_filters(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"voices": [VOICE_RAW]}
        resource = VoicesResource(mock_http)
        resource.list(tier="premium", gender="female", language="en-US")

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["tier"] == "premium"
        assert query["gender"] == "female"
        assert query["language"] == "en-US"

    def test_parses_voice_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CATALOG_RAW
        resource = VoicesResource(mock_http)
        result = resource.list()

        voice = result["voices"][0]
        assert isinstance(voice, Voice)
        assert voice.id == "voice_aria"
        assert voice.name == "Aria"
        assert voice.provider.value == "elevenlabs"
        assert voice.tier.value == "premium"
        assert voice.gender.value == "female"
        assert voice.language == "en-US"
        assert voice.accent == "American"
        assert voice.style == "conversational"
        assert voice.age_range == "25-35"
        assert voice.description == "Natural, warm conversational voice"
        assert voice.preview_url == "https://cdn.example.com/aria.mp3"

    def test_parses_minimal_voice(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"voices": [VOICE_BASIC_RAW]}
        resource = VoicesResource(mock_http)
        result = resource.list()

        voice = result["voices"][0]
        assert isinstance(voice, Voice)
        assert voice.id == "voice_telnyx_default"
        assert voice.tier.value == "basic"
        assert voice.gender is None
        assert voice.accent is None
        assert voice.preview_url is None
