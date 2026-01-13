"""Table and row iterators."""

from docx.oxml.ns import qn

from ..elements import empty, tc, tr
from .generic import register_iterator

# TABLE ITERATOR
register_iterator(
    "CT_Tbl",
    tags_to_ignore=[qn("w:tblPr"), qn("w:tblGrid")],
    extends=["EG_ContentRowContent"],
)

register_iterator(
    "EG_ContentRowContent",
    tags_to_yield={qn("w:tr"): tr, qn("w:sdt"): empty},
    tags_to_nest={qn("w:customXml"): "EG_ContentRowContent"},
    tags_to_ignore=[qn("w:customXmlPr")],
    extends=["EG_RangeMarkupElements"],
)


# ROW ITERATOR
register_iterator(
    "CT_Row",
    tags_to_ignore=[qn("w:tblPrEx"), qn("w:trPr")],
    extends=["EG_ContentCellContent"],
)

register_iterator(
    "EG_ContentCellContent",
    tags_to_yield={qn("w:tc"): tc, qn("w:sdt"): empty},
    tags_to_nest={qn("w:customXml"): "EG_ContentCellContent"},
    tags_to_ignore=[
        # FORMATTING PROPERTIES
        qn("w:customXmlPr")
    ],
    extends=["EG_RunLevelElts"],
)

# CELL ITERATOR
register_iterator("CT_Tc", tags_to_ignore=[qn("w:tcPr")], extends=["EG_BlockLevelElts"])
