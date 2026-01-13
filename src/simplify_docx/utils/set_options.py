"""Utilities for setting options that change how the document is traversed."""

from docx.oxml.ns import qn

from ..elements import customXml, el, empty, fldSimple, hyperlink, subDoc
from ..iterators.generic import build_iterators, register_iterator


def set_options(options: dict[str, str | bool | int | float]) -> None:
    """Register iterators depending on the selected options."""
    _set_eg_p_contents(options)
    _set_eg_content_run_contents(options)
    build_iterators()


def _set_eg_p_contents(options: dict[str, str | bool | int | float]) -> None:
    """group:"EG_PContent"."""
    tags_to_yield: dict[str, type[el]] = {qn("w:subDoc"): subDoc}

    tags_to_nest: dict[str, str] = {qn("w:r"): "CT_R"}

    # -----------------------------------------------
    if options["flatten-simpleField"]:
        tags_to_nest[qn("w:fldSimple")] = "EG_PContent"
    else:
        tags_to_yield[qn("w:fldSimple")] = fldSimple

    # -----------------------------------------------
    if options["flatten-hyperlink"]:
        tags_to_nest[qn("w:hyperlink")] = "EG_PContent"
    else:
        tags_to_yield[qn("w:hyperlink")] = hyperlink

    # -----------------------------------------------
    register_iterator(
        "EG_PContent",
        tags_to_yield=tags_to_yield,
        tags_to_nest=tags_to_nest,
        tags_to_ignore=[qn("w:customXmlPr"), qn("w:smartTagPr")],
        extends=["EG_RunLevelElts"],
        check_name=False,
    )


def _set_eg_content_run_contents(options: dict[str, str | bool | int | float]) -> None:
    """group: EG_ContentRunContent."""
    tags_to_yield: dict[str, type[el]] = {qn("w:sdt"): empty}

    tags_to_nest: dict[str, str] = {qn("w:r"): "CT_R"}

    # -----------------------------------------------
    if options["flatten-smartTag"]:
        tags_to_nest[qn("w:smartTag")] = "EG_PContent"
    else:
        tags_to_yield[qn("w:smartTag")] = empty

    # -----------------------------------------------
    if options["flatten-customXml"]:
        tags_to_nest[qn("w:customXml")] = "EG_PContent"
    else:
        tags_to_yield[qn("w:customXml")] = customXml

    # -----------------------------------------------
    register_iterator(
        "EG_ContentRunContents",
        tags_to_yield=tags_to_yield,
        tags_to_nest=tags_to_nest,
        tags_to_warn={
            qn("w:dir"): "Ignoring text-direction tags",
            qn("w:bdo"): "Ignoring text-direction tags",
        },
        extends=["EG_RunLevelElts"],
        check_name=False,
    )
