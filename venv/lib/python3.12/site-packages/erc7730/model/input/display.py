from typing import Annotated, Any, ForwardRef, Self

from pydantic import Discriminator, Field, Tag, model_validator

from erc7730.model.base import Model
from erc7730.model.display import (
    AddressNameType,
    DateEncoding,
    FieldFormat,
    FormatBase,
)
from erc7730.model.input.path import ContainerPathStr, DataPathStr, DescriptorPathStr
from erc7730.model.types import HexStr, Id, MixedCaseAddress, ScalarType
from erc7730.model.unions import field_discriminator, field_parameters_discriminator

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class InputFieldBase(Model):
    """
    A field formatter, containing formatting information of a single field in a message.
    """

    path: DescriptorPathStr | DataPathStr | ContainerPathStr | None = Field(
        default=None,
        title="Path",
        description="A path to the field in the structured data. The path is a JSON path expression that can be used "
        """to extract the field value from the structured data. Exactly one of "path" or "value" must be set.""",
    )

    value: DescriptorPathStr | ScalarType | None = Field(
        default=None,
        title="Value",
        description="A literal value on which the format should be applied instead of looking up a field in the "
        """structured data. Exactly one of "path" or "value" must be set.""",
    )

    @model_validator(mode="after")
    def _validate_one_of_path_or_value(self) -> Self:
        if self.path is None and self.value is None:
            raise ValueError('Either "path" or "value" must be set.')
        if self.path is not None and self.value is not None:
            raise ValueError('"path" and "value" are mutually exclusive.')
        return self


class InputReference(InputFieldBase):
    """
    A reference to a shared definition that should be used as the field formatting definition.

    The value is the key in the display definitions section, as a path expression $.display.definitions.DEFINITION_NAME.
    It is used to share definitions between multiple messages / functions.
    """

    ref: DescriptorPathStr = Field(
        alias="$ref",
        title="Internal Definition",
        description="An internal definition that should be used as the field formatting definition. The value is the "
        "key in the display definitions section, as a path expression $.display.definitions.DEFINITION_NAME.",
    )

    label: DescriptorPathStr | str | None = Field(
        default=None,
        title="Field Label",
        description="The label of the field, that will be displayed to the user in front of the formatted field value. "
        "Overrides the label in the referenced definition if set.",
    )

    params: dict[str, Any] | None = Field(
        default=None,
        title="Parameters",
        description="Parameters override. These values takes precedence over the ones in the definition itself.",
    )


class InputTokenAmountParameters(Model):
    """
    Token Amount Formatting Parameters.
    """

    tokenPath: DescriptorPathStr | DataPathStr | ContainerPathStr | None = Field(
        default=None,
        title="Token Path",
        description="Path reference to the address of the token contract. Used to associate correct ticker. If ticker "
        "is not found or tokenPath is not set, the wallet SHOULD display the raw value instead with an"
        '"Unknown token" warning. Exactly one of "tokenPath" or "token" must be set.',
    )

    token: DescriptorPathStr | MixedCaseAddress | None = Field(
        default=None,
        title="Token",
        description="The address of the token contract, as constant value. Used to associate correct ticker. If ticker "
        "is not found or value is not set, the wallet SHOULD display the raw value instead with an "
        '"Unknown token" warning. Exactly one of "tokenPath" or "token" must be set.',
    )

    nativeCurrencyAddress: list[DescriptorPathStr | MixedCaseAddress] | DescriptorPathStr | MixedCaseAddress | None = (
        Field(
            default=None,
            title="Native Currency Address",
            description="An address or array of addresses, any of which are interpreted as an amount in native "
            "currency rather than a token.",
        )
    )

    threshold: DescriptorPathStr | HexStr | int | None = Field(
        default=None,
        title="Unlimited Threshold",
        description="The threshold above which the amount should be displayed using the message parameter rather than "
        "the real amount (encoded as an int or byte array).",
    )

    message: DescriptorPathStr | str | None = Field(
        default=None,
        title="Unlimited Message",
        description="The message to display when the amount is above the threshold.",
    )

    @model_validator(mode="after")
    def _validate_one_of_token_path_or_value(self) -> Self:
        if self.tokenPath is not None and self.token is not None:
            raise ValueError('"tokenPath" and "token" are mutually exclusive.')
        return self


