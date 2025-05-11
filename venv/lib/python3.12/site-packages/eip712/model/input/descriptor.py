from eip712.model.base import Model
from eip712.model.input.contract import InputEIP712Contract

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class InputEIP712DAppDescriptor(Model):
    """
    Descriptor for a dapp on a specific network.

    Defines messages for one or more contracts and how we want to display them on device.
    """

    blockchainName: str
    chainId: int
    name: str
    contracts: list[InputEIP712Contract]
