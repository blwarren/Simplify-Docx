"""Form Field Data."""

from collections.abc import Iterator, Sequence
from typing import ClassVar
from warnings import warn

from ..types import xmlFragment
from . import el
from .base import get_val


class checkBox(el):  # noqa: N801
    """The ffData checkBox attribute."""

    __type__: ClassVar[str] = "CT_FFCheckBox"
    __props__: ClassVar[Sequence[str]] = ["default", "checked"]


class ddList(el):  # noqa: N801
    """The ffData ddList attribute."""

    __type__: ClassVar[str] = "CT_FFDDList"
    __props__: ClassVar[Sequence[str]] = ["default", "result", "listEntry_lst"]


class textInput(el):  # noqa: N801
    """The ffData textInput attribute."""

    __type__: ClassVar[str] = "CT_FFTextInput"
    __props__: ClassVar[Sequence[str]] = ["default", "type_", "format_"]


class ffData(el):  # noqa: N801
    """The ffData element."""

    __props__: ClassVar[Sequence[str]] = [
        "name",
        "label",
        "tabIndex",
        "enabled",
        "calcOnExit",
        "entryMacro",
        "exitMacro",
        "helpText",
        "statusText",
    ]
    __type__: ClassVar[str] = "CT_FFData"

    def __init__(self, x: xmlFragment) -> None:
        """Initialize form field data from an XML fragment."""
        super().__init__(x)

        check_box = getattr(x, "checkBox", None)
        if check_box is not None:
            self.check_box = checkBox(check_box)

        drop_down = getattr(x, "ddList", None)
        if drop_down is not None:
            self.dd_list = ddList(drop_down)

        text_input = getattr(x, "textInput", None)
        if text_input is not None:
            self.text_input = textInput(text_input)

    def to_json(
        self,
        doc: object,
        options: dict[str, object],
        super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a form field data element to JSON."""
        out = super().to_json(doc, options, super_iter)

        if getattr(self.fragment, "checkBox", None) is not None:
            out["checkBox"] = self.check_box.to_json(doc, options)

        if getattr(self.fragment, "ddList", None) is not None:
            out["ddList"] = self.dd_list.to_json(doc, options)

        if getattr(self.fragment, "textInput", None) is not None:
            out["textInput"] = self.text_input.to_json(doc, options)

        return out

    def field_results(self) -> xmlFragment:
        """Extract the field results elements."""
        return self.fragment


class fldChar(el):  # noqa: N801
    """Form Field Data."""

    __type__: ClassVar[str] = "fldChar"
    __props__: ClassVar[Sequence[str]] = ["fldCharType", "fldLock", "dirty"]

    field_codes: Sequence[el]
    field_results: Sequence[el]
    ff_data: ffData | None

    def __init__(self, x: xmlFragment) -> None:
        """Initialize the form field character from XML."""
        super().__init__(x)

        self.status = "fieldCodes"
        self.field_codes = []
        self.field_results = []
        ff_data = getattr(x, "ffData", None)
        if ff_data is not None:
            self.ff_data = ffData(ff_data)
            if getattr(x.ffData, "checkBox", None) is not None:
                self.__type__ = "Checkbox"
            elif getattr(x.ffData, "ddList", None) is not None:
                self.__type__ = "DropDown"
            elif getattr(x.ffData, "textInput", None) is not None:
                self.__type__ = "TextInput"
            else:
                warn("fldChar has unexpected ffData attribute: treating as generic-field", stacklevel=2)
                self.__type__ = "generic-field"
        else:
            self.ff_data = None
            self.__type__ = "generic-field"

    def to_json(  # noqa: PLR0911, PLR0912, PLR0915
        self,
        doc: object,
        options: dict[str, object],
        super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a form field character element to JSON."""
        out = super().to_json(doc, options, super_iter)
        from .paragraph import merge_run_contents  # noqa: PLC0415

        if self.__type__ == "Checkbox":
            checked = self.ff_data.check_box.props["checked"]
            if checked is None and options.get("use-checkbox-default", True):
                checked = self.ff_data.check_box.props["default"]
            value = None if checked is None else checked.val

            if options.get("checkbox-as-text", False):
                out.update({"TYPE": "CT_Text", "VALUE": f"[{self.__type__}:{value}]"})
                return out

            if options.get("simplify-checkbox", True):
                out.pop("fldCharType", None)
                out["VALUE"] = value
                _update_from(out, self.ff_data.check_box.props, ["default"])
                return out

        elif self.__type__ == "DropDown":
            values = self.ff_data.dd_list.props["listEntry_lst"]

            if options.get("trim-dropdown-options", True):
                for option in values:
                    option.val = option.val.strip()

            if not values:
                value = None
            else:
                result = self.ff_data.dd_list.props["result"]
                default = self.ff_data.dd_list.props["default"]
                if result is None:
                    value = values[0].val if default is None else values[default.val].val
                else:
                    value = values[result.val].val

            if options.get("dropdown-as-text", False):
                out.update({"TYPE": "CT_Text", "VALUE": f"[{self.__type__}:{value}]"})
                return out

            if options.get("simplify-dropdown", True):
                out.pop("fldCharType", None)
                out["VALUE"] = value
                _update_from(
                    out,
                    self.ff_data.dd_list.props,
                    ["default", "result", "listEntry_lst"],
                )
                out["options"] = out.pop("listEntry_lst")
                return out

        elif self.__type__ == "TextInput":
            text_contents = [elt.to_json(doc, options) for elt in self.field_results]
            contents = merge_run_contents(text_contents, options)
            value = contents[0]["VALUE"] if len(contents) == 1 else contents

            if options.get("textinput-as-text", False):
                if len(contents) > 1:
                    warn("Textinput has more than one element; ignoring all but the first element", stacklevel=2)
                out.update(
                    {
                        "TYPE": "CT_Text",
                        "VALUE": "[%s:%s]" % (contents[0]["VALUE"] if contents else ""),
                    }
                )
                return out

            if options.get("simplify-textinput", True):
                out.pop("fldCharType", None)
                if len(contents) > 1:
                    warn("Textinput has more than one element; ignoring all but the first element", stacklevel=2)
                out["VALUE"] = contents[0]["VALUE"] if contents else ""
                _update_from(out, self.ff_data.text_input.props, ["default"])
                return out

        else:
            generic_contents = [elt.to_json(doc, options) for elt in self.field_results]
            value = merge_run_contents(generic_contents, options)
            if options.get("flatten-generic-field", True):
                out["VALUE"] = value
                out.pop("fldCharType", None)
                return out

        resolved_contents = [elt.to_json(doc, options) for elt in self.field_results]
        contents = merge_run_contents(resolved_contents, options)
        codes = [elt.to_json(doc, options) for elt in self.field_codes]

        out.update(
            {
                "TYPE": self.__type__,
                "VALUE": value,
                "ffData": self.ff_data.to_json(doc, options),
                "fieldCodes": codes,
                "fieldResults": contents,
            }
        )

        return out

    def update(self, other: el) -> bool:
        """Update an incomplete field character."""
        if self.status == "complete":
            raise RuntimeError("Logic Error: Updating a completed field data")

        if isinstance(other, fldChar):
            fld_char_type = other.props.get("fldCharType")
            if fld_char_type == "begin":
                raise RuntimeError("Unhandled nesting of data fields")

            if fld_char_type == "separate":
                self.status = "fieldResults"
                return False
            if fld_char_type == "end":
                self.status = "complete"
                return True

        if self.status == "fieldResults":
            self.field_results.append(other)
        else:
            self.field_codes.append(other)
        return False


def _update_from(x: dict[str, object], y: dict[str, object], attrs: Sequence[str]) -> None:
    """Copy attributes from one object to another."""
    for attr in attrs:
        val = y.get(attr)
        if val is not None:
            x[attr] = get_val(val)
