from eip712.model.base import Model
from eip712.model.resolved.message import ResolvedEIP712Message
from eip712.model.types import ContractAddress

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class ResolvedEIP712Contract(Model):
    """
    Resolved Descriptor for a single smart contract on a specific network.

    Defines messages associated with this contract and how we want to display them on device.
    """

    address: ContractAddress
    contractName: str
    messages: list[ResolvedEIP712Message]
