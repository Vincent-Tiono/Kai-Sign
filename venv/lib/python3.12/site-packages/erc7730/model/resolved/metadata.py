"""
Object model for ERC-7730 descriptors `metadata` section.

Specification: https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs
JSON schema: https://github.com/LedgerHQ/clear-signing-erc7730-registry/blob/master/specs/erc7730-v1.schema.json
"""

from pydantic import Field

from erc7730.model.metadata import EnumDefinition, Metadata
from erc7730.model.types import Id

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class ResolvedMetadata(Metadata):
    """
    Metadata Section.

    The metadata section contains information about constant values relevant in the scope of the current contract /
    message (as matched by the `context` section)
    """

    enums: dict[Id, EnumDefinition] | None = Field(
        default=None,
        title="Enums",
        description="A set of enums that are used to format fields replacing values with human readable strings.",
        examples=[{"interestRateMode": {"1": "stable", "2": "variable"}}],
        max_length=32,  # TODO refine
    )
