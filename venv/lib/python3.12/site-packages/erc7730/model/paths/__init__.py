from enum import StrEnum, auto
from typing import Annotated, Literal, Self, override

from pydantic import Field as PydanticField
from pydantic import (
    model_validator,
)

from erc7730.model.base import Model

ArrayIndex = Annotated[
    int,
    PydanticField(
        title="Array index",
        description="Index of an element in an array. An index can be negative to count from the end of the array.",
        ge=-32767,  # TODO to be refined
        le=32768,  # TODO to be refined
    ),
]


class Field(Model):
    """A path component designating a field in a structured data schema."""

    type: Literal["field"] = PydanticField(
        "field",
        title="Path Component Type",
        description="The path component type identifier (discriminator for path components discriminated union).",
    )

    identifier: str = PydanticField(
        title="Field Identifier",
        description="The identifier of the referenced field in the structured data schema.",
        pattern=r"^[a-zA-Z0-9_]+$",
    )

    @override
    def __str__(self) -> str:
        return self.identifier


class ArrayElement(Model):
    """A path component designating a single element of an array."""

    type: Literal["array_element"] = PydanticField(
        "array_element",
        title="Path Component Type",
        description="The path component type identifier (discriminator for path components discriminated union).",
    )

    index: ArrayIndex = PydanticField(
        title="Array Element",
        description="The index of the element in the array. It can be negative to count from the end of the array.",
    )

    @override
    def __str__(self) -> str:
        return f"[{self.index}]"


class ArraySlice(Model):
    """A path component designating an element range of an array (in which case, the path targets multiple values)."""

    type: Literal["array_slice"] = PydanticField(
        "array_slice",
        title="Path Component Type",
        description="The path component type identifier (discriminator for path components discriminated union).",
    )

    start: ArrayIndex | None = PydanticField(
        default=None,
        title="Slice Start Index",
        description="The start index of the slice (inclusive). Must be lower than the end index. If unset, slice "
        "starts from the beginning of the array.",
    )

    end: ArrayIndex | None = PydanticField(
        default=None,
        title="Slice End Index",
        description="The end index of the slice (exclusive). Must be greater than the start index. If unset, slice "
        "ends at the end of the array.",
    )

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if (start := self.start) is None or (end := self.end) is None:
            return self
        if 0 <= end <= start or end <= start < 0:
            raise ValueError("Array slice start index must be strictly lower than end index.")
        return self

    def __str__(self) -> str:
        return f"[{'' if self.start is None else self.start}:{'' if self.end is None else self.end}]"


class Array(Model):
    """A path component designating all elements of an array (in which case, the path targets multiple values)."""

    type: Literal["array"] = PydanticField(
        "array",
        title="Path Component Type",
        description="The path component type identifier (discriminator for path components discriminated union).",
    )

    @override
    def __str__(self) -> str:
        return "[]"


class ContainerField(StrEnum):
    """
    Path applying to the container of the structured data to be signed.

    Such paths are prefixed with "@".
    """

    VALUE = auto()
    """The native currency value of the transaction containing the structured data."""

    FROM = auto()
    """The address of the sender of the transaction / signer of the message."""

    TO = auto()
    """The destination address of the containing transaction, ie the target smart contract address."""


DataPathElement = Annotated[
    Field | ArrayElement | ArraySlice | Array,
    PydanticField(
        title="Data Path Element",
        description="An element of a data path, applying to the structured data schema (ABI path for contracts, path"
        "in the message types itself for EIP-712)",
        discriminator="type",
    ),
]

DescriptorPathElement = Annotated[
    Field | ArrayElement,
    PydanticField(
        title="Descriptor Path Element",
        description="An element of a descriptor path, applying to the current file describing the structured data"
        "formatting, after merging with includes.",
        discriminator="type",
    ),
]


class ContainerPath(Model):
    """
    Path applying to the container of the structured data to be signed.

    Such paths are prefixed with "@".
    """

    type: Literal["container"] = PydanticField(
        "container",
        title="Path Type",
        description="The path type identifier (discriminator for paths discriminated union).",
    )

    field: ContainerField = PydanticField(
        title="Container field",
        description="The referenced field in the container, only some well-known values are allowed.",
    )

    @override
    def __str__(self) -> str:
        return f"@.{self.field}"


class DataPath(Model):
    """
    Path applying to the structured data schema (ABI path for contracts, path in the message types itself for
    EIP-712).

    A data path can reference multiple values if it contains array elements or slices.

    Such paths are prefixed with "#".
    """

    type: Literal["data"] = PydanticField(
        "data", title="Path Type", description="The path type identifier (discriminator for paths discriminated union)."
    )

    absolute: bool = PydanticField(
        title="Absolute",
        description="Whether the path is absolute (starting from the structured data root) or relative (starting from"
        "the current field).",
    )

    elements: list[DataPathElement] = PydanticField(
        title="Elements",
        description="The path elements, as a list of references to be interpreted left to right from the structured"
        "data root to reach the referenced value(s).",
    )

    @override
    def __str__(self) -> str:
        return f"{'#.' if self.absolute else ''}{'.'.join(str(e) for e in self.elements)}"

    @override
    def __hash__(self) -> int:
        return hash(str(self))


class DescriptorPath(Model):
    """
    Path applying to the current file describing the structured data formatting, after merging with includes.

    A descriptor path can only reference a single value in the document.

    Such paths are prefixed with "$".
    """

    type: Literal["descriptor"] = PydanticField(
        "descriptor",
        title="Path Type",
        description="The path type identifier (discriminator for paths discriminated union).",
    )

    elements: list[DescriptorPathElement] = PydanticField(
        title="Elements",
        description="The path elements, as a list of references to be interpreted left to right from the current file"
        "root to reach the referenced value.",
    )

    @override
    def __str__(self) -> str:
        return f"$.{'.'.join(str(e) for e in self.elements)}"

    @override
    def __hash__(self) -> int:
        return hash(str(self))


ROOT_DATA_PATH = DataPath(absolute=True, elements=[])
ROOT_DESCRIPTOR_PATH = DescriptorPath(elements=[])
