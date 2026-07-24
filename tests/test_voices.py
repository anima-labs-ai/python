"""Tests for VoicesResource with mocked HTTP."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from anima._types import Voice
from anima.resources.voices import VoicesResource

# ---------------------------------------------------------------------------
# Raw API response fixtures (vendor-neutral, multilingual catalog)
# ---------------------------------------------------------------------------

VOICE_RAW: dict[str, Any] = {
    "id": "celeste",
    "name": "Celeste",
    "gender": "female",
    "accent": "Castilian",
    "age": "adult",
    "descriptors": ["warm", "smooth"],
    "useCases": ["support", "sales"],
    "language": "es",
    "sampleUrl": "https://api.useanima.sh/v1/voice/catalog/celeste/sample",
}

VOICE_BASIC_RAW: dict[str, Any] = {
    "id": "thalia",
    "name": "Thalia",
    "gender": "neutral",
    "descriptors": [],
    "useCases": [],
    "language": "en",
}

CATALOG_RAW: dict[str, Any] = {
    "voices": [VOICE_RAW, VOICE_BASIC_RAW],
}


class TestVoicesList:
    def test_list_no_params(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CATALOG_RAW
        resource = VoicesResource(mock_http)
        result = resource.list()

        mock_http.request.assert_called_once_with("GET", "/voice/catalog", query=None, options=None)
        assert len(result["voices"]) == 2
        assert isinstance(result["voices"][0], Voice)

    def test_list_with_language_filter(self, mock_http: MagicMock) -> None:
        # Multilingual catalog: language is the primary filter axis.
        mock_http.request.return_value = {"voices": [VOICE_RAW]}
        resource = VoicesResource(mock_http)
        resource.list(language="es")

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["language"] == "es"

    def test_list_with_all_filters(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"voices": [VOICE_RAW]}
        resource = VoicesResource(mock_http)
        resource.list(gender="female", language="en")

        _, kwargs = mock_http.request.call_args
        query = kwargs["query"]
        assert query["gender"] == "female"
        assert query["language"] == "en"

    def test_parses_voice_fields(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = CATALOG_RAW
        resource = VoicesResource(mock_http)
        result = resource.list()

        voice = result["voices"][0]
        assert isinstance(voice, Voice)
        assert voice.id == "celeste"
        assert voice.name == "Celeste"
        assert voice.gender.value == "female"
        assert voice.language == "es"
        assert voice.accent == "Castilian"
        assert voice.age == "adult"
        assert voice.descriptors == ["warm", "smooth"]
        assert voice.use_cases == ["support", "sales"]
        assert voice.sample_url == "https://api.useanima.sh/v1/voice/catalog/celeste/sample"

    def test_parses_minimal_voice(self, mock_http: MagicMock) -> None:
        mock_http.request.return_value = {"voices": [VOICE_BASIC_RAW]}
        resource = VoicesResource(mock_http)
        result = resource.list()

        voice = result["voices"][0]
        assert isinstance(voice, Voice)
        assert voice.id == "thalia"
        assert voice.gender.value == "neutral"
        assert voice.accent is None
        assert voice.age is None
        assert voice.sample_url is None
        assert voice.descriptors == []
        assert voice.use_cases == []
