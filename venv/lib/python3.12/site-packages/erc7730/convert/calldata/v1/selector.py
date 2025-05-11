"""
Conversion of an ERC-7730 descriptor to a calldata descriptor (for a single chain + selector).
"""

import hashlib
from typing import cast

from eth_typing import ChainId as EthChainId
from pydantic_string_url import HttpUrl

from erc7730.common.binary import from_hex
from erc7730.common.ledger import ledger_network_id
from erc7730.common.options import first_not_none
from erc7730.common.output import OutputAdder
from erc7730.convert.calldata.v1.abi import function_to_abi_tree
from erc7730.convert.calldata.v1.enum import convert_enums
from erc7730.convert.calldata.v1.field import convert_field
from erc7730.model.abi import Function
from erc7730.model.calldata.descriptor import (
    CalldataDescriptor,
    CalldataDescriptorV1,
)
from erc7730.model.calldata.v1.instruction import (
    CalldataDescriptorInstructionTransactionInfoV1,
)
from erc7730.model.resolved.context import ResolvedDeployment
from erc7730.model.resolved.descriptor import ResolvedERC7730Descriptor
from erc7730.model.resolved.display import ResolvedFormat
from erc7730.model.types import Selector


def convert_selector(
    descriptor: ResolvedERC7730Descriptor,
    deployment: ResolvedDeployment,
    selector: Selector,
    format: ResolvedFormat,
    abi: Function,
    source: HttpUrl | None,
    out: OutputAdder,
) -> CalldataDescriptor | None:
    """
    Generate output calldata descriptor for a single selector ("format" in ERC-7730 source descriptor).

    If descriptor is invalid, None is returned. Errors are logged to the console.

    :param descriptor: resolved source ERC-7730 descriptor
    :param deployment: chain id / contract address for which the descriptor is generated
    :param selector: function for which the descriptor is generated
    :param format: ERC-7730 format for the selector
    :param abi: ABI of the function
    :param source: source of the descriptor file
    :param out: error handler
    :return: output calldata descriptors (1 per chain + selector)
    """

    abi_tree = function_to_abi_tree(abi)

    creator_legal_name: str | None = None
    creator_url: str | None = None
    deploy_date: str | None = None
    if (owner_info := descriptor.metadata.info) is not None:
        creator_legal_name = owner_info.legalName
        creator_url = owner_info.url
        deploy_date = owner_info.deploymentDate.strftime("%Y-%m-%dT%H:%M:%SZ") if owner_info.deploymentDate else None

    enums = convert_enums(deployment, selector, descriptor.metadata.enums)

    enums_by_id = {enum.enum_id: enum.id for enum in enums}

    fields = []
    for input_field in format.fields:
        if (output_fields := convert_field(abi=abi_tree, field=input_field, enums=enums_by_id, out=out)) is None:
            return None
        fields.extend(output_fields)

    hash = hashlib.sha3_256()
    for field in fields:
        hash.update(from_hex(field.descriptor))

    transaction_info = CalldataDescriptorInstructionTransactionInfoV1(
        chain_id=EthChainId(deployment.chainId),
        address=deployment.address,
        selector=selector,
        hash=hash.digest().hex(),
        operation_type=first_not_none(format.intent, format.id, selector),  # type:ignore
        creator_name=descriptor.metadata.owner,
        creator_legal_name=creator_legal_name,
        creator_url=creator_url,
        contract_name=descriptor.context.id,
        deploy_date=deploy_date,
    )

    return CalldataDescriptorV1(
        source=source,
        network=cast(str, ledger_network_id(deployment.chainId)),
        chain_id=EthChainId(deployment.chainId),
        address=deployment.address,
        selector=selector,
        transaction_info=transaction_info,
        enums=enums,
        fields=fields,
    )
