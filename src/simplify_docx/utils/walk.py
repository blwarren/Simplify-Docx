"""A utility function for walking a simplified document."""

from collections.abc import Callable, Sequence
from inspect import signature


def walk(  # noqa: PLR0912
    document: dict[str, object],
    fun: Callable[..., object],
    node_type: str | None = "document",
    no_iter: Sequence[str] | None = None,
    **kwargs: object,
) -> object | None:
    """Walk a document tree and apply a function to matching nodes.

    :param document: Simplified Docx element to walk
    :type document:object
    :param fun: A function to apply at each node in the document. If ``fun``
            takes just one parameter, it is passed the current element,
            otherwise it is passed the current element, the containing element,
            and the position of the current element within the containing
            element which is an integer in the current element is contained in
            an array of ``VALUE``s and ``None`` if the current element is the
            parent's ``VALUE``.
    :type fun: Callable
    :param node_type: The node ``TYPE``s at which to apply the function ``fun``
    :type node_type: str
    :param no_iter: Optional. A list of elmenet ``TYPE``s into which the walker
            should refrain from walking into. For example, setting
            ``no_iter=["paragraph"]`` would prevent the walker from traversing
            children (``VALUE``s) paragraph nodes.
    :type no_iter: Sequence[str]

    :return: ``None``
    :return type: None
    """
    if "TYPE" in kwargs:
        node_type = kwargs.pop("TYPE")
    if kwargs:
        msg = f"Unexpected keyword arguments: {', '.join(sorted(kwargs))}"
        raise TypeError(msg)

    _sig = signature(fun)
    _params = _sig.parameters

    has_multiple_parameters = len(_params) > 1 or any(
        param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL) for param in _params.values()
    )

    stack = [(document, None)]
    while True:
        try:
            current, index = stack.pop()
        except IndexError:
            break

        if index is None:
            # CURRENT IS AN OBJECT:

            # APPLY THE FUNCTION
            if node_type is None or current.get("TYPE", None) == node_type:
                if has_multiple_parameters:
                    try:
                        parent, parent_index = stack[-1]
                    except IndexError:
                        out = fun(current, None, None)
                    else:
                        out = fun(current, parent, parent_index - 1)
                else:
                    out = fun(current)
                if out is not None:
                    return out

            val = current.get("VALUE", None)
            if isinstance(val, dict) and current.get("TYPE", None):
                # CHILD IS AN ELEMENT TO BE WAKLED
                stack.append((val, None))
                continue

            if (
                isinstance(val, list)
                and val
                and val[0].get("TYPE", None)
                and (no_iter is None or current["TYPE"] not in no_iter)
            ):
                # CHILD IS A LIST OF ELEMENTS
                stack.append((val, 0))
                continue

        else:
            # CURRENT IS A LIST
            try:
                nxt = current[index]
            except IndexError:
                pass
            else:
                stack.append((current, index + 1))
                stack.append((nxt, None))
                del nxt

        del current, index
