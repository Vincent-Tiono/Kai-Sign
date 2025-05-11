"""
Object model for ERC-7730 descriptors `metadata` section.

Specification: https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs
JSON schema: https://github.com/LedgerHQ/clear-signing-erc7730-registry/blob/master/specs/erc7730-v1.schema.json
"""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import Field
from pydantic_string_url import HttpUrl

from erc7730.model.base import Model

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class OwnerInfo(Model):
    """
    Main contract's owner detailed information.

    The owner info section contains detailed information about the owner or target of the contract / message to be
    clear signed.
    """

    legalName: str = Field(
        title="Owner Legal Name",
        description="The full legal name of the owner if different from the owner field.",
        min_length=1,
        examples=["Tether Limited", "Lido DAO"],
    )

    lastUpdate: datetime | None = Field(
        default=None,
        title="[DEPRECATED] Last Update of the contract / message",
        description="The date of the last update of the contract / message."
        "Field is deprecated and will be removed, use `deploymentDate` instead.",
        examples=[datetime.now(UTC)],
    )

    deploymentDate: datetime | None = Field(
        default=None,
        title="Deployment date of contract / message",
        description="The deployment date of the contract / message.",
        examples=[datetime.now(UTC)],
    )

    url: HttpUrl = Field(
        title="Owner URL",
        description="URL with more info on the entity the user interacts with.",
        examples=[HttpUrl("https://tether.to"), HttpUrl("https://lido.fi")],
    )


class TokenInfo(Model):
    """
    Token Description.

    A description of an ERC20 token exported by this format, that should be trusted. Not mandatory if the
    corresponding metadata can be fetched from the contract itself.
    """

    name: str = Field(
        title="Token Name",
        description="The token display name.",
        min_length=1,
        max_length=255,  # TODO: arbitrary value, to be refined
        examples=["Tether USD", "Dai Stablecoin"],
    )

    ticker: str = Field(
        title="Token Ticker",
        description="A short capitalized ticker for the token, that will be displayed in front of corresponding "
        "amounts.",
        min_length=1,
        max_length=10,  # TODO: arbitrary value, to be refined
        pattern=r"^[a-zA-Z0-9_\\-\\.]+$",
        examples=["USDT", "DAI", "rsETH"],
    )

    decimals: int = Field(
        title="Token Decimals",
        description="The number of decimals of the token ticker, used to display amounts.",
        ge=0,
        le=255,
        examples=[0, 18],
    )


class Metadata(Model):
    """
    Metadata Section.

    The metadata section contains information about constant values relevant in the scope of the current contract /
    message (as matched by the `context` section)
    """

    owner: str | None = Field(
        default=None,
        title="Owner display name.",
        description="The display name of the owner or target of the contract / message to be clear signed.",
    )

    info: OwnerInfo | None = Field(
        default=None,
        title="Main contract's owner detailed information.",
        description="The owner info section contains detailed information about the owner or target of the contract / "
        "message to be clear signed.",
    )

    token: TokenInfo | None = Field(
        default=None,
        title="Token Description",
        description="A description of an ERC20 token exported by this format, that should be trusted. Not mandatory if "
        "the corresponding metadata can be fetched from the contract itself.",
    )


EnumDefinition = Annotated[
    dict[str, str],
    Field(
        title="Enum Definition",
        description="A mapping of enum values to human readable strings.",
        examples=[{"1": "stable", "2": "variable"}],
        min_length=1,
        max_length=32,
    ),
]
