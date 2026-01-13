"""Docx element objects."""

# from .blocks import smartTag, customXml, fldSimple, hyperlink, paragraph_list, paragraph
from .base import IncompatibleTypeError, container, el
from .body import body
from .document import altChunk, contentPart, document, subDoc
from .form import checkBox, ddList, ffData, fldChar, textInput
from .paragraph import (
    EG_PContent,
    customXml,
    fldSimple,
    hyperlink,
    paragraph,
    smartTag,
)
from .run_contents import SymbolChar, empty, simpleTextElement, text
from .table import table, tc, tr

__all__ = [
    "EG_PContent",
    "IncompatibleTypeError",
    "SymbolChar",
    "altChunk",
    "body",
    "checkBox",
    "container",
    "contentPart",
    "customXml",
    "ddList",
    "document",
    "el",
    "empty",
    "ffData",
    "fldChar",
    "fldSimple",
    "hyperlink",
    "paragraph",
    "simpleTextElement",
    "smartTag",
    "subDoc",
    "table",
    "tc",
    "text",
    "textInput",
    "tr",
]
