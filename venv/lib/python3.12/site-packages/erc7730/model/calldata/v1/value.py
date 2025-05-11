"""
Data model for calldata descriptor references to values (a.k.a., binary paths).

These model classes represent the exact same data fields that are serialized into TLV structs.
See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol
"""

from enum import IntEnum
from typing import Annotated, Literal

from pydantic import Discriminator, Field

from erc7730.common.pydantic import pydantic_enum_by_name
from erc7730.model.base import Model
from erc7730.model.calldata.v1.struct import (
    CalldataDescriptorStructV1,
)
from erc7730.model.resolved.path import ResolvedPath
from erc7730.model.types import HexStr, ScalarType


@pydantic_enum_by_name
class CalldataDescriptorPathElementType(IntEnum):
    """Type of path element."""

    TUPLE = 0x01
    """move by {value} slots from current slot"""

    ARRAY = 0x02
    """current slot is array length, added to offset if negative. multiple by item_size and move by result slots"""

    REF = 0x03
    """read value of current slot. apply read value as offset from current slot"""

    LEAF = 0x04
    """current slot is a leaf type, specifying the type of path end"""

    SLICE = 0x05
    """specify slicing to apply to final leaf value as (start, end)"""


@pydantic_enum_by_name
class CalldataDescriptorPathLeafType(IntEnum):
    """Type of path leaf element."""

    ARRAY_LEAF = 0x01
    """final offset is start of array encoding"""

    TUPLE_LEAF = 0x02
    """final offset is start of tuple encoding"""

    STATIC_LEAF = 0x03
    """final offset contains static encoded value (typ data on 32 bytes)"""

    DYNAMIC_LEAF = 0x04
    """final offset contains dynamic encoded value (typ length + data)"""


@pydantic_enum_by_name
class CalldataDescriptorTypeFamily(IntEnum):
    """Type family of a value."""

    UINT = 0x01
    INT = 0x02
    UFIXED = 0x03
    FIXED = 0x04
    ADDRESS = 0x05
    BOOL = 0x06
    BYTES = 0x07
    STRING = 0x08


@pydantic_enum_by_name
class CalldataDescriptorContainerPathValueV1(IntEnum):
    """Type of container paths."""

    FROM = 0x0
    TO = 0x1
    VALUE = 0x2


class CalldataDescriptorPathElementBaseV1(Model):
    """Descriptor for the PATH_ELEMENT payload."""


class CalldataDescriptorPathElementTupleV1(CalldataDescriptorPathElementBaseV1):
    """Descriptor for the PATH_ELEMENT struct of type TUPLE."""

    type: Literal["TUPLE"] = Field(
        default="TUPLE",
        title="Parameter type",
        description="Type of the parameter",
    )

    offset: int = Field(
        title="Index",
        description="Move by {value} slots from current slot",
    )


class CalldataDescriptorPathElementArrayV1(CalldataDescriptorPathElementBaseV1):
    """Descriptor for the PATH_ELEMENT struct of type ARRAY."""

    type: Literal["ARRAY"] = Field(
        default="ARRAY",
        title="Parameter type",
        description="Type of the parameter",
    )

    weight: int = Field(
        title="Item size",
        description="Size of each array element in chunks",
    )

    start: int | None = Field(
        title="Start",
        description="Start offset in array (inclusive). If not provided, lower bound is array start.",
    )

    end: int | None = Field(
        title="End",
        description="End offset in array (exclusive). If not provided, upper bound is array end.",
    )


class CalldataDescriptorPathElementRefV1(CalldataDescriptorPathElementBaseV1):
    """Descriptor for the PATH_ELEMENT struct of type REF."""

    type: Literal["REF"] = Field(
        default="REF",
        title="Parameter type",
        description="Type of the parameter",
    )


class CalldataDescriptorPathElementLeafV1(CalldataDescriptorPathElementBaseV1):
    """Descriptor for the PATH_ELEMENT struct of type LEAF."""

    type: Literal["LEAF"] = Field(
        default="LEAF",
        title="Parameter type",
        description="Type of the parameter",
    )

    leaf_type: CalldataDescriptorPathLeafType = Field(
        title="Leaf type",
        description="Type of the leaf element",
    )


