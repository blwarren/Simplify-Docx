"""utility functions for getting attributes."""

import re
from collections import namedtuple
from collections.abc import Sequence

from ..types import xmlFragment

# -------------------------------------------------------
# TYPINGS
# -------------------------------------------------------

Tag: tuple[str | None, str | None, str, str] = namedtuple("tag", ("namespace", "ns", "tag", "nstag"))


# -------------------------------------------------------
# ATTRIBUTE HANDLING
# -------------------------------------------------------


def get_attrs(el: xmlFragment, attrs: Sequence[str]) -> dict[str, str]:
    """Extract Named attributes from an lxml element."""
    out: dict[str, str] = {}
    for attr in attrs:
        if attr in el.attrib:
            out[attr] = el.attrib[attr]
    return out


def get_tag(element: xmlFragment, nsdict: dict[str, str] | None = None) -> Tag:
    """Extract parts of the tag (this is essentially the reverse of `qn()`)."""
    ns_names: dict[str, str]
    ns_names = NS_NAMES if nsdict is None else dict(zip(nsdict.values(), nsdict.keys(), strict=False))
    match = _re_tag.match(element.tag)
    if match is None:
        return Tag(None, None, element.tag, element.tag)
    groups: Sequence[str] = match.groups()
    namespace: str = groups[0]
    tag: str = groups[1]
    if namespace in ns_names:
        ns: str = ns_names[namespace]
        return Tag(namespace, ns, tag, f"{ns}:{tag}")
    return Tag(namespace, None, tag, element.tag)


# -------------------------------------------------------
# CONSTNATS
# -------------------------------------------------------

# could have used elem.xpath('local-name()') and elem.prefix instead...
_re_tag = re.compile(r"^(?:\{([^]]+)\})?(\w+)$")

NS_SCHEMA = {
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w10": "urn:schemas-microsoft-com:office:word",
    "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "aink": "http://schemas.microsoft.com/office/drawing/2016/ink",
    "cx1": "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex",
    "cx2": "http://schemas.microsoft.com/office/drawing/2015/10/21/chartex",
    "cx3": "http://schemas.microsoft.com/office/drawing/2016/5/9/chartex",
    "cx4": "http://schemas.microsoft.com/office/drawing/2016/5/10/chartex",
    "cx5": "http://schemas.microsoft.com/office/drawing/2016/5/11/chartex",
    "cx6": "http://schemas.microsoft.com/office/drawing/2016/5/12/chartex",
    "cx7": "http://schemas.microsoft.com/office/drawing/2016/5/13/chartex",
    "cx8": "http://schemas.microsoft.com/office/drawing/2016/5/14/chartex",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "am3d": "http://schemas.microsoft.com/office/drawing/2017/model3d",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "o": "urn:schemas-microsoft-com:office:office",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "v": "urn:schemas-microsoft-com:vml",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
}

NS_NAMES: dict[str, str] = dict(zip(NS_SCHEMA.values(), NS_SCHEMA.keys(), strict=False))
