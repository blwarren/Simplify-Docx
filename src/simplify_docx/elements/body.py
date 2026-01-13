"""The body element."""

from collections.abc import Iterator
from typing import Any

from more_itertools import peekable

from .base import container


class body(container):
    """A document body element."""

    __type__ = "CT_Body"

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
