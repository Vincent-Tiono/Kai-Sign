from enum import Enum
from typing import Annotated, Any

from pydantic import Field, RootModel

from erc7730.model.base import Model
from erc7730.model.types import Id

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class FieldFormat(str, Enum):
    """
    The format of the field, that will be used to format the field value in a human readable way.
    """

    RAW = "raw"
    """The field should be displayed as the natural representation of the underlying structured data type."""

    ADDRESS_NAME = "addressName"
    """The field should be displayed as a trusted name, or as a raw address if no names are found in trusted sources.
    List of trusted sources can be optionally specified in parameters."""

    CALL_DATA = "calldata"
    """The field is itself a calldata embedded in main call. Another ERC 7730 should be used to parse this field. If not
    available or not supported, the wallet MAY display a hash of the embedded calldata instead."""

    AMOUNT = "amount"
    """The field should be displayed as an amount in underlying currency, converted using the best magnitude / ticker
    available."""

    TOKEN_AMOUNT = "tokenAmount"  # nosec B105 - bandit false positive
    """The field should be displayed as an amount, preceded by the ticker. The magnitude and ticker should be derived
    from the tokenPath parameter corresponding metadata."""

    NFT_NAME = "nftName"
    """The field should be displayed as a single NFT names, or as a raw token Id if a specific name is not found.
    Collection is specified by the collectionPath parameter."""

    DATE = "date"
    """The field should be displayed as a date. Suggested RFC3339 representation. Parameter specifies the encoding of
    the date."""

    DURATION = "duration"
    """The field should be displayed as a duration in HH:MM:ss form. Value is interpreted as a number of seconds."""

    UNIT = "unit"
    """The field should be displayed as a percentage. Magnitude of the percentage encoding is specified as a parameter.
    Example: a value of 3000 with magnitude 4 is displayed as 0.3%."""

    ENUM = "enum"
    """The field should be displayed as a human readable string by converting the value using the enum referenced in
    parameters."""


class DateEncoding(str, Enum):
    """
    The encoding for a date.
    """

    BLOCKHEIGHT = "blockheight"
    """The date is encoded as a block height."""

    TIMESTAMP = "timestamp"
    """The date is encoded as a timestamp."""


class AddressNameType(str, Enum):
    """
    The type of address to display. Restrict allowable sources of names and MAY lead to additional checks from wallets.
    """

    WALLET = "wallet"
    """Address is an account controlled by the wallet."""

    EOA = "eoa"
    """Address is an Externally Owned Account."""

    CONTRACT = "contract"
    """Address is a well known smartcontract."""

    TOKEN = "token"  # nosec B105 - bandit false positive
    """Address is a well known ERC-20 token."""

    COLLECTION = "collection"
    """Address is a well known NFT collection."""


class Screen(RootModel[dict[str, Any]]):
    """
    Screens section is used to group multiple fields to display into screens. Each key is a wallet type name. The
    format of the screens is wallet type dependent, as well as what can be done (reordering fields, max number of
    screens, etc...). See each wallet manufacturer documentation for more information.
    """


SimpleIntent = Annotated[
    str,
    Field(
        title="Simple Intent",
        description="A description of the intent of the structured data signing, that will be displayed to the user.",
        min_length=1,
        max_length=256,  # TODO: arbitrary value, to be refined
    ),
]

ComplexIntent = Annotated[
    dict[str, str],
    Field(
        title="Complex Intent",
        description="A description of the intent of the structured data signing, that will be displayed to the user.",
        min_length=1,
        max_length=32,  # TODO: arbitrary value, to be refined
    ),
]


class FormatBase(Model):
    """
    A structured data format specification, containing formatting information of fields in a single type of message.
    """

    id: Id | None = Field(
        alias="$id",
        default=None,
        title="Id",
        description="An internal identifier that can be used either for clarity specifying what the element is or as a "
        "reference in device specific sections.",
    )

    intent: SimpleIntent | ComplexIntent | None = Field(
        default=None,
        title="Intent Message",
        description="A description of the intent of the structured data signing, that will be displayed to the user.",
    )

    screens: dict[str, list[Screen]] | None = Field(
        default=None,
        title="Screens grouping information",
        description="Screens section is used to group multiple fields to display into screens. Each key is a wallet "
        "type name. The format of the screens is wallet type dependent, as well as what can be done (reordering "
        "fields, max number of screens, etc...). See each wallet manufacturer documentation for more "
        "information.",
    )
