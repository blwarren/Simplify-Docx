"""Table elements."""

from collections.abc import Iterator
from typing import ClassVar

from docx.oxml.ns import qn
from more_itertools import peekable

from . import container


class tc(container):  # noqa: N801
    """A table cell."""

    __type__: ClassVar[str] = "CT_Tc"
    __friendly__: ClassVar[str] = "table-cell"

    def to_json(
        self,
        doc: object,
        options: dict[str, object] | None = None,
        _super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a container object to JSON."""
        contents = []
        iter_me = peekable(self)
        for elt in iter_me:
            json_data = elt.to_json(doc, options, iter_me)

            if (
                json_data["TYPE"] == "CT_P"
                and options.get("ignore-empty-paragraphs", False)
                and not json_data["VALUE"]
            ):
                continue

            contents.append(json_data)

        out: dict[str, object] = {"TYPE": self.__type__, "VALUE": contents}
        return out


class tr(container):  # noqa: N801
    """A table row."""

    __type__: ClassVar[str] = "CT_Row"
    __friendly__: ClassVar[str] = "table-row"


class table(container):  # noqa: N801
    """A Table object."""

    __type__: ClassVar[str] = "CT_Tbl"
    __friendly__: ClassVar[str] = "table"

    def to_json(
        self,
        doc: object,
        options: dict[str, object] | None = None,
        super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a table element to JSON."""
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
