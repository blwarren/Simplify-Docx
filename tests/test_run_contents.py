"""Tests for run-level content elements."""

from __future__ import annotations

from docx.oxml.ns import qn
from lxml import etree

from simplify_docx.elements.run_contents import SymbolChar, empty, simpleTextElement, text


def test_text_to_json_normalizes_characters() -> None:
    """Text replaces special characters based on options."""
    element = etree.Element(qn("w:t"))
    element.text = "\u201cHi\u201d\u2002\u2014\u200d"
    text_element = text(element)

    options = {
        "dumb-quotes": True,
        "dumb-spaces": True,
        "dumb-hyphens": True,
        "ignore-joiners": True,
        "flatten-inner-spaces": False,
        "ignore-left-to-right-mark": False,
        "ignore-right-to-left-mark": False,
    }

    assert text_element.to_json(None, options)["VALUE"] == '"Hi" -'


def test_empty_to_json_respects_empty_as_text() -> None:
    """Empty elements can render as text when configured."""
    element = etree.Element(qn("w:instrText"))
    empty_element = empty(element)

    as_text = empty_element.to_json(None, {"empty-as-text": True})
    as_empty = empty_element.to_json(None, {"empty-as-text": False})

    assert as_text == {"TYPE": "CT_Text", "VALUE": "[w:instrText]"}
    assert as_empty == {"TYPE": "CT_Empty", "VALUE": "[w:instrText]"}


def test_symbol_char_to_json_respects_symbol_as_text() -> None:
    """SymbolChar can return a text representation or a structured object."""
    element = etree.Element(qn("w:sym"))
    element.set(qn("w:char"), "A")
    element.set(qn("w:font"), "Wingdings")
    symbol_element = SymbolChar(element)

    as_text = symbol_element.to_json(None, {"symbol-as-text": True})
    as_structured = symbol_element.to_json(None, {"symbol-as-text": False})

    assert as_text == {"TYPE": "CT_Text", "VALUE": "A"}
    assert as_structured == {"TYPE": "SymbolChar", "VALUE": {"char": "A", "font": "Wingdings"}}


def test_simple_text_element_outputs_text_when_enabled() -> None:
    """SimpleTextElement emits text when special-characters-as-text is enabled."""
    element = etree.Element(qn("w:tab"))
    simple_element = simpleTextElement(element)

    as_text = simple_element.to_json(None, {"special-characters-as-text": True})

    assert as_text == {"TYPE": "CT_Text", "VALUE": "\t"}


def test_simple_text_element_outputs_type_when_disabled() -> None:
    """SimpleTextElement emits the type when special-characters-as-text is disabled."""
    element = etree.Element(qn("w:tab"))
    simple_element = simpleTextElement(element)

    as_type = simple_element.to_json(None, {"special-characters-as-text": False})

    assert as_type == {"TYPE": "TabChar"}
