"""Tests for paragraph content merging."""

from __future__ import annotations

from simplify_docx.elements.paragraph import merge_run_contents


def test_merge_run_contents_merges_consecutive_text() -> None:
    """merge_run_contents combines consecutive text nodes."""
    items = [
        {"TYPE": "CT_Text", "VALUE": "Hello"},
        {"TYPE": "CT_Text", "VALUE": "World"},
        {"TYPE": "CT_Empty", "VALUE": "[w:br]"},
    ]

    options = {"merge-consecutive-text": True, "ignore-empty-text": True}

    assert merge_run_contents(items, options) == [
        {"TYPE": "CT_Text", "VALUE": "HelloWorld"},
        {"TYPE": "CT_Empty", "VALUE": "[w:br]"},
    ]


def test_merge_run_contents_respects_disable_merge() -> None:
    """merge_run_contents skips merging when disabled."""
    items = [
        {"TYPE": "CT_Text", "VALUE": "Hello"},
        {"TYPE": "CT_Text", "VALUE": "World"},
    ]

    options = {"merge-consecutive-text": False, "ignore-empty-text": True}

    assert merge_run_contents(items, options) == items


def test_merge_run_contents_drops_empty_text_when_enabled() -> None:
    """merge_run_contents removes empty text nodes when enabled."""
    items = [
        {"TYPE": "CT_Text", "VALUE": ""},
        {"TYPE": "CT_Text", "VALUE": "Content"},
    ]

    options = {"merge-consecutive-text": True, "ignore-empty-text": True}

    assert merge_run_contents(items, options) == [{"TYPE": "CT_Text", "VALUE": "Content"}]
