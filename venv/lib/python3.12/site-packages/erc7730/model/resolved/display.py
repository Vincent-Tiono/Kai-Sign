from typing import Annotated, ForwardRef, Literal

from eip712.model.schema import EIP712Type
from pydantic import Discriminator, Field, Tag

from erc7730.common.abi import ABIDataType
from erc7730.model.base import Model
from erc7730.model.display import (
    AddressNameType,
    DateEncoding,
    FieldFormat,
    FormatBase,
)
from erc7730.model.paths import ContainerPath, DataPath
from erc7730.model.resolved.path import ResolvedPath
from erc7730.model.types import Address, HexStr, Id, ScalarType, Selector
from erc7730.model.unions import field_discriminator, field_parameters_discriminator

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class ResolvedValuePath(Model):
    """
    A path to the field in the structured data. The path is a JSON path expression that can be used to extract the
    field value from the structured data.
    """

    type: Literal["path"] = Field(
        default="path",
        title="Value Type",
        description="The value type identifier (discriminator for values discriminated union).",
    )

    path: ResolvedPath = Field(
        title="Path",
        description="A path to the field in the structured data. The path is a JSON path expression that can be used "
        "to extract the field value from the structured data.",
    )


class ResolvedValueConstant(Model):
    """
    A constant value.
    """

    type: Literal["constant"] = Field(
        default="constant",
        title="Value Type",
        description="The value type identifier (discriminator for values discriminated union).",
    )

    type_family: ABIDataType = Field(
        title="Type family",
        description="Type family of the value",
    )

    type_size: int | None = Field(
        default=None, title="Type size", description="Size of the type (in bytes)", ge=0, le=255
    )

    value: ScalarType = Field(
        title="Value",
        description="The constant value.",
    )

    raw: HexStr = Field(
        title="Raw Value",
        description="The constant value, serialized and hex encoded.",
    )


ResolvedValue = Annotated[
    ResolvedValuePath | ResolvedValueConstant,
    Discriminator("type"),
]


class ResolvedTokenAmountParameters(Model):
    """
    Token Amount Formatting Parameters.
    """

    token: ResolvedValue | None = Field(
        default=None,
        title="Token",
        description="The address of the token contract, either as path to a field in the structured data or a constant "
        "value. Used to associate correct ticker. If ticker is not found or value is not set, the wallet "
        'SHOULD display the raw value instead with an "Unknown token" warning.',
    )

    nativeCurrencyAddress: list[Address] | None = Field(
        default=None,
        title="Native Currency Address",
        description="An address or array of addresses, any of which are interpreted as an amount in native currency "
        "rather than a token.",
    )

    threshold: HexStr | None = Field(
        default=None,
        title="Unlimited Threshold",
        description="The threshold above which the amount should be displayed using the message parameter rather than "
        "the real amount (encoded as a byte array).",
    )

    message: str | None = Field(
        default=None,
        title="Unlimited Message",
        description="The message to display when the amount is above the threshold.",
    )


class ResolvedAddressNameParameters(Model):
    """
    Address Names Formatting Parameters.
    """

    types: list[AddressNameType] | None = Field(
        default=None,
        title="Address Type",
        description="An array of expected types of the address. If set, the wallet SHOULD check that the address "
        "matches one of the types provided.",
        min_length=1,
    )

    sources: list[str] | None = Field(
        default=None,
        title="Trusted Sources",
        description="An array of acceptable sources for names. If set, the wallet SHOULD restrict name lookup to "
        "relevant sources.",
        min_length=1,
    )


class ResolvedCallDataParameters(Model):
    """
    Embedded Calldata Formatting Parameters.
    """

    selector: str | None = Field(
        default=None,
        title="Called Selector",
        description="The selector being called, if not contained in the calldata. Hex string representation.",
    )

    callee: ResolvedValue = Field(
        title="Callee",
        description="The address of the contract being called by this embedded calldata, either as path to a field in "
        "the structured data or a constant value.",
    )


class ResolvedNftNameParameters(Model):
    """
    NFT Names Formatting Parameters.
    """

    collection: ResolvedValue = Field(
        title="Collection",
        description="The address of the collection contract, either as path to a field in the structured data or a "
        "constant value.",
    )


class ResolvedDateParameters(Model):
    """
    Date Formatting Parameters
    """

    encoding: DateEncoding = Field(title="Date Encoding", description="The encoding of the date.")


