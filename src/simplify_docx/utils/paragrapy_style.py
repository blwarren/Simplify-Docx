"""Helpers for extracting paragraph indention levels."""


def get_p_style(p: object, doc: object) -> object | None:
    """Get the referenced style element for a paragraph with a p.pPr.pStyle."""
    if getattr(p, "pPr", None) is not None and p.pPr.pStyle is not None:
        return doc.styles.element.find(f"w:style[@w:styleId='{p.pPr.pStyle.val}']", doc.styles.element.nsmap)
    return None


def get_num_style(p: object, doc: object) -> object | None:
    """Get the paragraph's numbering style."""
    if getattr(p, "pPr", None) is not None and p.pPr.numPr is not None and p.pPr.numPr.numId is not None:
        # the numbering style doc
        np = doc.part.numbering_part
        # the map between numbering id and the numbering style
        num = np.element.find(f"w:num[@w:numId='{p.pPr.numPr.numId.val}']", np.element.nsmap)
        _path = f"w:abstractNum[@w:abstractNumId='{num.abstractNumId.val}']"
        # the numbering styles themselves
        abstract_numbering = np.element.find(_path, np.element.nsmap)
        return abstract_numbering.find(f"w:lvl[@w:ilvl='{p.pPr.numPr.ilvl.val}']", np.element.nsmap)
    return None


def get_paragraph_ind(p: object, doc: object) -> object | None:
    """Get the style according to the hierarchy listed in section 17.3.1.27.

    "pStyle (Referenced Paragraph Style)".

    This formatting is applied at the following location in the style hierarchy:
    * Document defaults
    * Table styles
    * Numbering styles
    * Paragraph styles (this element)
    * Character styles
    * Direct Formatting
    """
    if getattr(p, "pPr", None) is not None and p.pPr.ind is not None:
        return p.pPr.ind

    num_style = get_num_style(p, doc)
    if (
        num_style is not None
        and getattr(num_style, "pPr", None) is not None
        and num_style.pPr is not None
        and num_style.pPr.ind is not None
    ):
        return num_style.pPr.ind

    p_style = get_p_style(p, doc)
    if p_style is not None and p_style.pPr is not None and p_style.pPr.ind is not None:
        return p_style.pPr.ind
    return None
