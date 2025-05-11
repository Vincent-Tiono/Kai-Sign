"""
Common data model for all calldata descriptor structs.

See documentation in https://github.com/LedgerHQ/app-ethereum for specifications of this protocol
"""

from abc import ABC

from pydantic import Field

from erc7730.model.base import Model


class CalldataDescriptorStructV1(Model, ABC):
    """Base class for calldata descriptor structs."""

    version: int = Field(
        title="Struct version",
        description="Version of the struct",
        ge=0,
        le=255,
    )
