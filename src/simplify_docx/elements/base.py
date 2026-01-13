"""base classes for the docx elements."""

from collections.abc import Generator, Iterator, Sequence

from docx.oxml.shared import CT_DecimalNumber, CT_OnOff, CT_String
from docx.shared import Twips

from ..types import xmlFragment

# --------------------------------------------------
# Base Classes
# --------------------------------------------------


class IncompatibleTypeError(Exception):
    """Incompatible types."""


class el:  # noqa: N801
    """Abstract base class for docx element."""

    __type__: str
    parent: "el"
    fragment: xmlFragment
    __iter_name__: str | None = None
    __iter_xpath__: str | None = None
    __props__: Sequence[str] | None
    props: dict[str, object]

    def __init__(self, x: xmlFragment) -> None:
        """Initialize the element with its XML fragment."""
        self.fragment = x
        __props__ = getattr(self, "__props__", None)
        if __props__:
            self.props = {}
            for prop in __props__:
                self.props[prop] = getattr(x, prop)

    def to_json(
        self,
        _doc: object,  # pylint: disable=unused-argument
        _options: dict[str, object],  # pylint: disable=unused-argument
        _super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce an object to JSON."""
        out = {"TYPE": self.__type__}

        if hasattr(self, "__props__"):
            for key, prop in self.props.items():
                if prop is None:
                    continue
                out[key] = get_val(prop)
            # return dict(self.props, **out)
        return out

    def __iter__(self) -> Generator["el"]:
        """Iterate over child XML elements as typed element objects."""
        from ..iterators import xml_iter  # noqa: PLC0415

        node: xmlFragment = (
            self.fragment if self.__iter_xpath__ is None else self.fragment.xpath(self.__iter_xpath__)
        )
        yield from xml_iter(node, self.__iter_name__ if self.__iter_name__ else self.__type__)

    def simplify(self, _options: dict[str, object]) -> "el":
        """Join the next element to the current one."""
        return self

    def append(self, _x: "el") -> None:  # pylint: disable=no-self-use
        """Join the next element to the current one."""
        raise IncompatibleTypeError


def get_val(x: object) -> object:
    """Extract the value from a simple property."""
    if isinstance(x, (str, bool)):
        return x
    if isinstance(x, list):
        return [get_val(elt) for elt in x]
    if isinstance(x, (CT_String, CT_OnOff, CT_DecimalNumber)):
        return x.val
    if isinstance(x, (Twips)):
        return x.twips
    raise RuntimeError(f"Unexpected value type '{x.__class__.__name__}'")


class container(el):  # noqa: N801
    """Represents an object that can contain other objects."""

    def to_json(
        self, doc: object, options: dict[str, object], super_iter: Iterator | None = None
    ) -> dict[str, object]:
        """Coerce a container object to JSON."""
        out: dict[str, object] = super().to_json(doc, options, super_iter)
        out.update(
            {
                "TYPE": self.__type__,
                "VALUE": [elt.to_json(doc, options) for elt in self],
            }
        )
        return out