class InputAddressNameParameters(Model):
    """
    Address Names Formatting Parameters.
    """

    types: list[AddressNameType] | DescriptorPathStr | None = Field(
        default=None,
        title="Address Type",
        description="An array of expected types of the address. If set, the wallet SHOULD check that the address "
        "matches one of the types provided.",
        min_length=1,
    )

    sources: list[str] | DescriptorPathStr | None = Field(
        default=None,
        title="Trusted Sources",
        description="An array of acceptable sources for names. If set, the wallet SHOULD restrict name lookup to "
        "relevant sources.",
        min_length=1,
    )


class InputCallDataParameters(Model):
    """
    Embedded Calldata Formatting Parameters.
    """

    selector: DescriptorPathStr | str | None = Field(
        default=None,
        title="Called Selector",
        description="The selector being called, if not contained in the calldata. Hex string representation.",
    )

    calleePath: DescriptorPathStr | DataPathStr | ContainerPathStr | None = Field(
        default=None,
        title="Callee Path",
        description="The path to the address of the contract being called by this embedded calldata. Exactly one of "
        '"calleePath" or "callee" must be set.',
    )

    callee: DescriptorPathStr | MixedCaseAddress | None = Field(
        default=None,
        title="Callee",
        description="The address of the contract being called by this embedded calldata, as a constant value. Exactly "
        'one of "calleePath" or "callee" must be set.',
    )

    @model_validator(mode="after")
    def _validate_one_of_callee_path_or_value(self) -> Self:
        if self.calleePath is None and self.callee is None:
            raise ValueError('Either "calleePath" or "callee" must be set.')
        if self.calleePath is not None and self.callee is not None:
            raise ValueError('"calleePath" and "callee" are mutually exclusive.')
        return self


class InputNftNameParameters(Model):
    """
    NFT Names Formatting Parameters.
    """

    collectionPath: DescriptorPathStr | DataPathStr | ContainerPathStr | None = Field(
        default=None,
        title="Collection Path",
        description="The path to the collection in the structured data. Exactly one of "
        '"collectionPath" or "collection" must be set.',
    )

    collection: DescriptorPathStr | MixedCaseAddress | None = Field(
        default=None,
        title="Collection",
        description="The address of the collection contract, as a constant value. Exactly one of "
        '"collectionPath" or "collection" must be set.',
    )

    @model_validator(mode="after")
    def _validate_one_of_collection_path_or_value(self) -> Self:
        if self.collectionPath is None and self.collection is None:
            raise ValueError('Either "collectionPath" or "collection" must be set.')
        if self.collectionPath is not None and self.collection is not None:
            raise ValueError('"collectionPath" and "collection" are mutually exclusive.')
        return self


class InputDateParameters(Model):
    """
    Date Formatting Parameters
    """

    encoding: DateEncoding | DescriptorPathStr = Field(title="Date Encoding", description="The encoding of the date.")


class InputUnitParameters(Model):
    """
    Unit Formatting Parameters.
    """

    base: DescriptorPathStr | str = Field(
        title="Unit base symbol",
        description="The base symbol of the unit, displayed after the converted value. It can be an SI unit symbol or "
        "acceptable dimensionless symbols like % or bps.",
    )

    decimals: int | DescriptorPathStr | None = Field(
        default=None, title="Decimals", description="The number of decimals of the value, used to convert to a float."
    )

    prefix: bool | DescriptorPathStr | None = Field(
        default=None,
        title="Prefix",
        description="Whether the value should be converted to a prefixed unit, like k, M, G, etc.",
    )


