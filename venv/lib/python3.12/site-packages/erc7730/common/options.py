from typing_extensions import TypeVar

_T = TypeVar("_T")


def first_not_none(*args: _T | None) -> _T | None:
    """
    Return the first argument that is not None.

    :param args: sequence of optional values
    :return: first non-None value, or None if there are none
    """
    for arg in args:
        if arg is not None:
            return arg
    return None
