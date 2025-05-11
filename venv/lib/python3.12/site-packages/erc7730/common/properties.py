from typing import Any


def has_any_property(target: Any, *names: str) -> bool:
    """
    Check if the target has a property with any of the given names.

    :param target: object of dict like
    :param names: attribute names
    :return: true if the target has the property
    """
    return any(has_property(target, n) for n in names)


def has_property(target: Any, name: str) -> bool:
    """
    Check if the target has a property with the given name.

    :param target: object of dict like
    :param name: attribute name
    :return: true if the target has the property
    """
    if isinstance(target, dict):
        return name in target
    return hasattr(target, name)


def get_property(target: Any, name: str) -> Any:
    """
    Get the property with the given name on target object.

    :param target: object of dict like
    :param name: attribute name
    :return: value for property on target object
    """
    if isinstance(target, dict):
        return target[name]
    return getattr(target, name)
