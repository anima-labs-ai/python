"""This SDK unwraps single-key response envelopes; the JS SDK does not.

``list_credentials()`` returns a ``list`` here and resolves to ``{ items }`` in
``@anima-labs/sdk``; ``generate_password()`` returns a ``str`` here and
``{ password }`` there. Both SDKs are internally consistent and inconsistent
with each other, which is documented in the README's "Response shapes" section.

That difference has already cost something. The toolkit packages were written
by translating call sites between the two languages and read ``.value`` off
``generate_password()`` in both — wrong in each, for opposite reasons
(anima-labs-ai/toolkit#5).

A README cannot fail. These guards can: if a method quietly starts returning
the raw envelope, the convention breaks here rather than in a caller, and
whoever changed it has to update the documentation deliberately.

The expected annotations are spelled out rather than read back off the method
being checked — a guard that derives its expectation from its subject cannot
fail when that subject is wrong.
"""

from __future__ import annotations

import inspect

import pytest

from anima import Anima
from anima._pagination import SyncPageIterator

#: (dotted resource path, method, expected return annotation as written).
UNWRAPPED_RETURNS = [
    ("vault", "list_credentials", "list[VaultCredential]"),
    ("vault", "generate_password", "str"),
    ("phones", "list", "list[PhoneIdentityOutput]"),
    ("addresses", "list", "list[AddressOutput]"),
]

#: Paginated resources are the documented exception: the cursor has to travel
#: with the page, so these return an iterator whose ``.items`` is page one.
PAGINATED_RETURNS = [("messages", "list"), ("agents", "list")]


@pytest.fixture(scope="module")
def client() -> Anima:
    return Anima(api_key="response-shape-guard")


@pytest.mark.parametrize(("resource", "method", "expected"), UNWRAPPED_RETURNS)
def test_envelope_is_unwrapped(
    client: Anima, resource: str, method: str, expected: str
) -> None:
    fn = getattr(type(getattr(client, resource)), method)
    annotation = inspect.signature(fn).return_annotation
    rendered = annotation if isinstance(annotation, str) else getattr(
        annotation, "__name__", str(annotation)
    )
    assert rendered == expected, (
        f"client.{resource}.{method} returns {rendered!r}, not {expected!r}. "
        "If the envelope convention changed on purpose, update the README's "
        "'Response shapes' section in the same commit."
    )


@pytest.mark.parametrize(("resource", "method"), PAGINATED_RETURNS)
def test_paginated_resources_return_an_iterator(
    client: Anima, resource: str, method: str
) -> None:
    fn = getattr(type(getattr(client, resource)), method)
    annotation = str(inspect.signature(fn).return_annotation)
    assert "SyncPageIterator" in annotation, (
        f"client.{resource}.{method} returns {annotation!r}; paginated "
        "resources must return SyncPageIterator so the cursor travels with "
        "the page."
    )


def test_page_iterator_exposes_the_first_page_as_items() -> None:
    """The README tells callers to reach page one via ``.items``."""
    assert hasattr(SyncPageIterator, "items")