class InputEnumParameters(Model):
    """
    Enum Formatting Parameters.
    """

    ref: DescriptorPathStr = Field(
        alias="$ref",
        title="Enum reference",
        description="The internal path to the enum definition used to convert this value.",
    )


InputFieldParameters = Annotated[
    Annotated[InputAddressNameParameters, Tag("address_name")]
    | Annotated[InputCallDataParameters, Tag("call_data")]
    | Annotated[InputTokenAmountParameters, Tag("token_amount")]
    | Annotated[InputNftNameParameters, Tag("nft_name")]
    | Annotated[InputDateParameters, Tag("date")]
    | Annotated[InputUnitParameters, Tag("unit")]
    | Annotated[InputEnumParameters, Tag("enum")],
    Discriminator(field_parameters_discriminator),
]


class InputFieldDefinition(Model):
    """
    A field formatter, containing formatting information of a single field in a message.
    """

    id: Id | None = Field(
        alias="$id",
        default=None,
        title="Id",
        description="An internal identifier that can be used either for clarity specifying what the element is or as a "
        "reference in device specific sections.",
    )

    label: DescriptorPathStr | str = Field(
        title="Field Label",
        description="The label of the field, that will be displayed to the user in front of the formatted field value.",
    )

    format: FieldFormat | None = Field(
        default=None,
        title="Field Format",
        description="The format of the field, that will be used to format the field value in a human readable way.",
    )

    params: InputFieldParameters | None = Field(
        default=None,
        title="Format Parameters",
        description="Format specific parameters that are used to format the field value in a human readable way.",
    )


class InputFieldDescription(InputFieldBase, InputFieldDefinition):
    """
    A field formatter, containing formatting information of a single field in a message.
    """


class InputNestedFields(InputFieldBase):
    """
    A single set of field formats, allowing recursivity in the schema.

    Used to group whole definitions for structures for instance. This allows nesting definitions of formats, but note
    that support for deep nesting will be device dependent.
    """

    fields: list[ForwardRef("InputField")] = Field(  # type: ignore
        title="Fields", description="Nested fields formats."
    )


InputField = Annotated[
    Annotated[InputReference, Tag("reference")]
    | Annotated[InputFieldDescription, Tag("field_description")]
    | Annotated[InputNestedFields, Tag("nested_fields")],
    Discriminator(field_discriminator),
]


class InputFormat(FormatBase):
    """
    A structured data format specification, containing formatting information of fields in a single type of message.
    """

    fields: list[InputField] = Field(
        title="Field Formats set",
        description="An array containing the ordered definitions of fields formats.",
    )

    required: list[DataPathStr | ContainerPathStr] | None = Field(
        default=None,
        title="Required fields",
        description="A list of fields that are required to be displayed to the user. A field that has a formatter and "
        "is not in this list is optional. A field that does not have a formatter should be silent, ie not "
        "shown.",
    )

    excluded: list[DataPathStr] | None = Field(
        default=None,
        title="Excluded fields",
        description="Intentionally excluded fields, as an array of *paths* referring to specific fields. A field that "
        "has no formatter and is not declared in this list MAY be considered as an error by the wallet when "
        "interpreting the descriptor. The excluded paths should interpreted as prefixes, meaning that all fields under "
        "excluded path should be ignored",
    )


class InputDisplay(Model):
    """
    Display Formatting Info Section.
    """

    definitions: dict[str, InputFieldDefinition] | None = Field(
        default=None,
        title="Common Formatter Definitions",
        description="A set of definitions that can be used to share formatting information between multiple messages / "
        "functions. The definitions can be referenced by the key name in an internal path.",
    )

    formats: dict[str, InputFormat] = Field(
        title="List of field formats",
        description="The list includes formatting info for each field of a structure. This list is indexed by a key "
        "identifying uniquely the message's type in the abi. For smartcontracts, it is the selector of the "
        "function or its signature; and for EIP712 messages it is the primaryType of the message.",
    )
