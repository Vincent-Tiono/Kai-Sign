"""
Conversion of ERC-7730 enum definitions to calldata descriptor instructions.
"""

from eth_typing import ChainId as EthChainId

from erc7730.model.calldata.v1.instruction import (
    CalldataDescriptorInstructionEnumValueV1,
)
from erc7730.model.metadata import EnumDefinition
from erc7730.model.resolved.context import ResolvedDeployment
from erc7730.model.types import Id, Selector


def convert_enums(
    deployment: ResolvedDeployment, selector: Selector, enums: dict[Id, EnumDefinition] | None
) -> list[CalldataDescriptorInstructionEnumValueV1]:
    """
    Convert descriptor enum definitions to calldata descriptor enum value instructions.

    @param enums: descriptor enum definitions
    @return: instructions for each enum entry
    """
    if enums is None:
        return []

    return [
        CalldataDescriptorInstructionEnumValueV1(
            chain_id=EthChainId(deployment.chainId),
            address=deployment.address,
            selector=selector,
            id=i,
            enum_id=enum_id,
            value=int(ordinal),
            name=name,
        )
        for i, (enum_id, enum) in enumerate(enums.items())
        for ordinal, name in enum.items()
    ]
