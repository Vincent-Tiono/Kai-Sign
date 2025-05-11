from typing import assert_never, final, override

from eip712.model.resolved.descriptor import ResolvedEIP712DAppDescriptor
from eip712.model.resolved.message import ResolvedEIP712MapperField
from eip712.model.schema import EIP712SchemaField, EIP712Type
from eip712.model.types import EIP712Format, EIP712NameSource, EIP712NameType
from eip712.utils import MissingRootTypeError, MultipleRootTypesError, get_primary_type
from pydantic_string_url import HttpUrl

from erc7730.common.output import ExceptionsToOutput, OutputAdder
from erc7730.convert import ERC7730Converter
from erc7730.model.context import EIP712Schema
from erc7730.model.display import (
    AddressNameType,
    DateEncoding,
    FieldFormat,
)
from erc7730.model.input.context import InputDeployment, InputDomain, InputEIP712, InputEIP712Context
from erc7730.model.input.descriptor import InputERC7730Descriptor
from erc7730.model.input.display import (
    InputAddressNameParameters,
    InputDateParameters,
    InputDisplay,
    InputFieldDescription,
    InputFormat,
    InputNestedFields,
    InputReference,
    InputTokenAmountParameters,
)
from erc7730.model.input.metadata import InputMetadata
from erc7730.model.paths import ContainerField, ContainerPath


@final
class EIP712toERC7730Converter(ERC7730Converter[ResolvedEIP712DAppDescriptor, InputERC7730Descriptor]):
    """
    Converts Ledger legacy EIP-712 descriptor to ERC-7730 descriptor.

    Generates 1 output ERC-7730 descriptor per contract, as ERC-7730 descriptors only represent 1 contract.
    """

    @override
    def convert(
        self, descriptor: ResolvedEIP712DAppDescriptor, out: OutputAdder
    ) -> dict[str, InputERC7730Descriptor] | None:
        with ExceptionsToOutput(out):
            descriptors: dict[str, InputERC7730Descriptor] = {}

            for contract in descriptor.contracts:
                formats: dict[str, InputFormat] = {}
                schemas: list[EIP712Schema | HttpUrl] = []

                for message in contract.messages:
                    if (primary_type := self._get_primary_type(message.schema_, out)) is None:
                        return None

                    schemas.append(EIP712Schema(primaryType=primary_type, types=message.schema_))

                    formats[primary_type] = InputFormat(
                        intent=message.mapper.label,
                        fields=[self._convert_field(field, out) for field in message.mapper.fields],
                        required=None,
                        screens=None,
                    )

                descriptors[contract.address] = InputERC7730Descriptor(
                    context=InputEIP712Context(
                        eip712=InputEIP712(
                            domain=InputDomain(
                                name=descriptor.name,
                                version=None,
                                chainId=descriptor.chainId,
                                verifyingContract=contract.address,
                            ),
                            schemas=schemas,
                            deployments=[InputDeployment(chainId=descriptor.chainId, address=contract.address)],
                        )
                    ),
                    metadata=InputMetadata(
                        owner=contract.contractName,
                        info=None,
                        token=None,
                        constants=None,
                        enums=None,
                    ),
                    display=InputDisplay(
                        definitions=None,
                        formats=formats,
                    ),
                )

        return descriptors

    @classmethod
    def _convert_field(
        cls, field: ResolvedEIP712MapperField, out: OutputAdder
    ) -> InputFieldDescription | InputReference | InputNestedFields:
        # FIXME must generate nested fields for arrays
        match field.format:
            case EIP712Format.RAW | None:
                return InputFieldDescription(path=field.path, label=field.label, format=FieldFormat.RAW, params=None)
            case EIP712Format.AMOUNT if field.assetPath is not None:
                return InputFieldDescription(
                    path=field.path,
                    label=field.label,
                    format=FieldFormat.TOKEN_AMOUNT,
                    params=InputTokenAmountParameters(tokenPath=field.assetPath),
                )
            case EIP712Format.AMOUNT:
                return InputFieldDescription(
                    path=field.path,
                    label=field.label,
                    format=FieldFormat.TOKEN_AMOUNT,
                    params=InputTokenAmountParameters(tokenPath=ContainerPath(field=ContainerField.TO)),
                )
            case EIP712Format.DATETIME:
                return InputFieldDescription(
                    path=field.path,
                    label=field.label,
                    format=FieldFormat.DATE,
                    params=InputDateParameters(encoding=DateEncoding.TIMESTAMP),
                )
            case EIP712Format.TRUSTED_NAME:
                field_format = (
                    FieldFormat.NFT_NAME if EIP712NameType.COLLECTION in field.nameTypes else FieldFormat.ADDRESS_NAME
                )
                return InputFieldDescription(
                    path=field.path,
                    label=field.label,
                    format=field_format,
                    params=InputAddressNameParameters(
                        types=cls.convert_trusted_names_types(field.nameTypes, out),
                        sources=cls.convert_trusted_names_sources(field.nameSources),
                    ),
                )
            case _:
                assert_never(field.format)

    @classmethod
    def _get_primary_type(
        cls, schema: dict[EIP712Type, list[EIP712SchemaField]], out: OutputAdder
    ) -> EIP712Type | None:
        try:
            return get_primary_type(schema)
        except MissingRootTypeError:
            return out.error(
                title="Invalid EIP-712 schema",
                message="Primary type could not be determined on EIP-712 schema, as all types are referenced by"
                "other types. Please make sure your schema has a root type.",
            )
        except MultipleRootTypesError:
            return out.error(
                title="Invalid EIP-712 schema",
                message="Primary type could not be determined on EIP-712 schema, as several types are not"
                "referenced by any other type. Please make sure your schema has a single root type.",
            )

    @classmethod
    def convert_trusted_names_types(
        cls, types: list[EIP712NameType] | None, out: OutputAdder
    ) -> list[AddressNameType] | None:
        if types is None:
            return None

        name_types: list[AddressNameType] = []
        for name_type in types:
            match name_type:
                case EIP712NameType.WALLET:
                    name_types.append(AddressNameType.WALLET)
                case EIP712NameType.EOA:
                    name_types.append(AddressNameType.EOA)
                case EIP712NameType.SMART_CONTRACT:
                    name_types.append(AddressNameType.CONTRACT)
                case EIP712NameType.TOKEN:
                    name_types.append(AddressNameType.TOKEN)
                case EIP712NameType.COLLECTION:
                    name_types.append(AddressNameType.COLLECTION)
                case EIP712NameType.CONTEXT_ADDRESS:
                    return out.error("EIP712 context_address trusted name type is not supported in ERC-7730")
                case _:
                    assert_never(name_type)

        return name_types

    @classmethod
    def convert_trusted_names_sources(cls, sources: list[EIP712NameSource] | None) -> list[str] | None:
        if sources is None:
            return None
        name_sources: list[str] = []

        for name_source in sources:
            if name_source == EIP712NameSource.LOCAL_ADDRESS_BOOK:
                # ERC-7730 specs defines "local" as an example
                name_sources.append("local")
            else:
                name_sources.append(name_source.value)
        return name_sources
