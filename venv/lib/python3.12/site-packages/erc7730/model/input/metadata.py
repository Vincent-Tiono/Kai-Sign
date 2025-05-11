"""
Object model for ERC-7730 descriptors `metadata` section.

Specification: https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs
JSON schema: https://github.com/LedgerHQ/clear-signing-erc7730-registry/blob/master/specs/erc7730-v1.schema.json
"""

from pydantic import Field
from pydantic_string_url import HttpUrl

from erc7730.model.metadata import Metadata
from erc7730.model.resolved.metadata import EnumDefinition
from erc7730.model.types import Id, ScalarType

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class InputMetadata(Metadata):
    """
    Metadata Section.

    The metadata section contains information about constant values relevant in the scope of the current contract /
    message (as matched by the `context` section)
    """

    constants: dict[Id, ScalarType | None] | None = Field(
        default=None,
        title="Constant values",
        description="A set of values that can be used in format parameters. Can be referenced with a path expression "
        "like $.metadata.constants.CONSTANT_NAME",
        examples=[
            {
                "token_path": "#.params.witness.outputs[0].token",
                "native_currency": "0x0000000000000000000000000000000000000001",
                "max_threshold": "0xFFFFFFFF",
                "max_message": "Max",
            }
        ],
    )

    enums: dict[Id, HttpUrl | EnumDefinition] | None = Field(
        default=None,
        title="Enums",
        description="A set of enums that are used to format fields replacing values with human readable strings.",
        examples=[{"interestRateMode": {"1": "stable", "2": "variable"}, "vaultIDs": "https://example.com/vaultIDs"}],
        max_length=32,  # TODO refine
    )
