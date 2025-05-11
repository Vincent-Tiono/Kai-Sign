"""
Data model for Ledger specific calldata descriptor, version 1 (also referred to as "generic parser" descriptor).
"""

from typing import Literal

from pydantic import Field

from erc7730.model.calldata import CalldataDescriptorBase
from erc7730.model.calldata.v1.instruction import (
    CalldataDescriptorInstructionEnumValueV1,
    CalldataDescriptorInstructionFieldV1,
    CalldataDescriptorInstructionTransactionInfoV1,
)


class CalldataDescriptorV1(CalldataDescriptorBase):
    """
    A clear signing descriptor for a smart contract function calldata.

    Also referred to as a "generic parser descriptor".
    """

    version: Literal["v1"] = Field(
        default="v1",
        title="Descriptor type version",
        description="Version of the descriptor type (not the version of this specific descriptor, the version of the "
        "descriptor specification)",
    )

    transaction_info: CalldataDescriptorInstructionTransactionInfoV1 = Field(
        title="TRANSACTION_INFO instruction descriptor",
        description="Descriptor and metadata to craft a TRANSACTION_INFO APDU.",
    )

    enums: list[CalldataDescriptorInstructionEnumValueV1] = Field(
        title="ENUM_VALUE instructions descriptors",
        description="Descriptor and metadata to craft ENUM APDUs.",
    )

    fields: list[CalldataDescriptorInstructionFieldV1] = Field(
        title="FIELD instructions descriptors",
        description="Descriptor and metadata to craft FIELD APDUs.",
    )
