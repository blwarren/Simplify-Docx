"""Generic XML iterators."""
# pylint: disable=too-many-arguments, too-many-branches

from collections.abc import Callable, Generator, Sequence
from typing import NamedTuple, NewType
from warnings import warn

from ..elements.base import el
from ..types import xmlFragment
from ..utils.tag import get_tag
from ..utils.warnings import UnexpectedElementWarning

FragmentIterator = NewType("FragmentIterator", Callable[[xmlFragment, str | None], Generator[xmlFragment]])

# CONSTANTS


class ElementHandlers(NamedTuple):
    """A convenience class."""

    TAGS_TO_YIELD: dict[str, type[el]] | None
    TAGS_TO_NEST: dict[str, str] | None
    TAGS_TO_IGNORE: Sequence[str] | None
    TAGS_TO_WARN: dict[str, str] | None
    TAGS_TO_SKIP: dict[str, tuple[str, str]] | None
    extends: Sequence[str] | None


ElementHandlers.__new__.__defaults__ = (None,) * 6  # https://stackoverflow.com/questions/11351032/

__definitions__: dict[str, ElementHandlers] = {}
__built__: dict[str, ElementHandlers] = {}


def register_iterator(  # noqa: PLR0913
    name: str,
    tags_to_yield: dict[str, type[el]] | None = None,
    tags_to_nest: dict[str, str] | None = None,
    tags_to_ignore: Sequence[str] | None = None,
    tags_to_warn: dict[str, str] | None = None,
    tags_to_skip: dict[str, tuple[str, str]] | None = None,
    extends: Sequence[str] | None = None,
    check_name: bool = True,
) -> None:
    """Register an iterator that skips deleted/moved resources and revision containers.

    This configuration also ignores orientation elements like bookmarks, comments, and permissions.
    """
    if check_name and name in __definitions__:
        raise ValueError(f"iterator named '{name}' already registered")

    __definitions__[name] = ElementHandlers(
        tags_to_yield, tags_to_nest, tags_to_ignore, tags_to_warn, tags_to_skip, extends=extends
    )


def build_iterators() -> None:
    """Build the iterators for the current iteration."""
    _resovled: list[str] = []

    def _resolve(x: str) -> None:
        if x in _resovled:
            return

        xdef = __definitions__[x]
        if not xdef.extends:
            __built__[x] = xdef
            _resovled.append(x)
            return

        tags_to_yield = dict(xdef.TAGS_TO_YIELD) if xdef.TAGS_TO_YIELD else {}
        tags_to_nest = dict(xdef.TAGS_TO_NEST) if xdef.TAGS_TO_NEST else {}
        tags_to_ignore = list(xdef.TAGS_TO_IGNORE) if xdef.TAGS_TO_IGNORE else []
        tags_to_warn = dict(xdef.TAGS_TO_WARN) if xdef.TAGS_TO_WARN else {}
        tags_to_skip = dict(xdef.TAGS_TO_SKIP) if xdef.TAGS_TO_SKIP else {}

        for dependency in xdef.extends:
            try:
                _resolve(dependency)
            except KeyError as err:
                msg = f"Iterator for '{x}' depends on undefined group '{dependency}'"
                raise RuntimeError(msg) from err

            ddef = __built__[dependency]
            if ddef.TAGS_TO_YIELD:
                tags_to_yield.update(ddef.TAGS_TO_YIELD)
            if ddef.TAGS_TO_NEST:
                tags_to_nest.update(ddef.TAGS_TO_NEST)
            if ddef.TAGS_TO_IGNORE:
                tags_to_ignore.extend(ddef.TAGS_TO_IGNORE)
            if ddef.TAGS_TO_WARN:
                tags_to_warn.update(ddef.TAGS_TO_WARN)
            if ddef.TAGS_TO_SKIP:
                tags_to_skip.update(ddef.TAGS_TO_SKIP)

        __built__[x] = ElementHandlers(
            TAGS_TO_YIELD=tags_to_yield,
            TAGS_TO_NEST=tags_to_nest,
            TAGS_TO_IGNORE=tags_to_ignore,
            TAGS_TO_WARN=tags_to_warn,
            TAGS_TO_SKIP=tags_to_skip,
        )

        _resovled.append(x)

    for name in __definitions__:
        _resolve(name)


def xml_iter(p: xmlFragment, name: str, msg: str | None = None) -> Generator[el]:  # noqa: PLR0912
    """Iterate over an XML node yielding an appropriate element (el)."""
    handlers = __built__[name]

    # INIT PHASE
    children = p.getchildren()
    if not children:
        return

    current: xmlFragment | None = p.getchildren()[0]

    # ITERATION PHASE
    while current is not None:
        if msg is not None and current.tag not in handlers.TAGS_TO_IGNORE:
            print(msg + ("" if current.prefix is None else (current.prefix + ":")) + current.tag)

        if handlers.TAGS_TO_YIELD and current.tag in handlers.TAGS_TO_YIELD:
            # Yield all math tags
            yield handlers.TAGS_TO_YIELD[current.tag](current)

            if handlers.TAGS_TO_NEST and current.tag in handlers.TAGS_TO_NEST:
                _msg = None if msg is None else ("  " + msg)
                for elt in xml_iter(current, handlers.TAGS_TO_NEST[current.tag], _msg):
                    yield elt

        elif handlers.TAGS_TO_NEST and current.tag in handlers.TAGS_TO_NEST:
            _msg = None if msg is None else ("  " + msg)
            for elt in xml_iter(current, handlers.TAGS_TO_NEST[current.tag], _msg):
                yield elt

        elif handlers.TAGS_TO_WARN and current.tag in handlers.TAGS_TO_WARN:
            # Skip these unhandled tags with a warning
            warn(f"Skipping {handlers.TAGS_TO_WARN[current.tag]} tag: {current.tag}", stacklevel=2)

        elif handlers.TAGS_TO_IGNORE and current.tag in handlers.TAGS_TO_IGNORE:
            # ignore paragraph properties, deleted content and meta tags
            # like bookmarks, permissions, comments, etc.
            pass

        elif handlers.TAGS_TO_SKIP and current.tag in handlers.TAGS_TO_SKIP:
            # Skip over content that has been moved elsewhere
            data = handlers.TAGS_TO_SKIP[current.tag]
            current = skip_range(current, data[0], data[1])
            if current is None:
                return

        else:
            warn(f"Skipping unexpected tag: {current.tag}", UnexpectedElementWarning, stacklevel=2)

        current = current.getnext()

    return


def skip_range(x: xmlFragment, id_attr: str, waitfor: str) -> xmlFragment | None:
    """Return the element at the end of the range."""
    _id: str = x.attrib[id_attr]
    current: xmlFragment | None = x.getnext()

    while True:
        if current is None:
            return current
        if get_tag(current).tag == waitfor and current.attrib[id_attr] == _id:
            return current
        current = current.getnext()
