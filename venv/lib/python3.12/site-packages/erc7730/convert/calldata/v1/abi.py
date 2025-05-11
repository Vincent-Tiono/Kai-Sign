"""
Conversion of a function ABI to an ABI tree.

An ABI tree is a tree representation of the ABI of a function inputs, enriched with some metadata to ease crafting
paths to access values in the serialized calldata.
"""

from abc import ABC, abstractmethod
from typing import Annotated, Literal, assert_never, override

import eth_abi
from eth_abi.grammar import BasicType, TupleType
from pydantic import Field

from erc7730.model.abi import Component, Function, InputOutput
from erc7730.model.base import Model
from erc7730.model.calldata.v1.value import (
    CalldataDescriptorTypeFamily,
)


class ABINode(Model, ABC):
    """Represents a node in the tree defined by a function ABI."""

    @property
    @abstractmethod
    def is_dynamic(self) -> bool:
        raise NotImplementedError()

    @property
    @abstractmethod
    def size(self) -> int:
        raise NotImplementedError()


class ABILeafNode(ABINode, ABC):
    """Represents a leaf node in the tree defined by a function ABI."""

    type_family: CalldataDescriptorTypeFamily = Field(title="Data type family")
    type_size: int | None = Field(default=None, title="Data type size (in bytes)")


class ABIStruct(ABINode):
    """ABI node representing a function or a tuple."""

    type: Literal["struct"] = Field(default="struct", title="ABI tree node type")
    components: dict[str, "ABITree"] = Field(title="Struct components")
    offsets: dict[str, int] = Field(title="Struct components offsets")

    @override
    @property
    def is_dynamic(self) -> bool:
        return any(comp.is_dynamic for comp in self.components.values())

    @override
    @property
    def size(self) -> int:
        return 1 if self.is_dynamic else sum(comp.size for comp in self.components.values())


class ABIStaticArray(ABINode):
    """ABI node representing an array with static size."""

    type: Literal["static_array"] = Field(default="static_array", title="ABI tree node type")
    dimension: int = Field(title="Array dimension", ge=0)
    component: "ABITree" = Field(title="Array element type")

    @override
    @property
    def is_dynamic(self) -> bool:
        return self.component.is_dynamic

    @override
    @property
    def size(self) -> int:
        return 1 if self.is_dynamic else self.dimension * self.component.size


class ABIDynamicArray(ABINode):
    """ABI node representing an array with dynamic size."""

    type: Literal["dynamic_array"] = Field(default="dynamic_array", title="ABI tree node type")
    component: "ABITree" = Field(title="Array element type")

    @override
    @property
    def is_dynamic(self) -> bool:
        return True

    @override
    @property
    def size(self) -> int:
        return 1


class ABIStaticLeaf(ABILeafNode):
    """ABI node representing a scalar type with static size."""

    type: Literal["static_leaf"] = Field(default="static_leaf", title="ABI tree node type")

    @override
    @property
    def is_dynamic(self) -> bool:
        return False

    @override
    @property
    def size(self) -> int:
        return 1


class ABIDynamicLeaf(ABILeafNode):
    """ABI node representing a scalar type with dynamic size."""

    type: Literal["dynamic_leaf"] = Field(default="dynamic_leaf", title="ABI tree node type")

    @override
    @property
    def is_dynamic(self) -> bool:
        return True

    @override
    @property
    def size(self) -> int:
        return 1


ABITree = Annotated[
    ABIStruct | ABIStaticArray | ABIDynamicArray | ABIStaticLeaf | ABIDynamicLeaf, Field(discriminator="type")
]


def function_to_abi_tree(function: Function) -> ABITree:
    """
    Convert a function ABI to an ABI tree.

    An ABI tree is a tree representation of the ABI of a function inputs, enriched with some metadata to ease crafting
    paths to access values in the serialized calldata.

    @param function: function ABI
    @return:
    """
    return _struct_component_to_abi_tree(function)


def _component_to_abi_tree(inp: InputOutput | Component) -> ABITree:
    """
    Convert an ABI component to an ABI tree node.

    @param inp: ABI element (can be a single component, or a function input)
    @return: ABI tree
    """
    match eth_abi.grammar.parse(inp.type):
        case TupleType():
            return _struct_component_to_abi_tree(inp)

        case BasicType() as tp:
            if tp.is_array:
                match tp.base:
                    case "tuple" | "struct":
                        component = _struct_component_to_abi_tree(inp)
                    case _:
                        component = _component_to_abi_tree(inp.model_copy(update={"type": tp.item_type.to_type_str()}))

                if len(dimension := tp.arrlist[-1]) == 0:
                    return ABIDynamicArray(component=component)
                else:
                    return ABIStaticArray(component=component, dimension=dimension[0])

            match tp.base:
                case "tuple" | "struct":
                    return _struct_component_to_abi_tree(inp)
                case "int":
                    type_family = CalldataDescriptorTypeFamily.INT
                    type_size = (tp.sub or 256) // 8
                case "uint":
                    type_family = CalldataDescriptorTypeFamily.UINT
                    type_size = (tp.sub or 256) // 8
                case "address":
                    type_family = CalldataDescriptorTypeFamily.ADDRESS
                    type_size = (tp.sub or 160) // 8
                case "bool":
                    type_family = CalldataDescriptorTypeFamily.BOOL
                    type_size = (tp.sub or 8) // 8
                case "bytes":
                    type_family = CalldataDescriptorTypeFamily.BYTES
                    type_size = tp.sub // 8 if tp.sub else None
                case "string":
                    type_family = CalldataDescriptorTypeFamily.STRING
                    type_size = tp.sub // 8 if tp.sub else None
                case "fixed" | "ufixed":
                    raise NotImplementedError("Fixed precision numbers are not supported by v1 of calldata descriptor")
                case unknown:
                    raise Exception(f"Unexpected ABI type: {unknown}")

            if tp.is_dynamic:
                return ABIDynamicLeaf(type_family=type_family, type_size=type_size)
            else:
                return ABIStaticLeaf(type_family=type_family, type_size=type_size)

        case unknown:
            raise Exception(f"Unexpected ABI type: {type(unknown)}")


def _struct_component_to_abi_tree(inp: Function | InputOutput | Component) -> ABITree:
    """
    Convert a struct-like ABI component to an ABI tree node (can be the top level function directly).

    @param inp: ABI element
    @return: ABI tree
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
        case _:
            assert_never(inp)

    # recurse and compute field offsets
    components: dict[str, ABITree] = {}
    offsets: dict[str, int] = {}
    offset = 0
    for _, component in enumerate(input_components):
        node = _component_to_abi_tree(component)
        components[component.name] = node
        offsets[component.name] = offset
        offset += node.size

    return ABIStruct(components=components, offsets=offsets)
