"""Utilities for applying friendly names."""

from collections.abc import Callable


def apply_friendly_names(x: dict[str, object]) -> None:
    """Apply friendly names to a simplified document tree."""
    _walk(x, _apply_friendly_names)


__friendly_names__ = {
    "CT_Tc": "table-cell",
    "CT_Row": "table-row",
    "CT_Tbl": "table",
    "SymbolChar": "symbol",
    "CT_Ind": "indentation-data",
    "CT_SimpleField": "simple-field",
    "CT_Hyperlink": "hyperlink",
    "CT_P": "paragraph",
    "numPr": "numbering-properties",
    "Checkbox": "check-box",
    "DropDown": "drop-down",
    "CT_Text": "text",
    "TextInput": "text-input",
    "fldChar": "form-field",
    "CT_FFData": "form-field-data",
    "CT_FFTextInput": "text-input-data",
    "CT_FFDDList": "drop-down-data",
    "CT_Body": "body",
    "CT_FFCheckBox": "check-box-data",
    "CT_AltChunk": "nested-file",
    "CT_Document": "document",
    "CT_Rel": "nested-file",
}


def _apply_friendly_names(x: dict[str, object]) -> None:
    x["TYPE"] = __friendly_names__.get(x["TYPE"], x["TYPE"])


def _walk(x: dict[str, object], fun: Callable[[dict[str, object]], None]) -> None:
    fun(x)
    val = x.get("VALUE")
    if not val:
        return
    if isinstance(val, dict) and val.get("TYPE", None):
        # child is an element
        _walk(val, fun)
    if isinstance(val, list) and val[0].get("TYPE", None):
        # child is a list of elements
        for child in val:
            _walk(child, fun)
