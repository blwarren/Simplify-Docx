"""Abstract classes for typing purposes only."""

# pylint: disable=no-self-use,pointless-statement,missing-docstring,invalid-name, too-few-public-methods
from __future__ import annotations

from collections.abc import Sequence


class xmlFragment:
    """an abstract class representing the xml fragments returned by python-docx."""

    tag: str
    prefix: str | None
    attrib: dict[str, str]
    nsmap: dict[str, str]
    text: str | None
    tail: str | None

    def getchildren(self) -> Sequence[xmlFragment]: ...
    def getparent(self) -> xmlFragment | None: ...
    def getnext(self) -> xmlFragment | None: ...
    def xpath(self, x: str) -> xmlFragment | None:  # pylint: disable=unused-argument
        ...


class ct_altchunk(xmlFragment):
    rId: str


class ct_p(xmlFragment): ...


class ct_numpr(xmlFragment): ...


# BASIC TYPES


class ct_onoff:
    val: bool


class ct_string(xmlFragment):
    val: str


class ct_decimalnumber(xmlFragment):
    val: float


# TEXT TYPES


class ct_br(xmlFragment):
    type: str | None
    clear: str | None


class ct_pPr(xmlFragment):
    numpr: ct_numpr | None


class ct_rPr(xmlFragment):
    vanish: ct_onoff | None
    webHidden: ct_onoff | None


class ct_r(xmlFragment):
    rPr: ct_rPr | None


class ct_num(xmlFragment):
    abstractNumId: xmlFragment  #  = OneAndOnlyOne('w: abstractNumId')
    # lvlOverride = ZeroOrMore('w: lvlOverride')
    numId: float  #  = RequiredAttribute('w: numId', ST_DecimalNumber)


# tables


class ct_cell(xmlFragment): ...


class ct_row(xmlFragment):
    # tblPrEx = Optional[ct_tblPrEx]
    tc: Sequence[ct_cell] | None


class ct_tbl(xmlFragment):
    tblPr: xmlFragment
    tr: Sequence[ct_row] | None


# parts


class part:
    element: xmlFragment


class documentPart:
    element: ct_document  # pylint: disable=used-before-assignment
    related_parts: dict[str, part]


class altchunkpart:
    element: documentPart


class ct_sectionPr(xmlFragment): ...


class ct_body(xmlFragment):
    sectPr: ct_sectionPr | None


class ct_document(xmlFragment):
    body: ct_body
    part: documentPart
