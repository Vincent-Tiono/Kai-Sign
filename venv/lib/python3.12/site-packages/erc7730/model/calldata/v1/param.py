"""
Data model for calldata descriptor field parameters.

These model classes represent the exact same data fields that are serialized into TLV structs.
See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol
"""

from abc import ABC
from enum import IntEnum
from typing import Annotated, Literal

from pydantic import Field

from erc7730.model.calldata.types import TrustedNameSource, TrustedNameType
from erc7730.model.calldata.v1.struct import (
    CalldataDescriptorStructV1,
)
from erc7730.model.calldata.v1.value import (
    CalldataDescriptorValueV1,
)
from erc7730.model.types import Address, HexStr


class CalldataDescriptorParamType(IntEnum):
    """Type of calldata field parameters."""

    RAW = 0x00
    AMOUNT = 0x01
    TOKEN_AMOUNT = 0x02
    NFT = 0x03
    DATETIME = 0x04
    DURATION = 0x05
    UNIT = 0x06
    ENUM = 0x07
    TRUSTED_NAME = 0x08
    CALLDATA = 0x09


class CalldataDescriptorDateType(IntEnum):
    """Type of date formatting."""

    UNIX = 0x00
    BLOCK_HEIGHT = 0x01


class CalldataDescriptorParamBaseV1(CalldataDescriptorStructV1, ABC):
    """Base class for calldata descriptor PARAM_* structs."""

    value: CalldataDescriptorValueV1 = Field(
        title="Parameter value", description="Reference to value to display (as a path in serialized data)"
    )


class CalldataDescriptorParamRawV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_RAW struct."""

    type: Literal["RAW"] = Field(
        default="RAW",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_RAW struct",
    )


class CalldataDescriptorParamAmountV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_AMOUNT struct."""

    type: Literal["AMOUNT"] = Field(
        default="AMOUNT",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_AMOUNT struct",
    )


class CalldataDescriptorParamTokenAmountV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_TOKEN_AMOUNT struct."""

    type: Literal["TOKEN_AMOUNT"] = Field(
        default="TOKEN_AMOUNT",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_TOKEN_AMOUNT struct",
    )

    token: CalldataDescriptorValueV1 | None = Field(
        default=None,
        title="Token address value",
        description="Reference to token address (as a path in serialized data)",
    )

    native_currencies: list[Address] | None = Field(
        default=None, title="Native currencies", description="Addresses to interpret as native currency"
    )

    threshold: HexStr | None = Field(
        default=None,
        title="Unlimited amount threshold",
        description="Amount threshold to display as unlimited amount",
    )

    above_threshold_message: str | None = Field(
        default=None,
        title="Unlimited amount message",
        description="Label to display for unlimited amount",
        min_length=1,
        max_length=32,  # TODO to be refined
    )


class CalldataDescriptorParamNFTV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_NFT struct."""

    type: Literal["NFT"] = Field(
        default="NFT",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_NFT struct",
    )

    collection: CalldataDescriptorValueV1 = Field(
        title="Collection address value",
        description="Reference to the collection address (as a path in serialized data)",
    )


class CalldataDescriptorParamDatetimeV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_DATETIME struct."""

    type: Literal["DATETIME"] = Field(
        default="DATETIME",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_DATETIME struct",
    )

    date_type: CalldataDescriptorDateType = Field(
        title="Date type",
        description="Type of date formatting",
    )


class CalldataDescriptorParamDurationV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_DURATION struct."""

    type: Literal["DURATION"] = Field(
        default="DURATION",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_DURATION struct",
    )


class CalldataDescriptorParamUnitV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_UNIT struct."""

    type: Literal["UNIT"] = Field(
        default="UNIT",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_UNIT struct",
    )

    base: str = Field(
        title="Unit base symbol",
        description="The base symbol of the unit, displayed after the converted value. It can be an SI unit symbol or "
        "acceptable dimensionless symbols like % or bps.",
        min_length=1,
        max_length=32,  # TODO to be refined
    )

    decimals: int | None = Field(
        default=None,
        title="Decimals",
        description="The number of decimals of the value, used to convert to a float.",
        ge=0,
        le=255,
    )

    prefix: bool | None = Field(
        default=None,
        title="Prefix",
        description="Whether the value should be converted to a prefixed unit, like k, M, G, etc.",
    )


class CalldataDescriptorParamEnumV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_ENUM struct."""

    type: Literal["ENUM"] = Field(
        default="ENUM",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_ENUM struct",
    )

    id: int = Field(
        title="Enum identifier",
        description="Identifier of the enum (to differentiate multiple enums in one contract)",
        ge=0,
        le=255,
    )


class CalldataDescriptorParamTrustedNameV1(CalldataDescriptorParamBaseV1):
    """Descriptor for the PARAM_TRUSTED_NAME struct."""

    type: Literal["TRUSTED_NAME"] = Field(
        default="TRUSTED_NAME",
        title="Parameter type",
        description="Type of the parameter",
    )

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the PARAM_TRUSTED_NAME struct",
    )

    types: list[TrustedNameType] = Field(
        title="Allowed types", description="Allowed types for trusted names display", min_length=1
    )

    sources: list[TrustedNameSource] = Field(
        title="Allowed sources", description="Allowed sources for trusted names display", min_length=1
    )


CalldataDescriptorParamV1 = Annotated[
    CalldataDescriptorParamRawV1
    | CalldataDescriptorParamAmountV1
    | CalldataDescriptorParamTokenAmountV1
    | CalldataDescriptorParamNFTV1
    | CalldataDescriptorParamDatetimeV1
    | CalldataDescriptorParamDurationV1
    | CalldataDescriptorParamUnitV1
    | CalldataDescriptorParamEnumV1
    | CalldataDescriptorParamTrustedNameV1,
    Field(
        title="Field parameter",
        description="Format specific parameters for a calldata descriptor field.",
        discriminator="type",
    ),
]