class CalldataDescriptorPathElementSliceV1(CalldataDescriptorPathElementBaseV1):
    """Descriptor for the PATH_ELEMENT struct of type SLICE."""

    type: Literal["SLICE"] = Field(
        default="SLICE",
        title="Parameter type",
        description="Type of the parameter",
    )

    start: int | None = Field(
        title="Start",
        description="Slice start index (inclusive, unset = start of data)",
    )

    end: int | None = Field(
        title="End",
        description="Slice end index (inclusive, unset = end of data)",
    )


CalldataDescriptorPathElementV1 = Annotated[
    CalldataDescriptorPathElementTupleV1
    | CalldataDescriptorPathElementArrayV1
    | CalldataDescriptorPathElementRefV1
    | CalldataDescriptorPathElementLeafV1
    | CalldataDescriptorPathElementSliceV1,
    Field(
        title="Path element",
        description="Data path element to reach the target value in the serialized transaction",
        discriminator="type",
    ),
]


class CalldataDescriptorContainerPathV1(CalldataDescriptorStructV1):
    """Descriptor for the CONTAINER_PATH struct."""

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the CONTAINER_PATH struct",
    )

    type: Literal["CONTAINER"] = Field(
        default="CONTAINER",
        title="Path type",
        description="Type of the path",
    )

    value: CalldataDescriptorContainerPathValueV1 = Field(title="Value", description="Container field")


class CalldataDescriptorDataPathV1(CalldataDescriptorStructV1):
    """Descriptor for the DATA_PATH struct."""

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the VALUE struct",
    )

    type: Literal["DATA"] = Field(
        default="DATA",
        title="Path type",
        description="Type of the path",
    )

    elements: list[CalldataDescriptorPathElementV1] = Field(
        title="Elements",
        description="Path element to reach the target value",
        min_length=1,
        max_length=256,  # TODO to be refined
    )


CalldataDescriptorPathV1 = Annotated[
    CalldataDescriptorContainerPathV1 | CalldataDescriptorDataPathV1,
    Field(
        title="Path",
        description="Data or container path to reach the target value in the serialized transaction",
        discriminator="type",
    ),
]


class CalldataDescriptorValueBaseV1(CalldataDescriptorStructV1):
    """Descriptor for the VALUE struct."""

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the VALUE struct",
    )

    type_family: CalldataDescriptorTypeFamily = Field(
        title="Type family",
        description="Type family of the value",
    )

    type_size: int | None = Field(
        default=None, title="Type size", description="Size of the type (in bytes)", ge=0, le=255
    )


class CalldataDescriptorValuePathV1(CalldataDescriptorValueBaseV1):
    """
    A path to the field in the structured data. The path is a JSON path expression that can be used to extract the
    field value from the structured data.
    """

    type: Literal["path"] = Field(
        default="path",
        title="Value Type",
        description="The value type identifier (discriminator for values discriminated union).",
    )

    abi_path: ResolvedPath | None = Field(
        default=None,
        title="Path (source descriptor)",
        description="Path to reach the target value in the container or serialized transaction",
    )

    binary_path: CalldataDescriptorPathV1 = Field(
        title="Path (generic parser protocol)",
        description="Path to reach the target value in the container or serialized transaction",
    )


class CalldataDescriptorValueConstantV1(CalldataDescriptorValueBaseV1):
    """
    A constant value.
    """

    type: Literal["constant"] = Field(
        default="constant",
        title="Value Type",
        description="The value type identifier (discriminator for values discriminated union).",
    )

    value: ScalarType = Field(
        title="Value",
        description="The constant value.",
    )

    raw: HexStr = Field(
        title="Raw Value",
        description="The constant value, serialized and hex encoded.",
    )


CalldataDescriptorValueV1 = Annotated[
    CalldataDescriptorValuePathV1 | CalldataDescriptorValueConstantV1,
    Discriminator("type"),
]