class ResolvedUnitParameters(Model):
    """
    Unit Formatting Parameters.
    """

    base: str = Field(
        title="Unit base symbol",
        description="The base symbol of the unit, displayed after the converted value. It can be an SI unit symbol or "
        "acceptable dimensionless symbols like % or bps.",
    )

    decimals: int | None = Field(
        default=None,
        title="Decimals",
        description="The number of decimals of the value, used to convert to a float.",
        ge=0,
        le=255,
    )

    prefix: bool | None = Field(
        default=None,
        title="Prefix",
        description="Whether the value should be converted to a prefixed unit, like k, M, G, etc.",
    )


class ResolvedEnumParameters(Model):
    """
    Enum Formatting Parameters.
    """

    enumId: Id = Field(
        title="Enum Identifier",
        description="The identifier of the enum in the $.context.metadata section.",
    )


ResolvedFieldParameters = Annotated[
    Annotated[ResolvedAddressNameParameters, Tag("address_name")]
    | Annotated[ResolvedCallDataParameters, Tag("call_data")]
    | Annotated[ResolvedTokenAmountParameters, Tag("token_amount")]
    | Annotated[ResolvedNftNameParameters, Tag("nft_name")]
    | Annotated[ResolvedDateParameters, Tag("date")]
    | Annotated[ResolvedUnitParameters, Tag("unit")]
    | Annotated[ResolvedEnumParameters, Tag("enum")],
    Discriminator(field_parameters_discriminator),
]


class ResolvedFieldBase(Model):
    """
    A field formatter, containing formatting information of a single field in a message.
    """

    value: ResolvedValue = Field(
        title="Value",
        description="A reference to the value to display, either as path to a field in the structured data or a "
        "constant value.",
    )


class ResolvedFieldDescription(ResolvedFieldBase):
    """
    A field formatter, containing formatting information of a single field in a message.
    """

    id: Id | None = Field(
        alias="$id",
        default=None,
        title="Id",
        description="An internal identifier that can be used either for clarity specifying what the element is or as a"
        "reference in device specific sections.",
    )

    label: str = Field(
        title="Field Label",
        description="The label of the field, that will be displayed to the user in front of the formatted field value.",
    )

    format: FieldFormat | None = Field(
        title="Field Format",
        description="The format of the field, that will be used to format the field value in a human readable way.",
    )

    params: ResolvedFieldParameters | None = Field(
        default=None,
        title="Format Parameters",
        description="Format specific parameters that are used to format the field value in a human readable way.",
    )


class ResolvedNestedFields(ResolvedFieldBase):
    """
    A single set of field formats, allowing recursivity in the schema.

    Used to group whole definitions for structures for instance. This allows nesting definitions of formats, but note
    that support for deep nesting will be device dependent.
    """

    fields: list[ForwardRef("ResolvedField")] = Field(  # type: ignore
        title="Fields", description="Nested fields formats."
    )


ResolvedField = Annotated[
    Annotated[ResolvedFieldDescription, Tag("field_description")]
    | Annotated[ResolvedNestedFields, Tag("nested_fields")],
    Discriminator(field_discriminator),
]


class ResolvedFormat(FormatBase):
    """
    A structured data format specification, containing formatting information of fields in a single type of message.
    """

    fields: list[ResolvedField] = Field(
        title="Field Formats set", description="An array containing the ordered definitions of fields formats."
    )

    required: list[DataPath | ContainerPath] | None = Field(
        default=None,
        title="Required fields",
        description="A list of fields that are required to be displayed to the user. A field that has a formatter and "
        "is not in this list is optional. A field that does not have a formatter should be silent, ie not "
        "shown.",
    )

    excluded: list[DataPath] | None = Field(
        default=None,
        title="Excluded fields",
        description="Intentionally excluded fields, as an array of *paths* referring to specific fields. A field that "
        "has no formatter and is not declared in this list MAY be considered as an error by the wallet when "
        "interpreting the descriptor. The excluded paths should interpreted as prefixes, meaning that all fields under "
        "excluded path should be ignored",
    )


class ResolvedDisplay(Model):
    """
    Display Formatting Info Section.
    """

    formats: dict[EIP712Type | Selector, ResolvedFormat] = Field(
        title="List of field formats",
        description="The list includes formatting info for each field of a structure. This list is indexed by a key"
        "identifying uniquely the message's type in the abi. For smartcontracts, it is the selector of the"
        "function or its signature; and for EIP712 messages it is the primaryType of the message.",
    )
