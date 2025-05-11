"""
Package implementing an object model for ERC-7730 input descriptors.

This model represents descriptors before resolution phase:
    - URLs have been not been fetched yet
    - Contract addresses have not been normalized to lowercase
    - References have not been inlined
    - Constants have not been inlined
    - Field definitions have not been inlined
    - Nested fields have been flattened where possible
    - Selectors have been converted to 4 bytes form
"""

from pydantic import Field

from erc7730.model.base import Model
from erc7730.model.input.context import InputContractContext, InputEIP712Context
from erc7730.model.input.display import InputDisplay
from erc7730.model.input.metadata import InputMetadata

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class InputERC7730Descriptor(Model):
    """
    An ERC7730 Clear Signing descriptor.

    This model is directly serializable back the original JSON document.

    Specification: https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs

    JSON schema: https://github.com/LedgerHQ/clear-signing-erc7730-registry/blob/master/specs/erc7730-v1.schema.json
    """

    schema_: str | None = Field(
        None,
        alias="$schema",
        description="The schema that the document should conform to. This should be the URL of a version of the clear "
        "signing JSON schemas available under "
        "https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs",
    )

    context: InputContractContext | InputEIP712Context = Field(
        title="Binding Context Section",
        description="The binding context is a set of constraints that are used to bind the ERC7730 file to a specific"
        "structured data being displayed. Currently, supported contexts include contract-specific"
        "constraints or EIP712 message specific constraints.",
    )

    metadata: InputMetadata = Field(
        title="Metadata Section",
        description="The metadata section contains information about constant values relevant in the scope of the"
        "current contract / message (as matched by the `context` section)",
    )

    display: InputDisplay = Field(
        title="Display Formatting Info Section",
        description="The display section contains all the information needed to format the data in a human readable"
        "way. It contains the constants and formatters used to display the data contained in the bound structure.",
    )
