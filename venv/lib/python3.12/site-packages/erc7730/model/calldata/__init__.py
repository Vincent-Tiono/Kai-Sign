"""
Data model for Ledger specific calldata descriptor (also referred to as "generic parser" descriptor).

See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol

This data model is exposed in the public API and used by client applications to interact with the Ethereum application
using the generic parser protocol.
"""

from abc import ABC
from enum import StrEnum, auto
from typing import Literal

from eth_typing import ChainId as EthChainId
from pydantic import Field
from pydantic_string_url import HttpUrl

from erc7730.model.base import Model
from erc7730.model.types import Address, Id, Selector


class CalldataDescriptorVersion(StrEnum):
    """Version of the calldata descriptor."""

    v1 = auto()


class CalldataDescriptorBase(Model, ABC):
    """
    A clear signing descriptor for a smart contract function calldata.

    Note a calldata descriptor is bound to a single deployment (single chain id/contract address) and a single function.

    Also referred to as a "generic parser descriptor".
    """

    type: Literal["calldata"] = Field(
        default="calldata",
        title="Descriptor type",
        description="Type of the descriptor",
    )

    source: HttpUrl | None = Field(
        default=None,
        title="Descriptor source URL",
        description="The URL of the source of the descriptor (typically in clear-signing-erc7730-registry).",
    )

    network: Id = Field(
        title="Ledger Network identifier",
        description="The Ledger network this descriptor applies to.",
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
