"""Elements which inherit from EG_PContent."""

from collections.abc import Iterator, Sequence
from typing import ClassVar
from warnings import warn

from ..utils.paragrapy_style import get_paragraph_ind
from . import container, el
from .form import fldChar


class EG_PContent(container):  # noqa: N801
    """Base class for elements which with  EG_PContent."""

    def to_json(  # noqa: PLR0912
        self,
        doc: object,
        options: dict[str, object],
        super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a paragraph-content element to JSON."""
        fld_char: fldChar | None = None
        bare_contents: list[dict[str, object]] = []

        run_iterator = iter(self)
        while True:
            # ITERATE OVER THE PARAGRAPH CONTENTS
            for elt in run_iterator:
                if fld_char is not None:
                    finished: bool = fld_char.update(elt)
                    if finished:
                        fld_char_json = fld_char.to_json(doc, options)

                        if fld_char_json.get("TYPE", None) == "generic-field" and options.get(
                            "flatten-generic-field", True
                        ):
                            bare_contents.extend(fld_char_json.get("VALUE", []))
                        else:
                            bare_contents.append(fld_char_json)
                        fld_char = None
                    continue

                if isinstance(elt, fldChar):
                    fld_char = elt
                    continue

                bare_contents.append(elt.to_json(doc, options))

            if fld_char is not None:
                # THE PARAGRAPH ENDED IN AN INCOMPLETE FORM-FIELD
                if options.get("greedy-text-input", True):
                    try:
                        _next = super_iter.peek()
                    except StopIteration:
                        break
                    if isinstance(_next, paragraph):
                        # TODO: insert a line break into the text run...
                        run_iterator = iter(super_iter.__next__())
                    else:
                        warn(
                            f"Paragraph ended with an un-closed form-field followed by a {_next.__class__.__name__} element: this may cause parsing to fail",
                            stacklevel=2,
                        )
                        break
                else:
                    warn(
                        "Paragraph ended with an un-closed form-field: this may cause parsing to fail.  Consider setting 'greedy-text-input' to True.",
                        stacklevel=2,
                    )
                    break
            else:
                break

        contents = merge_run_contents(bare_contents, options)
        return {"TYPE": self.__type__, "VALUE": contents}


def merge_run_contents(x: Sequence[dict[str, object]], options: dict[str, object]) -> list[dict[str, object]]:
    """Merge a series of run contents as appropriate."""
    out: list[dict[str, object]] = []
    prev_data: dict[str, object] | None = None
    for data in x:
        if options.get("ignore-empty-text", True) and data["TYPE"] == "CT_Text" and not data["VALUE"]:
            continue

        if not prev_data:
            prev_data = data
            out.append(data)
            continue

        if (
            prev_data["TYPE"] == "CT_Text"
            and data["TYPE"] == "CT_Text"
            and options.get("merge-consecutive-text", True)
        ):
            prev_data["VALUE"] += data["VALUE"]

        else:
            prev_data = data
            out.append(data)

    return out


class numPr(el):  # noqa: N801
    """The paragraph numbering property."""

    __type__: ClassVar[str] = "numPr"
    __props__: ClassVar[Sequence[str]] = ["ilvl", "numId"]


class indentation(el):  # noqa: N801
    """``<w:ind>`` element, specifying paragraph indentation."""

    __type__: ClassVar[str] = "CT_Ind"
    __props__: ClassVar[Sequence[str]] = ["left", "right", "firstLine", "hanging"]


class paragraph(EG_PContent):  # noqa: N801
    """Represents a simple paragraph."""

    __name__: ClassVar[str] = "CT_P"
    __type__: ClassVar[str] = "CT_P"

    def to_json(
        self,
        doc: object,
        options: dict[str, object],
        super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a container object to JSON."""
        out: dict[str, object] = super().to_json(doc, options, super_iter)

        if options.get("remove-leading-white-space", True):
            children: list[dict[str, object]] = out["VALUE"]
            while children:
                if children[0]["TYPE"] != "CT_Text":
                    break
                first = children.pop(0)
                first["VALUE"] = first["VALUE"].lstrip()
                if first["VALUE"]:
                    children.insert(0, first)
                    break

        if options.get("remove-trailing-white-space", True):
            children = out["VALUE"]
            while children:
                if children[-1]["TYPE"] != "CT_Text":
                    break
                last = children.pop()
                last["VALUE"] = last["VALUE"].rstrip()
                if last["VALUE"]:
                    children.append(last)
                    break

        if options.get("include-paragraph-indent", True):
            _indent = get_paragraph_ind(self.fragment, doc)
            if _indent is not None:
                out["style"] = {"indent": indentation(_indent).to_json(doc, options)}

        if (
            options.get("include-paragraph-numbering", True)
            and self.fragment.pPr is not None
            and self.fragment.pPr.numPr is not None
        ):
            out["style"] = out.get("style", {})
            out["style"]["numPr"] = numPr(self.fragment.pPr.numPr).to_json(doc, options)

        return out


class hyperlink(EG_PContent):  # noqa: N801
    """The hyperlink element."""

    __type__: ClassVar[str] = "CT_Hyperlink"
    __props__: ClassVar[Sequence[str]] = ["anchor", "docLocatoin", "history", "id", "tgtFrame", "tooltip"]


class fldSimple(EG_PContent):  # noqa: N801
    """The SimpleField element."""

    __type__: ClassVar[str] = "CT_SimpleField"
    __props__: ClassVar[Sequence[str]] = ["instr", "fldLock", "dirty"]


class customXml(container):  # noqa: N801
    """The customXml element."""

    __name__: ClassVar[str] = "CustomXmlRun"
    __type__: ClassVar[str] = "CT_CustomXmlRun"
    __props__: ClassVar[Sequence[str]] = ["element"]


class smartTag(container):  # noqa: N801
    """The smartTag element."""

    __name__: ClassVar[str] = "CT_SmartTagRun"
    __type__: ClassVar[str] = "EG_PContent"
    __props__: ClassVar[Sequence[str]] = ["element", "uri"]
