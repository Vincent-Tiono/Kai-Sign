"""
Conversion of ERC-7730 field definitions to calldata descriptor instructions.
"""

from typing import assert_never, cast

from erc7730.common.output import OutputAdder
from erc7730.convert.calldata.v1.abi import ABITree
from erc7730.convert.calldata.v1.path import convert_value
from erc7730.model.calldata.types import TrustedNameSource, TrustedNameType
from erc7730.model.calldata.v1.instruction import (
    CalldataDescriptorInstructionFieldV1,
)
from erc7730.model.calldata.v1.param import (
    CalldataDescriptorDateType,
    CalldataDescriptorParamAmountV1,
    CalldataDescriptorParamDatetimeV1,
    CalldataDescriptorParamDurationV1,
    CalldataDescriptorParamEnumV1,
    CalldataDescriptorParamNFTV1,
    CalldataDescriptorParamRawV1,
    CalldataDescriptorParamTokenAmountV1,
    CalldataDescriptorParamTrustedNameV1,
    CalldataDescriptorParamUnitV1,
    CalldataDescriptorParamV1,
)
from erc7730.model.calldata.v1.value import (
    CalldataDescriptorValueV1,
)
from erc7730.model.display import AddressNameType, DateEncoding, FieldFormat
from erc7730.model.resolved.display import (
    ResolvedAddressNameParameters,
    ResolvedDateParameters,
    ResolvedEnumParameters,
    ResolvedField,
    ResolvedFieldDescription,
    ResolvedNestedFields,
    ResolvedNftNameParameters,
    ResolvedTokenAmountParameters,
    ResolvedUnitParameters,
)
from erc7730.model.types import Address, HexStr


def convert_field(
    abi: ABITree,
    field: ResolvedField,
    enums: dict[str, int],
    out: OutputAdder,
) -> list[CalldataDescriptorInstructionFieldV1] | None:
    """
    Convert descriptor field definitions to calldata descriptor field instructions.

    Note that 1 input field can result in multiple output instructions, e.g. for nested fields.

    @param abi: function ABI
    @param field: resolved field
    @param enums: mapping of source descriptor enum ids to calldata descriptor enum ids
    @param out: error handler
    @return: 1 or more calldata field instructions
    """
    match field:
        case ResolvedFieldDescription():
            if (param := convert_param(abi=abi, field=field, enums=enums, out=out)) is None:
                return None
            return [CalldataDescriptorInstructionFieldV1(name=field.label, param=param)]
        case ResolvedNestedFields():
            # note: in v1 of protocol, nested fields are flattened. For instance, if a descriptor defines an array of
            # tokens with each a name field and an amount field, this will display all the tokens names and then all
            # the token amounts.
            instructions = []
            for nested_field in field.fields:
                if (nested_instructions := convert_field(abi=abi, field=nested_field, enums=enums, out=out)) is None:
                    return None
                instructions.extend(nested_instructions)
            return instructions
        case _:
            assert_never(field)


