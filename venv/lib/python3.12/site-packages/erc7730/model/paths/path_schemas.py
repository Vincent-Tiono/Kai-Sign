from dataclasses import dataclass
from typing import assert_never

from eip712.model.schema import EIP712SchemaField

from erc7730.model.abi import Component, Function, InputOutput
from erc7730.model.context import EIP712Schema
from erc7730.model.paths import (
    ROOT_DATA_PATH,
    Array,
    ArrayElement,
    ArraySlice,
    ContainerPath,
    DataPath,
    DataPathElement,
    Field,
)
from erc7730.model.paths.path_ops import data_path_append
from erc7730.model.resolved.display import (
    ResolvedAddressNameParameters,
    ResolvedCallDataParameters,
    ResolvedDateParameters,
    ResolvedEnumParameters,
    ResolvedField,
    ResolvedFieldDescription,
    ResolvedFormat,
    ResolvedNestedFields,
    ResolvedNftNameParameters,
    ResolvedTokenAmountParameters,
    ResolvedUnitParameters,
    ResolvedValue,
    ResolvedValueConstant,
    ResolvedValuePath,
)
from erc7730.model.resolved.path import ResolvedPath


@dataclass(kw_only=True, frozen=True)
class FormatPaths:
    data_paths: set[DataPath]  # References to values in the serialized data
    container_paths: set[ContainerPath]  # References to values in the container


def compute_eip712_schema_paths(schema: EIP712Schema) -> set[DataPath]:
    """
    Compute the sets of valid schema paths for an EIP-712 schema.

    :param schema: EIP-712 schema
    :return: valid schema paths
    """

    if (primary_type := schema.types.get(schema.primaryType)) is None:
        raise ValueError(f"Invalid schema: primaryType {schema.primaryType} not in types")

    paths: set[DataPath] = set()

    def append_paths(path: DataPath, current_type: list[EIP712SchemaField]) -> None:
        for field in current_type:
            if len(field.name) == 0:
                continue  # skip unnamed parameters

            sub_path = data_path_append(path, Field(identifier=field.name))

            field_base_type = field.type.rstrip("[]")

            if field_base_type in {"bytes"}:
                paths.add(data_path_append(sub_path, Array()))

            if field_base_type != field.type:
                sub_path = data_path_append(sub_path, Array())
                paths.add(sub_path)

            if (target_type := schema.types.get(field_base_type)) is not None:
                append_paths(sub_path, target_type)
            else:
                paths.add(sub_path)

    append_paths(ROOT_DATA_PATH, primary_type)

    return paths


def compute_abi_schema_paths(abi: Function) -> set[DataPath]:
    """
    Compute the sets of valid schema paths for an ABI function.

    :param abi: Solidity ABI function
    :return: valid schema paths
    """
    paths: set[DataPath] = set()

    def append_paths(path: DataPath, params: list[InputOutput] | list[Component] | None) -> None:
        if not params:
            return None
        for param in params:
            if len(param.name) == 0:
                continue  # skip unnamed parameters

            sub_path = data_path_append(path, Field(identifier=param.name))

            param_base_type = param.type.rstrip("[]")

            if param_base_type in {"bytes"}:
                paths.add(data_path_append(sub_path, Array()))

            if param_base_type != param.type:
                sub_path = data_path_append(sub_path, Array())
                paths.add(sub_path)

            if param.components:
                append_paths(sub_path, param.components)  # type: ignore
            else:
                paths.add(sub_path)

    append_paths(ROOT_DATA_PATH, abi.inputs)

    return paths


def compute_format_schema_paths(format: ResolvedFormat) -> FormatPaths:
    """
    Compute the sets of schema paths referred in an ERC7730 Format section.

    :param format: resolved $.display.format section
    :return: schema paths used by field formats
    """
    data_paths: set[DataPath] = set()  # references to values in the serialized data
    container_paths: set[ContainerPath] = set()  # references to values in the container

    if format.fields is not None:

        def add_path(path: ResolvedPath | None) -> None:
            match path:
                case None:
                    pass
                case ContainerPath():
                    container_paths.add(path)
                case DataPath():
                    data_paths.add(data_path_to_schema_path(path))
                case _:
                    assert_never(path)

        def add_value(value: ResolvedValue | None) -> None:
            match value:
                case None:
                    pass
                case ResolvedValueConstant():
                    pass
                case ResolvedValuePath(path=path):
                    add_path(path)
                case _:
                    assert_never(value)

        def append_paths(field: ResolvedField) -> None:
            add_value(field.value)
            match field:
                case ResolvedFieldDescription():
                    match field.params:
                        case None:
                            pass
                        case ResolvedAddressNameParameters():
                            pass
                        case ResolvedCallDataParameters(callee=callee):
                            add_value(callee)
                        case ResolvedTokenAmountParameters(token=token):
                            add_value(token)
                        case ResolvedNftNameParameters(collection=collection):
                            add_value(collection)
                        case ResolvedDateParameters():
                            pass
                        case ResolvedUnitParameters():
                            pass
                        case ResolvedEnumParameters():
                            pass
                        case _:
                            assert_never(field.params)
                case ResolvedNestedFields():
                    for nested_field in field.fields:
                        append_paths(nested_field)
                case _:
                    assert_never(field)

        for field in format.fields:
            append_paths(field)

    return FormatPaths(data_paths=data_paths, container_paths=container_paths)


def data_path_to_schema_path(path: DataPath) -> DataPath:
    """
    Convert a data path to a schema path.

    Example: #.foo.[].[-2].bar.[1:5] -> #.foo.[].[].bar

    :param path: data path
    :return: schema path
    """

    def to_schema(element: DataPathElement) -> DataPathElement | None:
        match element:
            case Field() as f:
                return f
            case Array() | ArrayElement():
                return Array()
            # TODO: Spec also allows slicing on array type, but for now it is only used on primitive types
            case ArraySlice():
                return None
            case _:
                assert_never(element)

    return path.model_copy(update={"elements": [to_schema(e) for e in path.elements if to_schema(e) is not None]})
