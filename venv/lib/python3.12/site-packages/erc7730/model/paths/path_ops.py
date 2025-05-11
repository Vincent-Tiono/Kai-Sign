from typing import assert_never

from erc7730.model.paths import (
    ROOT_DATA_PATH,
    ContainerPath,
    DataPath,
    DataPathElement,
    DescriptorPath,
    DescriptorPathElement,
)


def descriptor_path_strip_prefix(path: DescriptorPath, prefix: DescriptorPath) -> DescriptorPath:
    """
    Strip expected prefix from a descriptor path, raising an error if the prefix is not matching.

    :param path: path to strip
    :param prefix: prefix to strip
    :return: path without prefix
    :raises ValueError: if the path does not start with the prefix
    """
    if len(path.elements) < len(prefix.elements):
        raise ValueError(f"Path {path} does not start with prefix {prefix}.")
    for i, element in enumerate(prefix.elements):
        if path.elements[i] != element:
            raise ValueError(f"Path {path} does not start with prefix {prefix}.")
    return DescriptorPath(elements=path.elements[len(prefix.elements) :])


def data_path_strip_prefix(path: DataPath, prefix: DataPath) -> DataPath:
    """
    Strip expected prefix from a data path, raising an error if the prefix is not matching.

    :param path: path to strip
    :param prefix: prefix to strip
    :return: path without prefix
    :raises ValueError: if the path does not start with the prefix
    """
    if path.absolute != prefix.absolute or len(path.elements) < len(prefix.elements):
        raise ValueError(f"Path {path} does not start with prefix {prefix}.")
    for i, element in enumerate(prefix.elements):
        if path.elements[i] != element:
            raise ValueError(f"Path {path} does not start with prefix {prefix}.")
    return DataPath(absolute=path.absolute, elements=path.elements[len(prefix.elements) :])


def descriptor_path_starts_with(path: DescriptorPath, prefix: DescriptorPath) -> bool:
    """
    Check if descriptor path starts with a given prefix.

    :param path: path to inspect
    :param prefix: prefix to check
    :return: True if path starts with prefix
    """
    try:
        descriptor_path_strip_prefix(path, prefix)
        return True
    except ValueError:
        return False


def data_path_starts_with(path: DataPath, prefix: DataPath) -> bool:
    """
    Check if data path starts with a given prefix.

    :param path: path to inspect
    :param prefix: prefix to check
    :return: True if path starts with prefix
    """
    try:
        data_path_strip_prefix(path, prefix)
        return True
    except ValueError:
        return False


def path_starts_with(
    path: DataPath | ContainerPath | DescriptorPath, prefix: DataPath | ContainerPath | DescriptorPath
) -> bool:
    """
    Check if path starts with a given prefix.

    :param path: path to inspect
    :param prefix: prefix to check
    :return: True if path starts with prefix
    """
    match (path, prefix):
        case (ContainerPath(), ContainerPath()):
            return path == prefix
        case (DataPath(), DataPath()):
            return data_path_starts_with(path, prefix)
        case (DescriptorPath(), DescriptorPath()):
            return descriptor_path_starts_with(path, prefix)
        case _:
            return False


def descriptor_path_ends_with(path: DescriptorPath, suffix: DescriptorPathElement) -> bool:
    """
    Check if descriptor path ends with a given element.

    :param path: path to inspect
    :param suffix: suffix to check
    :return: True if path ends with suffix
    """
    return path.elements[-1] == suffix


def data_path_ends_with(path: DataPath, suffix: DataPathElement) -> bool:
    """
    Check if data path ends with a given element.

    :param path: path to inspect
    :param suffix: suffix to check
    :return: True if path ends with suffix
    """
    if not path.elements:
        return False
    return path.elements[-1] == suffix


def data_path_concat(parent: DataPath | None, child: DataPath) -> DataPath:
    """
    Concatenate two data paths.

    :param parent: parent path
    :param child: child path
    :return: concatenated path
    """
    if parent is None or child.absolute:
        return child
    return DataPath(absolute=parent.absolute, elements=[*parent.elements, *child.elements])


def data_or_container_path_concat(parent: DataPath | None, child: DataPath | ContainerPath) -> DataPath | ContainerPath:
    """
    Concatenate a data path with either another data path, or a container path.

    :param parent: parent path
    :param child: child path
    :return: concatenated path
    """
    if parent is None:
        return child
    match child:
        case DataPath() as child:
            return data_path_concat(parent, child)
        case ContainerPath() as child:
            return child
        case _:
            assert_never(child)


def data_path_append(parent: DataPath, child: DataPathElement) -> DataPath:
    """
    Append an element to a data path.

    :param parent: parent path
    :param child: element to append
    :return: concatenated path
    """
    return parent.model_copy(update={"elements": [*parent.elements, child]})


def descriptor_path_append(parent: DescriptorPath, child: DescriptorPathElement) -> DescriptorPath:
    """
    Append an element to a descriptor path.

    :param parent: parent path
    :param child: element to append
    :return: concatenated path
    """
    return parent.model_copy(update={"elements": [*parent.elements, child]})


def to_absolute(path: DataPath | ContainerPath) -> DataPath | ContainerPath:
    """
    Convert a path to an absolute path.

    :param path: data path
    :return: absolute path
    """
    match path:
        case DataPath():
            return data_path_concat(ROOT_DATA_PATH, path)
        case ContainerPath():
            return path
        case _:
            assert_never(path)


def to_relative(path: DataPath | ContainerPath) -> DataPath | ContainerPath:
    """
    Convert a path to a relative path.

    :param path: data path
    :return: absolute path
    """
    match path:
        case DataPath():
            return path.model_copy(update={"absolute": False})
        case ContainerPath():
            return path
        case _:
            assert_never(path)
