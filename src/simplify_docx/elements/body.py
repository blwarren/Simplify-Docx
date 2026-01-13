"""The body element."""

from collections.abc import Iterator

from more_itertools import peekable

from .base import container


class body(container):  # noqa: N801
    """A document body element."""

    __type__ = "CT_Body"

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
