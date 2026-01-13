"""Tests for tag utility helpers."""

from __future__ import annotations

from lxml import etree

from simplify_docx.utils.tag import NS_SCHEMA, get_attrs, get_tag


def test_get_attrs_filters_missing_attributes() -> None:
    """get_attrs returns only attributes present on the element."""
    element = etree.Element("root", attrib={"one": "1", "two": "2"})

    assert get_attrs(element, ["one", "missing"]) == {"one": "1"}


def test_get_tag_handles_non_namespaced_elements() -> None:
    """get_tag returns a plain tuple for non-namespaced elements."""
    element = etree.Element("plain")

    assert get_tag(element) == (None, None, "plain", "plain")


def test_get_tag_uses_known_namespace_mappings() -> None:
    """get_tag resolves namespace prefixes when using known mappings."""
    namespace = NS_SCHEMA["w"]
    element = etree.Element(f"{{{namespace}}}p")

    tag = get_tag(element)

    assert tag.namespace == namespace
    assert tag.ns == "w"
    assert tag.tag == "p"
    assert tag.nstag == "w:p"


def test_get_tag_uses_custom_namespace_mappings() -> None:
    """get_tag honors the provided namespace map."""
    namespace = "urn:example"
    element = etree.Element(f"{{{namespace}}}item")

    tag = get_tag(element, nsdict={"x": namespace})

    assert tag.namespace == namespace
    assert tag.ns == "x"
    assert tag.tag == "item"
    assert tag.nstag == "x:item"
