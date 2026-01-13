"""The body element."""

from collections.abc import Iterator

from .base import container


class document(container):  # noqa: N801
    """A document body element."""

    __type__ = "CT_Document"


class CT_Rel(container):  # noqa: N801
    """A document body element."""

    __type__ = "CT_Rel"
    __name__ = "CT_Rel"

    def to_json(
        self,
        doc: object,
        options: dict[str, object] | None = None,
        _super_iter: Iterator | None = None,
    ) -> dict[str, object]:
        """Coerce a container object to JSON."""
        chunk_id = self.fragment.rId
        chunk_part = doc.part.related_parts[chunk_id]
        chunk_doc = chunk_part.element
        chunk_doc.element.body.getchildren()

        return {
            "TYPE": self.__name__,
            "VALUE": document(chunk_part.element.element).to_json(chunk_doc, options),
        }


class subDoc(CT_Rel):  # noqa: N801
    """A nested sub-document."""

    __name__ = "subDoc"


class contentPart(CT_Rel):  # noqa: N801
    """A content part."""

    __name__ = "contentPart"


class altChunk(CT_Rel):  # noqa: N801
    """An alternate format chunk."""

    __type__ = "CT_AltChunk"
