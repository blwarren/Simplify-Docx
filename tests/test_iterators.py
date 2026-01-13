"""Tests for XML iterator behavior."""

from __future__ import annotations

import contextlib
from collections.abc import Iterator

import pytest
from lxml import etree

from simplify_docx.iterators import generic
from simplify_docx.iterators.generic import build_iterators, register_iterator, xml_iter
from simplify_docx.utils.warnings import UnexpectedElementWarning


class DummyElement:
    """Minimal element wrapper used for iterator tests."""

    def __init__(self, fragment: etree._Element) -> None:
        """Store the tag for validation in tests."""
        self.tag = fragment.tag


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


def test_xml_iter_warns_on_unexpected_tags() -> None:
    """Unexpected tags emit UnexpectedElementWarning."""
    root = etree.Element("root")
    etree.SubElement(root, "unexpected")

    with _clean_iterators():
        register_iterator("warn_iter")
        build_iterators()

        with pytest.warns(UnexpectedElementWarning, match="Skipping unexpected tag"):
            list(xml_iter(root, "warn_iter"))


def test_xml_iter_skips_range_and_continues() -> None:
    """Skipped ranges are not yielded and iteration continues."""
    root = etree.Element("root")
    etree.SubElement(root, "skipStart", attrib={"id": "1"})
    etree.SubElement(root, "mid", attrib={"id": "1"})
    etree.SubElement(root, "skipEnd", attrib={"id": "1"})
    etree.SubElement(root, "keep")

    with _clean_iterators():
        register_iterator(
            "skip_iter",
            tags_to_yield={"keep": DummyElement},
            tags_to_skip={"skipStart": ("id", "skipEnd")},
        )
        build_iterators()

        tags = [elt.tag for elt in xml_iter(root, "skip_iter")]

    assert tags == ["keep"]
