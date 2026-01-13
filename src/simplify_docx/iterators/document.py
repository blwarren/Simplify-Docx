"""Iterate over Document and AltChunk (i.e. "things that can contain EG_BlockLevelElts")."""

from docx.oxml.ns import qn

from ..elements import body
from .generic import register_iterator

register_iterator(
    "CT_Document",
    tags_to_yield={qn("w:body"): body},
    tags_to_ignore=[qn("w:docPartPr")],
)
