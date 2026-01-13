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
