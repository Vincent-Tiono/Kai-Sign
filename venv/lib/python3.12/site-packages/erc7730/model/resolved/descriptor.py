"""
Module implementing an object model for ERC-7730 resolved descriptors.

This model represents descriptors after resolution phase:
    - URLs have been fetched
    - Contract addresses have been normalized to lowercase
    - References have been inlined
    - Constants have been inlined
    - Field definitions have been inlined
    - Nested fields have been flattened where possible
    - Selectors have been converted to 4 bytes form
"""

from pydantic import Field

from erc7730.model.base import Model
from erc7730.model.resolved.context import ResolvedContractContext, ResolvedEIP712Context
from erc7730.model.resolved.display import ResolvedDisplay
from erc7730.model.resolved.metadata import ResolvedMetadata

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class ResolvedERC7730Descriptor(Model):
    """
    An ERC7730 Clear Signing descriptor.

    This model represents descriptors after resolution phase:
        - URLs have been fetched
        - Contract addresses have been normalized to lowercase
        - References have been inlined
        - Constants have been inlined
        - Field definitions have been inlined
        - Nested fields have been flattened where possible
        - Selectors have been converted to 4 bytes form

    Specification: https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs

    JSON schema: https://github.com/LedgerHQ/clear-signing-erc7730-registry/blob/master/specs/erc7730-v1.schema.json
    """

    schema_: str | None = Field(
        alias="$schema",
        default=None,
        title="Schema URL",
        description="The schema that the document should conform to. This should be the URL of a version of the clear "
        "signing JSON schemas available under "
        "https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs",
    )

    context: ResolvedContractContext | ResolvedEIP712Context = Field(
        title="Binding Context Section",
        description="The binding context is a set of constraints that are used to bind the ERC7730 file to a specific"
        "structured data being displayed. Currently, supported contexts include contract-specific"
        "constraints or EIP712 message specific constraints.",
    )

    metadata: ResolvedMetadata = Field(
        title="Metadata Section",
        description="The metadata section contains information about constant values relevant in the scope of the"
        "current contract / message (as matched by the `context` section)",
    )

    display: ResolvedDisplay = Field(
        title="Display Formatting Info Section",
        description="The display section contains all the information needed to format the data in a human readable"
        "way. It contains the constants and formatters used to display the data contained in the bound structure.",
    )
