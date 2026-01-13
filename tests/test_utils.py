"""Tests for utility helpers."""

from __future__ import annotations

import contextlib
from collections.abc import Iterator

import pytest

from simplify_docx.iterators import generic
from simplify_docx.iterators.generic import register_iterator
from simplify_docx.utils import warnings as warn_mod
from simplify_docx.utils.friendly_names import apply_friendly_names
from simplify_docx.utils.walk import walk


@contextlib.contextmanager
def _clean_iterators() -> Iterator[None]:
    """Temporarily isolate iterator registrations for test cases."""
    saved_definitions = dict(generic.__definitions__)
    saved_built = dict(generic.__built__)
    generic.__definitions__.clear()
    generic.__built__.clear()
    try:
        yield
    finally:
        generic.__definitions__.clear()
        generic.__definitions__.update(saved_definitions)
        generic.__built__.clear()
        generic.__built__.update(saved_built)


def test_walk_returns_early_when_function_returns_value() -> None:
    """Walk exits early when the callback returns a value."""
    document = {"TYPE": "document", "VALUE": [{"TYPE": "paragraph", "VALUE": []}]}

    def _find_paragraph(node: dict[str, object]) -> str | None:
        if node.get("TYPE") == "paragraph":
            return "found"
        return None

    assert walk(document, _find_paragraph, TYPE=None) == "found"


def test_walk_respects_no_iter() -> None:
    """Walk does not traverse into types listed in no_iter."""
    document = {
        "TYPE": "document",
        "VALUE": [
            {"TYPE": "paragraph", "VALUE": [{"TYPE": "text", "VALUE": []}]},
            {"TYPE": "table", "VALUE": []},
        ],
    }
    visited: list[str] = []

    def _collect(node: dict[str, object]) -> None:
        visited.append(node["TYPE"])  # type: ignore[index]

    walk(document, _collect, TYPE=None, no_iter=["paragraph"])
    assert "paragraph" in visited
    assert "text" not in visited


def test_walk_passes_parent_list_and_index_for_list_children() -> None:
    """Walk passes the parent list and index for list-based children."""
    document = {"TYPE": "document", "VALUE": [{"TYPE": "paragraph", "VALUE": []}]}
    seen: list[tuple[str, int]] = []

    def _collect(node: dict[str, object], parent: list[dict[str, object]] | None, index: int | None) -> None:
        if node.get("TYPE") == "paragraph":
            assert parent is not None
            assert index is not None
            seen.append((node["TYPE"], index))  # type: ignore[index]

    walk(document, _collect, TYPE=None)
    assert seen == [("paragraph", 0)]


def test_apply_friendly_names_updates_nested_types() -> None:
    """Friendly names are applied to nested elements."""
    document = {
        "TYPE": "CT_Document",
        "VALUE": [
            {"TYPE": "CT_P", "VALUE": [{"TYPE": "CT_Text", "VALUE": []}]},
            {"TYPE": "CustomType", "VALUE": []},
        ],
    }

    apply_friendly_names(document)

    assert document["TYPE"] == "document"
    assert document["VALUE"][0]["TYPE"] == "paragraph"
    assert document["VALUE"][0]["VALUE"][0]["TYPE"] == "text"
    assert document["VALUE"][1]["TYPE"] == "CustomType"


def test_unexpected_element_warning_is_runtime_warning() -> None:
    """UnexpectedElementWarning derives from RuntimeWarning."""
    assert issubclass(warn_mod.UnexpectedElementWarning, RuntimeWarning)


def test_register_iterator_rejects_duplicate_names() -> None:
    """register_iterator raises on duplicate names."""
    with _clean_iterators():
        register_iterator("dup-name")
        with pytest.raises(ValueError, match="already registered"):
            register_iterator("dup-name")
