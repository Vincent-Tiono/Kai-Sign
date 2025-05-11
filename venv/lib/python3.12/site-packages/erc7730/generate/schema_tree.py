from abc import ABC
from typing import assert_never

import eth_abi
from eip712.model.schema import EIP712SchemaField, EIP712Type
from eth_abi.grammar import BasicType, TupleType
from pydantic import Field

from erc7730.common.abi import ABIDataType
from erc7730.model.abi import Component, Function, InputOutput
from erc7730.model.base import Model
from erc7730.model.context import EIP712Schema


class SchemaNode(Model, ABC):
    """Represents a node in the tree defined by a function ABI / EIP-712 schema."""


class SchemaStruct(SchemaNode):
    """Schema node representing a function or a tuple."""

    components: dict[str, "SchemaTree"] = Field(title="Struct components")


class SchemaArray(SchemaNode):
    """Schema node representing an array."""

    component: "SchemaTree" = Field(title="Array element type")


class SchemaLeaf(SchemaNode):
    """Schema node representing a scalar type."""

    data_type: ABIDataType = Field(title="Data type")


SchemaTree = SchemaStruct | SchemaArray | SchemaLeaf


def eip712_schema_to_tree(schema: EIP712Schema) -> SchemaTree:
    """
    Convert an EIP-712 schema to a schema tree.

    A schema tree is a tree representation of the EIP-712 schema, enriched with some metadata to ease crafting
    paths to access values in the message.

    :param schema: EIP-712 schema
    :return: Schema tree
    """
    if (primary_type_fields := schema.types.get(schema.primaryType)) is None:
        raise ValueError("Primary type not found in schema types")

    return _eip712_struct_type_to_tree(fields=primary_type_fields, types=schema.types)


def _eip712_struct_type_to_tree(
    fields: list[EIP712SchemaField], types: dict[EIP712Type, list[EIP712SchemaField]]
) -> SchemaTree:
    """
    Convert a complex EIP-712 type to a schema tree node (can be the primary type directly).

    :param fields: type fields
    :param types: all schema types
    :return: Schema tree
    """
    return SchemaStruct(components={field.name: _eip712_field_to_tree(field, types) for field in fields})


def _eip712_field_to_tree(field: EIP712SchemaField, types: dict[EIP712Type, list[EIP712SchemaField]]) -> SchemaTree:
    """
    Convert an EIP-712 type to a schema tree node.

    :param field: ABI element (can be a single component, or a function input)
    :param types: all schema types
    :return: Schema tree
    """
    match eth_abi.grammar.parse(field.type):
        case TupleType():
            return _eip712_struct_type_to_tree(types[field.type], types)

        case BasicType() as tp:
            if tp.is_array:
                match tp.base:
                    case "tuple" | "struct":
                        component = _eip712_struct_type_to_tree(types[field.type], types)
                    case _:
                        component = _eip712_field_to_tree(
                            field=field.model_copy(update={"type": tp.item_type.to_type_str()}), types=types
                        )

                return SchemaArray(component=component)

            match tp.base:
                case "tuple" | "struct":
                    return _eip712_struct_type_to_tree(types[field.type], types)
                case base if base in set(ABIDataType):
                    type_family = ABIDataType(base)
                case base_type:
                    if (base_type_fields := types.get(base_type)) is None:
                        raise Exception(f"Unexpected EIP-712 type: {base_type}")
                    return _eip712_struct_type_to_tree(base_type_fields, types)

            return SchemaLeaf(data_type=type_family)

        case unknown:
            raise Exception(f"Unexpected EIP-712 type: {type(unknown)}")


def abi_function_to_tree(function: Function) -> SchemaTree:
    """
    Convert a function ABI to a schema tree.

    A schema tree is a tree representation of the ABI of a function inputs, enriched with some metadata to ease
    crafting paths to access values in the serialized calldata.

    :param function: function ABI
    :return: Schema tree
    """
    return _abi_struct_component_to_tree(function)


def _abi_struct_component_to_tree(inp: Function | InputOutput | Component) -> SchemaTree:
    """
    Convert a struct-like ABI component to a schema tree node (can be the top level function directly).

    :param inp: ABI element
    :return: Schema tree
    """

    # get inputs/components list based on argument type
    input_components: list[InputOutput | Component] = []
    match inp:
        case Function(inputs=inputs):
            if inputs is not None:
                input_components.extend(inputs)
        case InputOutput(components=inp_components):
            if inp_components is not None:
                input_components.extend(inp_components)
        case Component(components=inp_components):
            if inp_components is not None:
                input_components.extend(inp_components)
        case list() as eip712_fields:
            input_components.extend(eip712_fields)
        case _:
            assert_never(inp)

    return SchemaStruct(
        components={component.name: _abi_component_to_tree(component) for component in input_components}
    )


def _abi_component_to_tree(inp: InputOutput | Component) -> SchemaTree:
    """
    Convert an ABI component to a schema tree node.

    :param inp: ABI element (can be a single component, or a function input)
    :return: Schema tree
    """
    match eth_abi.grammar.parse(inp.type):
        case TupleType():
            return _abi_struct_component_to_tree(inp)

        case BasicType() as tp:
            if tp.is_array:
                match tp.base:
                    case "tuple" | "struct":
                        component = _abi_struct_component_to_tree(inp)
                    case _:
                        component = _abi_component_to_tree(inp.model_copy(update={"type": tp.item_type.to_type_str()}))

                return SchemaArray(component=component)

            match tp.base:
                case "tuple" | "struct":
                    return _abi_struct_component_to_tree(inp)
                case base if base in set(ABIDataType):
                    type_family = ABIDataType(base)
                case unknown:
                    raise Exception(f"Unexpected ABI type: {unknown}")

            return SchemaLeaf(data_type=type_family)

        case unknown:
            raise Exception(f"Unexpected ABI type: {type(unknown)}")
