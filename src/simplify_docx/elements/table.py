"""Table elements."""

from collections.abc import Iterator
from typing import Any

from docx.oxml.ns import qn
from more_itertools import peekable

from . import container


class tc(container):
    """A table cell."""

    __type__ = "CT_Tc"
    __friendly__ = "table-cell"

    def to_json(
        self, doc, options: dict[str, str] | None = None, super_iter: Iterator | None = None
    ) -> dict[str, Any]:
        """Coerce a container object to JSON."""
        contents = []
        iter_me = peekable(self)
        for elt in iter_me:
            JSON = elt.to_json(doc, options, iter_me)

            if JSON["TYPE"] == "CT_P" and options.get("ignore-empty-paragraphs", False) and not JSON["VALUE"]:
                continue

            contents.append(JSON)

        out: dict[str, Any] = {"TYPE": self.__type__, "VALUE": contents}
        return out


class tr(container):
    """A table row."""

    __type__ = "CT_Row"
    __friendly__ = "table-row"


class table(container):
    """A Table object."""

    __type__ = "CT_Tbl"
    __friendly__ = "table"

    def to_json(
        self, doc, options: dict[str, str] | None = None, super_iter: Iterator | None = None
    ) -> dict[str, Any]:
        out = super().to_json(doc, options, super_iter)

        _caption = self.fragment.tblPr.find(qn("w:tblCaption"))
        if _caption is not None:
            if (not _caption.val) and options.get("ignore-empty-table-caption", True):
                pass
            else:
                out["tblCaption"] = _caption.val

        _desc = self.fragment.tblPr.find(qn("w:tblDescription"))
        if _desc is not None:
            if (not getattr(_desc, "val", None)) and options.get("ignore-empty-table-description", True):
                pass
            else:
                out["tblDescription"] = _desc.val
        return out
