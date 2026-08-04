"""The query string must carry an Enum's value, not its repr.

Every enum in this SDK subclasses ``str``, so handing one to a parameter
annotated ``str`` type-checks cleanly. In a JSON body that is harmless --
``json.dumps`` serialises a ``(str, Enum)`` to its value. In a query string it
is not: httpx calls ``str()`` on each param, and ``str(SecuritySeverity.HIGH)``
is ``"SecuritySeverity.HIGH"``.

So this passed mypy and sent ``?severity=SecuritySeverity.HIGH``:

    client.security.list_events(org_id=..., severity=SecuritySeverity.HIGH)

Unwrapping happens in ``_http._encode_query`` rather than at each call site, so
a new resource method cannot reintroduce it -- there were ~30 query assignments
and only the compliance ones unwrapped.
"""

from __future__ import annotations

import httpx
import pytest

from anima._http import _encode_query, unwrap_enum
from anima._types import ComplianceFramework, SecuritySeverity, Tier


class TestEncodeQuery:
    def test_unwraps_an_enum_to_its_value(self) -> None:
        assert _encode_query({"severity": SecuritySeverity.HIGH}) == {"severity": "HIGH"}

    def test_leaves_plain_strings_alone(self) -> None:
        assert _encode_query({"cursor": "cur_abc"}) == {"cursor": "cur_abc"}

    def test_unwraps_inside_a_list(self) -> None:
        """List values become repeated keys; each element needs unwrapping too."""
        assert _encode_query({"framework": [ComplianceFramework.SOC2, "GDPR"]}) == {
            "framework": ["SOC2", "GDPR"]
        }

    def test_none_passes_through(self) -> None:
        assert _encode_query(None) is None

    def test_numbers_are_stringified(self) -> None:
        assert _encode_query({"limit": 20}) == {"limit": "20"}


class TestAgainstHttpx:
    """The behaviour that motivates the whole thing, pinned against real httpx."""

    def test_raw_enum_would_serialise_wrongly(self) -> None:
        request = httpx.Request(
            "GET", "https://x.test/e", params={"severity": SecuritySeverity.HIGH}
        )
        # This is the bug: httpx stringifies the member, not its value.
        assert "severity=SecuritySeverity.HIGH" in str(request.url)

    def test_encoded_enum_serialises_correctly(self) -> None:
        request = httpx.Request(
            "GET",
            "https://x.test/e",
            params=_encode_query({"severity": SecuritySeverity.HIGH}),
        )
        assert "severity=HIGH" in str(request.url)


class TestUnwrapEnum:
    """Body serialisation shares the helper but must not stringify."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (Tier.STARTER, "STARTER"),
            ("STARTER", "STARTER"),
            (42, 42),
            (None, None),
            ({"a": 1}, {"a": 1}),
        ],
    )
    def test_passes_non_enums_through_untouched(self, value: object, expected: object) -> None:
        assert unwrap_enum(value) == expected
