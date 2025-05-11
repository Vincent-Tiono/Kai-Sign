"""
Conversion of a root ERC-7730 descriptor to calldata descriptors (1 per chain + selector).
"""

from typing import cast

from pydantic_string_url import HttpUrl

from erc7730.common.abi import get_functions
from erc7730.common.ledger import ledger_network_id
from erc7730.common.output import OutputAdder
from erc7730.convert.calldata.v1.selector import convert_selector
from erc7730.convert.resolved.convert_erc7730_input_to_resolved import (
    ERC7730InputToResolved,
)
from erc7730.model.abi import Function
from erc7730.model.calldata.descriptor import CalldataDescriptor
from erc7730.model.input.descriptor import InputERC7730Descriptor
from erc7730.model.resolved.context import ResolvedContractContext
from erc7730.model.types import Selector


def convert_descriptor(
    input_descriptor: InputERC7730Descriptor,
    source: HttpUrl | None,
    chain_id: int | None,
    out: OutputAdder,
) -> list[CalldataDescriptor]:
    """
    Generate output calldata descriptors from an input ERC-7730 descriptor with contract context.

    If descriptor is invalid, an empty list is returned. If the descriptor is partially invalid, a partial list is
    returned. Errors are logged as warnings.

    :param input_descriptor: deserialized input ERC-7730 descriptor
    :param source: source of the descriptor file
    :param chain_id: if set, only emit calldata descriptors for given chain IDs
    :param out: error handler
    :return: output calldata descriptors (1 per chain + selector)
    """

    if (resolved_descriptor := ERC7730InputToResolved().convert(input_descriptor, out)) is None:
        return []

    context = cast(ResolvedContractContext, resolved_descriptor.context)
    abis: dict[Selector, Function] = get_functions(context.contract.abi).functions

    output_descriptors = []

    for deployment in context.contract.deployments:
        if chain_id is not None and chain_id != deployment.chainId:
            continue

        if ledger_network_id(deployment.chainId) is None:
            out.warning(f"Chain id {deployment.chainId} is not known, skipping it")
            continue

        for selector, format in resolved_descriptor.display.formats.items():
            if (abi := abis.get(selector)) is None:
                out.error(
                    title="Invalid selector",
                    message=f"Selector {selector} not found in ABI.",
                )
                continue

            descriptor = convert_selector(
                descriptor=resolved_descriptor,
                deployment=deployment,
                selector=selector,
                format=format,
                abi=abi,
                source=source,
                out=out,
            )

            if descriptor is not None:
                output_descriptors.append(descriptor)

    return output_descriptors
