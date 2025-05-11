"""
Data model for calldata descriptor instructions.

These model classes represent the exact same data fields that are serialized into TLV structs.
See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol
"""

from abc import ABC
from functools import cached_property
from typing import Annotated, Literal

from eth_typing import ChainId as EthChainId
from pydantic import Field, computed_field
from pydantic_string_url import HttpUrl

from erc7730.model.calldata.v1.param import (
    CalldataDescriptorParamV1,
)
from erc7730.model.calldata.v1.struct import (
    CalldataDescriptorStructV1,
)
from erc7730.model.types import Address, HexStr, Selector

CalldataDescriptorInstructionHex = Annotated[
    HexStr,
    Field(
        title="Serialized TLV instruction payload",
        description="Serialized, hex encoded TLV payload.",
        min_length=8,
        max_length=32768,
    ),
]

CalldataDescriptorInstructionProtobuf = Annotated[
    HexStr,
    Field(
        title="Serialized production signature payload",
        description="Serialized, hex encoded Protobuf payload used for production signature.",
        min_length=8,
        max_length=32768,
    ),
]


# extra must be ignored because of descriptor computed field
class CalldataDescriptorInstructionBaseV1(CalldataDescriptorStructV1, ABC, extra="ignore"):
    """Base class for calldata descriptor instructions."""


class CalldataDescriptorInstructionTransactionInfoV1(CalldataDescriptorInstructionBaseV1):
    """Instruction descriptor for the TRANSACTION_INFO struct."""

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the TRANSACTION_INFO struct",
    )

    chain_id: EthChainId = Field(
        title="Chain ID",
        description="The contract deployment EIP-155 chain id.",
    )

    address: Address = Field(
        title="Contract address",
        description="The contract deployment address.",
    )

    selector: Selector = Field(
        title="Function selector",
        description="The 4-bytes function selector this descriptor applies to.",
    )

    hash: str = Field(
        title="Structs hash",
        description="Hash of all the FIELD structs",
        pattern=r"^[a-f0-9]+$",
        min_length=64,
        max_length=64,
    )

    operation_type: str = Field(
        title="Operation type",
        description="Displayed in review first screens",
        min_length=1,
        max_length=32,  # TODO to be refined
    )

    creator_name: str | None = Field(
        default=None,
        title="Creator name",
        description="Displayed in review first screens",
        min_length=1,
        max_length=32,  # TODO to be refined
    )

    creator_legal_name: str | None = Field(
        default=None,
        title="Creator legal name",
        description="Displayed in review first screens",
        min_length=1,
        max_length=32,  # TODO to be refined
    )

    creator_url: HttpUrl | None = Field(
        default=None,
        title="Creator URL",
        description="Displayed in review first screens",
        min_length=1,
        max_length=256,  # TODO to be refined
    )

    contract_name: str | None = Field(
        default=None,
        title="Contract name",
        description="Displayed in review first screens",
        min_length=1,
        max_length=32,  # TODO to be refined
    )

    deploy_date: str | None = Field(
        default=None,
        title="Deploy date",
        description="Displayed in review first screens",
    )

    @computed_field(title="Descriptor", description="Hex encoded TRANSACTION_INFO TLV struct")  # type: ignore[misc]
    @cached_property
    def descriptor(self) -> CalldataDescriptorInstructionHex:
        from erc7730.convert.calldata.v1.tlv import (
            tlv_transaction_info,
        )

        return tlv_transaction_info(self).hex()


class CalldataDescriptorInstructionEnumValueV1(CalldataDescriptorInstructionBaseV1):
    """Instruction descriptor for the ENUM_VALUE struct."""

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the ENUM struct",
    )

    chain_id: EthChainId = Field(
        title="Chain ID",
        description="The contract deployment EIP-155 chain id.",
    )

    address: Address = Field(
        title="Contract address",
        description="The contract deployment address.",
    )

    selector: Selector = Field(
        title="Function selector",
        description="The 4-bytes function selector this descriptor applies to.",
    )

    enum_id: str = Field(
        title="Source enum identifier",
        description="Source identifier of the enum (to differentiate multiple enums in one contract)",
    )

    id: int = Field(
        title="Enum identifier",
        description="Identifier of the enum (to differentiate multiple enums in one contract)",
        ge=0,
        le=255,
    )

    value: int = Field(
        title="Enum entry value",
        description="Identifier of this specific entry (ordinal of the entry, type agnostic)",
        ge=0,
        le=32,
    )

    name: str = Field(
        title="Enum entry name",
        description="Enum display name (ASCII)",
        min_length=1,
        max_length=32,  # TODO to be refined
    )

    @computed_field(title="Descriptor", description="Hex encoded ENUM TLV struct")  # type: ignore[misc]
    @cached_property
    def descriptor(self) -> CalldataDescriptorInstructionHex:
        from erc7730.convert.calldata.v1.tlv import tlv_enum_value

        return tlv_enum_value(self).hex()


class CalldataDescriptorInstructionFieldV1(CalldataDescriptorInstructionBaseV1):
    """Instruction descriptor for the FIELD struct."""

    version: Literal[1] = Field(
        default=1,
        title="Struct version",
        description="Version of the FIELD struct",
    )

    name: str = Field(
        title="Field name",
        description="Field display name (ASCII)",
        min_length=1,
        max_length=32,  # TODO to be refined
    )

    param: CalldataDescriptorParamV1 = Field(
        title="Field parameter",
        description="Parameter of the field",
    )

    @computed_field(title="Descriptor", description="Hex encoded FIELD TLV struct")  # type: ignore[misc]
    @cached_property
    def descriptor(self) -> CalldataDescriptorInstructionHex:
        from erc7730.convert.calldata.v1.tlv import tlv_field

        return tlv_field(self).hex()
