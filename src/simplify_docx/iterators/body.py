"""Iterate over containers (i.e. "things that can contain EG_BlockLevelElts")."""

from docx.oxml.ns import qn

from ..elements import altChunk, empty, paragraph, table
from .generic import register_iterator

# RANGE MARKUP
register_iterator(
    "EG_RangeMarkupElements",
    tags_to_ignore=[
        qn("w:bookmarkStart"),
        qn("w:bookmarkEnd"),
        qn("w:commentRangeStart"),
        qn("w:commentRangeEnd"),
        qn("w:moveToRangeStart"),
        qn("w:moveToRangeEnd"),
    ],
    tags_to_warn={
        qn("w:customXmlInsRangeStart"): "Ignoring Revision Tags",
        qn("w:customXmlInsRangeEnd"): "Ignoring Revision Tags",
        qn("w:customXmlDelRangeStart"): "Ignoring Revision Tags",
        qn("w:customXmlDelRangeEnd"): "Ignoring Revision Tags",
        qn("w:customXmlMoveFromRangeStart"): "Ignoring Revision Tags",
        qn("w:customXmlMoveFromRangeEnd"): "Ignoring Revision Tags",
        qn("w:customXmlMoveToRangeStart"): "Ignoring Revision Tags",
        qn("w:customXmlMoveToRangeEnd"): "Ignoring Revision Tags",
    },
    tags_to_skip={qn("w:moveFromRangeStart"): ("id", qn("w:MoveFromRangeEnd"))},
)

# RUN LEVEL LEMENTS
register_iterator(
    "EG_RunLevelElts",
    tags_to_yield={qn("m:oMathPara"): empty, qn("m:oMath"): empty},
    tags_to_nest={qn("w:ins"): "EG_RunLevelElts", qn("w:moveTo"): "EG_RunLevelElts"},
    tags_to_ignore=[
        # INVISIBLE THINGS
        qn("w:proofErr"),
        qn("w:permStart"),
        qn("w:permEnd"),
        qn("w:del"),
        qn("w:moveFrom"),
        qn("w:commentRangeStart"),
        qn("w:commentRangeEnd"),
        # RANGE MARKER
        qn("w:moveToRangeStart"),
        qn("w:moveToRangeEnd"),
    ],
    extends=["EG_RangeMarkupElements"],
)

# BLOCK LEVEL ELEMENTS
register_iterator(
    "EG_BlockLevelElts",
    tags_to_yield={
        qn("w:p"): paragraph,
        qn("w:tbl"): table,
        qn("w:sdt"): empty,
        qn("w:altChunk"): altChunk,
    },
    tags_to_nest={qn("w:customXml"): "EG_BlockLevelElts"},
    tags_to_ignore=[qn("w:sectPr"), qn("w:tcPr"), qn("w:pPr")],
    extends=["EG_RunLevelElts"],
)

# BODY
register_iterator("CT_Body", tags_to_ignore=[qn("w:sectPr")], extends=["EG_BlockLevelElts"])
