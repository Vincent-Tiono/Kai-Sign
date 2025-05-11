"""
Utilities for accessing ERC-7730 input descriptors nested fields.
"""

from erc7730.model.input.context import InputBindingContext, InputContractContext, InputDeployment, InputEIP712Context
from erc7730.model.input.descriptor import InputERC7730Descriptor


def get_chain_ids(descriptor: InputERC7730Descriptor) -> set[int]:
    """Get deployment chaind ids for a descriptor."""
    return {d.chainId for d in get_deployments(descriptor)}


def get_deployments(descriptor: InputERC7730Descriptor) -> list[InputDeployment]:
    """Get deployments section for a descriptor."""
    return get_binding_context(descriptor).deployments


def get_binding_context(descriptor: InputERC7730Descriptor) -> InputBindingContext:
    """Get binding context for a descriptor."""
    if isinstance(context := descriptor.context, InputEIP712Context):
        return context.eip712
    if isinstance(context := descriptor.context, InputContractContext):
        return context.contract
    raise ValueError(f"Invalid context type {type(descriptor.context)}")
