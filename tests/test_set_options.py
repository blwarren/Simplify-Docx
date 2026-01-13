"""Tests for option-driven iterator configuration."""

from __future__ import annotations

import contextlib
from collections.abc import Iterator

from docx.oxml.ns import qn

import simplify_docx.iterators  # noqa: F401
from simplify_docx import __default_options__
from simplify_docx.iterators import generic
from simplify_docx.utils.set_options import set_options


@contextlib.contextmanager
def _restore_iterators() -> Iterator[None]:
    """Restore iterator definitions after the test mutates them."""
    saved_definitions = dict(generic.__definitions__)
    saved_built = dict(generic.__built__)
    try:
        yield
    finally:
        generic.__definitions__.clear()
        generic.__definitions__.update(saved_definitions)
        generic.__built__.clear()
        generic.__built__.update(saved_built)


def test_set_options_respects_flatten_flags() -> None:
    """set_options sets EG_PContent handlers based on flatten options."""
    options = dict(__default_options__)
    options["flatten-simpleField"] = True
    options["flatten-hyperlink"] = False

    with _restore_iterators():
        set_options(options)

        handlers = generic.__built__["EG_PContent"]
        tags_to_yield = handlers.TAGS_TO_YIELD or {}
        tags_to_nest = handlers.TAGS_TO_NEST or {}

        assert qn("w:fldSimple") in tags_to_nest
        assert qn("w:fldSimple") not in tags_to_yield
        assert qn("w:hyperlink") in tags_to_yield


def test_set_options_respects_flatten_custom_xml() -> None:
    """set_options controls customXml handling in run contents."""
    options = dict(__default_options__)
    options["flatten-customXml"] = False

    with _restore_iterators():
        set_options(options)

        handlers = generic.__built__["EG_ContentRunContents"]
        tags_to_yield = handlers.TAGS_TO_YIELD or {}

        assert qn("w:customXml") in tags_to_yield
