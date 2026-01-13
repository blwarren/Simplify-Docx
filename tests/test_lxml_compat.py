"""Compatibility tests for lxml usage."""

from __future__ import annotations

import contextlib
from collections.abc import Iterator

from lxml import etree  # ty:ignore[unresolved-import]

from simplify_docx.iterators import generic
from simplify_docx.iterators.generic import build_iterators, register_iterator, skip_range, xml_iter
from simplify_docx.utils.tag import get_attrs, get_tag


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


def test_get_attrs_filters_requested_keys() -> None:
    """Only requested attributes are returned."""
    element = etree.Element("root", attrib={"a": "1", "b": "2"})
    assert get_attrs(element, ["a", "c"]) == {"a": "1"}


def test_get_tag_without_namespace() -> None:
    """Tags without namespaces are returned as plain names."""
    element = etree.Element("foo")
    tag = get_tag(element)
    assert tag.namespace is None
    assert tag.ns is None
    assert tag.tag == "foo"
    assert tag.nstag == "foo"


def test_get_tag_with_namespace_mapping() -> None:
    """Tags with namespaces are normalized with the provided mapping."""
    ns = "http://example.com/ns"
    element = etree.Element(f"{{{ns}}}bar")
    tag = get_tag(element, {"ex": ns})
    assert tag.namespace == ns
    assert tag.ns == "ex"
    assert tag.tag == "bar"
    assert tag.nstag == "ex:bar"


def test_xml_iter_uses_lxml_sibling_traversal() -> None:
    """Iterator respects lxml sibling traversal order."""
    root = etree.Element("root")
    etree.SubElement(root, "a")
    etree.SubElement(root, "b")

    iterator_name = "test_lxml_iter"
    with _clean_iterators():
        register_iterator(iterator_name, TAGS_TO_YIELD={"a": DummyElement, "b": DummyElement})
        build_iterators()

        tags = [elt.tag for elt in xml_iter(root, iterator_name)]
    assert tags == ["a", "b"]


def test_skip_range_finds_matching_end() -> None:
    """Skip range returns the matching end element for the range."""
    root = etree.Element("root")
    start = etree.SubElement(root, "start", attrib={"id": "1"})
    etree.SubElement(root, "mid", attrib={"id": "1"})
    end = etree.SubElement(root, "end", attrib={"id": "1"})

    result = skip_range(start, "id", "end")
    assert result is not None
    assert result is end
