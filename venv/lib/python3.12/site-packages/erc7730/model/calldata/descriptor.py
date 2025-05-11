"""
Base data model for Ledger specific calldata descriptor (also referred to as "generic parser" descriptor).

See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol

This data model is exposed in the public API and used by client applications to interact with the Ethereum application
using the generic parser protocol.
"""

from typing import Annotated

from pydantic import Field

from erc7730.model.calldata.v1.descriptor import (
    CalldataDescriptorV1,
)

CalldataDescriptor = Annotated[
    CalldataDescriptorV1,
    Field(
        title="Calldata descriptor",
        description="A clear signing descriptor for a smart contract function calldata. Also referred to as a "
        """"generic parser descriptor".""",
        discriminator="version",
    ),
]
