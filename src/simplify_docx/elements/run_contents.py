"""Run level elements."""

import re
from collections.abc import Iterator
from typing import ClassVar

from docx.oxml.ns import qn

from ..types import xmlFragment
from . import el  # , IncompatibleTypeError

RE_SPACES = re.compile("  +", re.IGNORECASE)


class empty(el):  # noqa: N801
    """Generic for CT_Empty elements."""

    __type__: str

    def __init__(self, x: xmlFragment) -> None:
        """Initialize an empty element from XML."""
        super().__init__(x)
        self.__type__ = x.tag.split("}")[-1]

    def to_json(
        self,
        _doc: object,
        options: dict[str, object],
        _super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce an object to JSON."""
        if options.get("empty-as-text", False):
            return {"TYPE": "CT_Text", "VALUE": f"[w:{self.__type__}]"}

        return {"TYPE": "CT_Empty", "VALUE": f"[w:{self.__type__}]"}


# settings to be imported at a later time
default_text_options = {
    "simplify_text": True,
    "simplify_symbol": True,
    "simplify_empty": True,
}


class text(el):  # noqa: N801
    """A Text element."""

    __type__: str
    value: str

    def __init__(self, x: xmlFragment) -> None:
        """Initialize the text element from XML."""
        super().__init__(x)
        self.__type__ = x.tag.split("}")[-1]
        if x.text is None:
            self.value = ""
        else:
            self.value = x.text

    def to_json(
        self,
        _doc: object,
        options: dict[str, object],
        _super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce an object to JSON."""
        _value = self.value
        if options.get("dumb-quotes", True):
            _value = (
                _value.replace("\u2018", "'").replace("\u2019", "'").replace("\u201a", "'").replace("\u201b", "'")
            )
            _value = _value.replace("\u201c", '"').replace("\u201d", '"')

        if options.get("dumb-spaces", True):
            _value = (
                _value.replace("\u2000", " ")
                .replace("\u2001", " ")
                .replace("\u2002", " ")
                .replace("\u2003", " ")
                .replace("\u2004", " ")
                .replace("\u2005", " ")
                .replace("\u2006", " ")
                .replace("\u2007", " ")
                .replace("\u2008", " ")
                .replace("\u2009", " ")
                .replace("\u200a", " ")
                .replace("\u201b", " ")
            )

        if options.get("dumb-hyphens", True):
            _value = (
                _value.replace("\u2010", "-")
                .replace("\u2011", "-")
                .replace("\u2012", "-")
                .replace("\u2013", "-")
                .replace("\u2014", "-")
                .replace("\u2015", "-")
                .replace("\u00a0", "-")
            )

        if options.get("ignore-joiners", True):
            _value = _value.replace("\u200c", "").replace("\u200d", "")

        if options.get("flatten-inner-spaces", True):
            _value = RE_SPACES(" ", _value)

        if options.get("ignore-left-to-right-mark", False):
            _value = _value.replace("\u200e", "")

        if options.get("ignore-right-to-left-mark", False):
            _value = _value.replace("\u200f", "")

        return {"TYPE": "CT_Text", "VALUE": _value}


class SymbolChar(el):
    """Represent a symbol character element.

    The font matters for rendering even though the element is text-like.
    """

    __type__: ClassVar[str] = "SymbolChar"
    char: str
    font: str

    def __init__(self, x: xmlFragment) -> None:
        """Initialize the symbol character element from XML."""
        super().__init__(x)
        self.char = x.get(qn("w:char"))
        self.font = x.get(qn("w:font"))

    def to_json(
        self,
        _doc: object,
        options: dict[str, object],
        _super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce an object to JSON."""
        if options.get("symbol-as-text", True):
            return {"TYPE": "CT_Text", "VALUE": self.char}

        return {"TYPE": self.__type__, "VALUE": {"char": self.char, "font": self.font}}


simple_text_element_text = {
    "CarriageReturn": "\r",
    "Break": "\r",
    "TabChar": "\t",
    "PositionalTab": "\t",
    "NoBreakHyphen": "-",
    "SoftHyphen": "-",
}


tag_to_type_map: dict[str, str] = {
    qn("w:br"): "Break",
    qn("w:cr"): "CarriageReturn",
    qn("w:tab"): "TabChar",
    qn("w:noBreakHyphen"): "NoBreakHyphen",
    qn("w:softHyphen"): "SoftHyphen",
    qn("w:ptab"): "PositionalTab",
}


class simpleTextElement(el):  # noqa: N801
    """A simple text element represented by a CT_Empty."""

    def __init__(self, x: xmlFragment) -> None:
        """Initialize the simple text element from XML."""
        super().__init__(x)
        self.__type__ = tag_to_type_map[x.tag]

    def to_json(
        self,
        _doc: object,
        options: dict[str, object],
        _super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a simple text element to JSON."""
        if options.get("special-characters-as-text", True):
            return {"TYPE": "CT_Text", "VALUE": simple_text_element_text[self.__type__]}

        return {"TYPE": self.__type__}