def convert_param(
    abi: ABITree,
    field: ResolvedFieldDescription,
    enums: dict[str, int],
    out: OutputAdder,
) -> CalldataDescriptorParamV1 | None:
    """
    Convert descriptor field parameters to calldata descriptor field parameters.

    @param abi: function ABI
    @param field: resolved field description
    @param enums: mapping of source descriptor enum ids to calldata descriptor enum ids
    @param out: error handler
    @return: calldata protocol field parameter
    """
    if (value := convert_value(value=field.value, abi=abi, out=out)) is None:
        return None

    match field.format:
        case None | FieldFormat.RAW:
            return CalldataDescriptorParamRawV1(value=value)

        case FieldFormat.ADDRESS_NAME:
            address_params = cast(ResolvedAddressNameParameters | None, field.params)

            types: list[TrustedNameType] = []
            sources: list[TrustedNameSource] = []

            if address_params is not None:
                if (input_types := address_params.types) is not None:
                    for input_type in input_types:
                        if input_type == AddressNameType.CONTRACT:
                            types.append(TrustedNameType.SMART_CONTRACT)
                        else:
                            types.append(TrustedNameType(input_type))

                # since sources are free form in ERC-7730, we apply the following algorithm:
                #   1) assign valid sources based on type
                #   2) add sources that perfectly match by name
                for type in types:
                    match type:
                        case TrustedNameType.EOA | TrustedNameType.WALLET | TrustedNameType.COLLECTION:
                            sources.append(TrustedNameSource.ENS)
                            sources.append(TrustedNameSource.UNSTOPPABLE_DOMAIN)
                            sources.append(TrustedNameSource.FREENAME)
                        case TrustedNameType.SMART_CONTRACT | TrustedNameType.TOKEN:
                            sources.append(TrustedNameSource.CRYPTO_ASSET_LIST)
                        case TrustedNameType.CONTEXT_ADDRESS:
                            sources.append(TrustedNameSource.DYNAMIC_RESOLVER)
                        case _:
                            assert_never(type)

                if (input_sources := address_params.sources) is not None:
                    for input_source in input_sources:
                        if input_source.lower() == "local":
                            sources.append(TrustedNameSource.LOCAL_ADDRESS_BOOK)
                        if input_source.lower() in set(TrustedNameSource):
                            sources.append(TrustedNameSource(input_source.lower()))

            # default to all types / sources allowed, else deduplicate
            types = list(TrustedNameType) if not types else list(dict.fromkeys(types))
            sources = list(TrustedNameSource) if not sources else list(dict.fromkeys(sources))

            return CalldataDescriptorParamTrustedNameV1(value=value, types=types, sources=sources)

        case FieldFormat.ENUM:
            enum_params = cast(ResolvedEnumParameters, field.params)

            if (enum_id := enums.get(enum_params.enumId)) is None:
                return out.error(
                    title="Invalid enum id",
                    message=f"""Failed finding descriptor id for enum {enum_params.enumId}, please report this bug""",
                )

            return CalldataDescriptorParamEnumV1(value=value, id=enum_id)

        case FieldFormat.UNIT:
            unit_params = cast(ResolvedUnitParameters, field.params)

            return CalldataDescriptorParamUnitV1(
                value=value, base=unit_params.base, decimals=unit_params.decimals, prefix=unit_params.prefix
            )

        case FieldFormat.DURATION:
            return CalldataDescriptorParamDurationV1(value=value)

        case FieldFormat.NFT_NAME:
            nft_params = cast(ResolvedNftNameParameters, field.params)

            if (collection_path := convert_value(value=nft_params.collection, abi=abi, out=out)) is None:
                return None

            return CalldataDescriptorParamNFTV1(value=value, collection=collection_path)

        case FieldFormat.CALL_DATA:
            # not supported in v1
            return CalldataDescriptorParamRawV1(value=value)

        case FieldFormat.DATE:
            date_params = cast(ResolvedDateParameters, field.params)

            match date_params.encoding:
                case DateEncoding.TIMESTAMP:
                    date_type = CalldataDescriptorDateType.UNIX
                case DateEncoding.BLOCKHEIGHT:
                    date_type = CalldataDescriptorDateType.BLOCK_HEIGHT
                case _:
                    assert_never(date_params.encoding)

            return CalldataDescriptorParamDatetimeV1(value=value, date_type=date_type)

        case FieldFormat.AMOUNT:
            return CalldataDescriptorParamAmountV1(value=value)

        case FieldFormat.TOKEN_AMOUNT:
            token_path: CalldataDescriptorValueV1 | None = None
            native_currencies: list[Address] | None = None
            threshold: HexStr | None = None
            above_threshold_message: str | None = None

            if (token_amount_params := cast(ResolvedTokenAmountParameters, field.params)) is not None:
                if token_amount_params.token is None:
                    token_path = None
                elif (token_path := convert_value(value=token_amount_params.token, abi=abi, out=out)) is None:
                    return None

                threshold = token_amount_params.threshold
                native_currencies = token_amount_params.nativeCurrencyAddress
                above_threshold_message = token_amount_params.message

            return CalldataDescriptorParamTokenAmountV1(
                value=value,
                token=token_path,
                native_currencies=native_currencies,
                threshold=threshold,
                above_threshold_message=above_threshold_message,
            )

        case _:
            assert_never(field.format)
