"""Coerce Docx Documents to JSON.

Not thread safe! (but could be if build_iterators returned the built iterator
definitions and passed them around...)
"""

from .elements import document
from .types.fragment import documentPart
from .utils.friendly_names import apply_friendly_names
from .utils.set_options import set_options as __set_options__
from .utils.walk import walk as walk

__version__ = "0.1.0"


# --------------------------------------------------
# Main API
# --------------------------------------------------
type Options = dict[str, object]


def simplify(doc: documentPart, options: Options | None = None) -> dict[str, object]:
    """Coerce Docx Documents to JSON."""
    # SET OPTIONS
    _options: Options
    _options = dict(__default_options__, **options) if options else __default_options__
    __set_options__(_options)

    out = document(doc.element).to_json(doc, _options)

    if _options.get("friendly-name", True):
        apply_friendly_names(out)

    return out


# --------------------------------------------------
# Default Options
# --------------------------------------------------
__default_options__: dict[str, str | bool | int | float] = {
    # general
    "friendly-names": True,
    # flattening special content
    "flatten-hyperlink": True,
    "flatten-smartTag": True,
    "flatten-customXml": True,
    "flatten-simpleField": True,
    "merge-consecutive-text": True,
    "flatten-inner-spaces": False,
    # possibly meaningful style:
    "include-paragraph-indent": True,
    "include-paragraph-numbering": True,
    # ignoring invisible things
    "ignore-joiners": True,
    "ignore-left-to-right-mark": False,
    "ignore-right-to-left-mark": False,
    "ignore-empty-table-description": True,
    "ignore-empty-table-caption": True,
    "ignore-empty-paragraphs": True,
    "ignore-empty-text": True,
    "remove-trailing-white-space": True,
    "remove-leading-white-space": True,
    # forms
    "use-checkbox-default": True,
    "greedy-text-input": True,
    "checkbox-as-text": False,
    "dropdown-as-text": False,
    "simplify-dropdown": True,
    "simplify-textinput": True,
    "simplify-checkbox": True,
    "flatten-generic-field": True,
    "trim-dropdown-options": True,
    # special symbols
    "empty-as-text": False,
    "symbol-as-text": True,
    "special-characters-as-text": True,
    "dumb-quotes": True,
    "dumb-hyphens": True,
    "dumb-spaces": True,
}
