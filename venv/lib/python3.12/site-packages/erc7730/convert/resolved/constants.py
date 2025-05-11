from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, assert_never, override

from pydantic import TypeAdapter, ValidationError
from typing_extensions import TypeVar

from erc7730.common.output import OutputAdder
from erc7730.common.properties import get_property
from erc7730.model.input.descriptor import InputERC7730Descriptor
from erc7730.model.input.path import ContainerPathStr, DataPathStr
from erc7730.model.paths import ROOT_DESCRIPTOR_PATH, ArrayElement, ContainerPath, DataPath, DescriptorPath, Field
from erc7730.model.paths.path_ops import descriptor_path_append, to_absolute
from erc7730.model.types import MixedCaseAddress

_T = TypeVar("_T", covariant=True)


class ConstantProvider(ABC):
    """
    Resolver for constants values referenced by descriptor paths.
    """

    @abstractmethod
    def get(self, path: DescriptorPath, out: OutputAdder) -> Any:
        """
        Get the constant for the given path.

        :param path: descriptor path
        :param out: error handler
        :return: constant value, or None if not found
        """
        raise NotImplementedError()

    def resolve(self, value: _T | DescriptorPath, out: OutputAdder) -> _T:
        """
        Resolve the value if it is a descriptor path.

        :param value: descriptor path or actual value
        :param out: error handler
        :return: constant value, or the value itself if not a descriptor path
        """
        return self.get(value, out) if isinstance(value, DescriptorPath) else value

    def resolve_or_none(self, value: _T | DescriptorPath | None, out: OutputAdder) -> _T | None:
        """
        Resolve the optional value if it is a descriptor path.

        :param value: descriptor path, actual value or None
        :param out: error handler
        :return: None, constant value, or the value itself if not a descriptor path
        """
        return None if value is None else self.resolve(value, out)

    def resolve_path(
        self, value: DataPath | ContainerPath | DescriptorPath, out: OutputAdder
    ) -> DataPath | ContainerPath | None:
        """
        Resolve the value as a data/container path.

        :param value: descriptor path or actual data/container path
        :param out: error handler
        :return: resolved data/container path
        """

        def assert_not_address(path: DataPath | ContainerPath) -> bool:
            match path:
                case ContainerPath():
                    return True
                case DataPath():
                    if path.absolute:
                        return True
                    try:
                        TypeAdapter(MixedCaseAddress).validate_strings(str(path))
                        out.error(
                            title="Invalid data path",
                            message=f""""{path}" is invalid, it must contain a data path to the address in the """
                            "transaction data. It seems you are trying to use a constant address value instead, please "
                            "use the adequate parameter to provide a constant value.",
                        )
                        return False
                    except ValidationError:
                        return True
                case _:
                    assert_never(path)

        if isinstance(value, DataPath | ContainerPath):
            if not assert_not_address(value):
                return None
            return value

        resolved_value: Any
        if (resolved_value := self.resolve(value, out)) is None:
            return None

        if not isinstance(resolved_value, str):
            return out.error(
                title="Invalid constant path",
                message=f"Constant path defined at {value} must be a path string, got {type(resolved_value).__name__}.",
            )

        match TypeAdapter(DataPathStr | ContainerPathStr).validate_strings(resolved_value):
            case ContainerPath() as path:
                return path
            case DataPath() as path:
                if not assert_not_address(path):
                    return None
                if not path.absolute:
                    return out.error(
                        title="Invalid data path constant",
                        message=f"Data path defined at {value} must be absolute, please change it to "
                        f"{to_absolute(path)}.",
                    )
                return path
            case _:
                assert_never(resolved_value)

        # noinspection PyUnreachableCode
        return None

    def resolve_path_or_none(
        self, value: DataPath | ContainerPath | DescriptorPath | None, out: OutputAdder
    ) -> DataPath | ContainerPath | None:
        """
        Resolve the value as a data/container path.

        :param value: descriptor path or actual data/container path
        :param out: error handler
        :return: resolved data/container path
        """
        return None if value is None else self.resolve_path(value, out)


class DefaultConstantProvider(ConstantProvider):
    """
    Resolver for constants values from a provided dictionary.
    """

    def __init__(self, descriptor: InputERC7730Descriptor) -> None:
        self.descriptor: InputERC7730Descriptor = descriptor

    @override
    def get(self, path: DescriptorPath, out: OutputAdder) -> Any:
        current_target = self.descriptor
        parent_path = ROOT_DESCRIPTOR_PATH
        current_path = ROOT_DESCRIPTOR_PATH

        for element in path.elements:
            current_path = descriptor_path_append(current_path, element)
            match element:
                case Field(identifier=field):
                    if isinstance(current_target, Sequence):
                        return out.error(
                            title="Invalid constant path",
                            message=f"""Path {current_path} is invalid, {parent_path} is an array.""",
                        )
                    else:
                        try:
                            current_target = get_property(current_target, field)
                        except (AttributeError, KeyError):
                            return out.error(
                                title="Invalid constant path",
                                message=f"""Path {current_path} is invalid, {parent_path} has no "{field}" field.""",
                            )
                case ArrayElement(index=i):
                    if not isinstance(current_target, Sequence):
                        return out.error(
                            title="Invalid constant path",
                            message=f"Path {current_path} is invalid, {parent_path} is not an array.",
                        )
                    if i >= len(current_target):
                        return out.error(
                            title="Invalid constant path",
                            message=f"""Path {current_path} is invalid, index {i} is out of bounds.""",
                        )
                    current_target = current_target[i]
                case _:
                    assert_never(element)
            parent_path = descriptor_path_append(parent_path, element)

        return current_target
