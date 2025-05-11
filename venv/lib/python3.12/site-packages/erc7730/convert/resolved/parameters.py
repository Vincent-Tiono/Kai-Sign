from typing import assert_never, cast

from erc7730.common.abi import ABIDataType
from erc7730.common.output import OutputAdder
from erc7730.convert.resolved.constants import ConstantProvider
from erc7730.convert.resolved.enums import get_enum, get_enum_id
from erc7730.convert.resolved.values import resolve_path_or_constant_value
from erc7730.model.input.display import (
    InputAddressNameParameters,
    InputCallDataParameters,
    InputDateParameters,
    InputEnumParameters,
    InputFieldParameters,
    InputNftNameParameters,
    InputTokenAmountParameters,
    InputUnitParameters,
)
from erc7730.model.input.path import DescriptorPathStr
from erc7730.model.metadata import EnumDefinition
from erc7730.model.paths import DataPath
from erc7730.model.resolved.display import (
    ResolvedAddressNameParameters,
    ResolvedCallDataParameters,
    ResolvedDateParameters,
    ResolvedEnumParameters,
    ResolvedFieldParameters,
    ResolvedNftNameParameters,
    ResolvedTokenAmountParameters,
    ResolvedUnitParameters,
)
from erc7730.model.types import Address, HexStr, Id, MixedCaseAddress


def resolve_field_parameters(
    prefix: DataPath,
    params: InputFieldParameters | None,
    enums: dict[Id, EnumDefinition],
    constants: ConstantProvider,
    out: OutputAdder,
) -> ResolvedFieldParameters | None:
    match params:
        case None:
            return None
        case InputAddressNameParameters():
            return resolve_address_name_parameters(prefix, params, constants, out)
        case InputCallDataParameters():
            return resolve_calldata_parameters(prefix, params, constants, out)
        case InputTokenAmountParameters():
            return resolve_token_amount_parameters(prefix, params, constants, out)
        case InputNftNameParameters():
            return resolve_nft_parameters(prefix, params, constants, out)
        case InputDateParameters():
            return resolve_date_parameters(prefix, params, constants, out)
        case InputUnitParameters():
            return resolve_unit_parameters(prefix, params, constants, out)
        case InputEnumParameters():
            return resolve_enum_parameters(prefix, params, enums, constants, out)
        case _:
            assert_never(params)


def resolve_address_name_parameters(
    prefix: DataPath, params: InputAddressNameParameters, constants: ConstantProvider, out: OutputAdder
) -> ResolvedAddressNameParameters | None:
    return ResolvedAddressNameParameters(
        types=constants.resolve_or_none(params.types, out), sources=constants.resolve_or_none(params.sources, out)
    )


def resolve_calldata_parameters(
    prefix: DataPath, params: InputCallDataParameters, constants: ConstantProvider, out: OutputAdder
) -> ResolvedCallDataParameters | None:
    if (
        callee := resolve_path_or_constant_value(
            prefix=prefix,
            input_path=params.calleePath,
            input_value=params.callee,
            abi_type=ABIDataType.ADDRESS,
            constants=constants,
            out=out,
        )
    ) is None:
        return None

    return ResolvedCallDataParameters(
        selector=constants.resolve_or_none(params.selector, out),
        callee=callee,
    )


def resolve_token_amount_parameters(
    prefix: DataPath, params: InputTokenAmountParameters, constants: ConstantProvider, out: OutputAdder
) -> ResolvedTokenAmountParameters | None:
    token = resolve_path_or_constant_value(
        prefix=prefix,
        input_path=params.tokenPath,
        input_value=params.token,
        abi_type=ABIDataType.ADDRESS,
        constants=constants,
        out=out,
    )

    input_addresses = cast(
        list[DescriptorPathStr | MixedCaseAddress] | MixedCaseAddress | None,
        constants.resolve_or_none(params.nativeCurrencyAddress, out),
    )
    resolved_addresses: list[Address] | None
    if input_addresses is None:
        resolved_addresses = None
    elif isinstance(input_addresses, list):
        resolved_addresses = []
        for input_address in input_addresses:
            if (resolved_address := constants.resolve(input_address, out)) is None:
                return None
            resolved_addresses.append(Address(resolved_address))
    elif isinstance(input_addresses, str):
        resolved_addresses = [Address(input_addresses)]
    else:
        raise Exception("Invalid nativeCurrencyAddress type")

    input_threshold = cast(HexStr | int | None, constants.resolve_or_none(params.threshold, out))
    resolved_threshold: HexStr | None
    if input_threshold is not None:
        if isinstance(input_threshold, int):
            resolved_threshold = "0x" + input_threshold.to_bytes(byteorder="big", signed=False).hex()
        else:
            resolved_threshold = input_threshold
    else:
        resolved_threshold = None

    return ResolvedTokenAmountParameters(
        token=token,
        nativeCurrencyAddress=resolved_addresses,
        threshold=resolved_threshold,
        message=constants.resolve_or_none(params.message, out),
    )


def resolve_nft_parameters(
    prefix: DataPath, params: InputNftNameParameters, constants: ConstantProvider, out: OutputAdder
) -> ResolvedNftNameParameters | None:
    if (
        collection := resolve_path_or_constant_value(
            prefix=prefix,
            input_path=params.collectionPath,
            input_value=params.collection,
            abi_type=ABIDataType.ADDRESS,
            constants=constants,
            out=out,
        )
    ) is None:
        return None

    return ResolvedNftNameParameters(collection=collection)


def resolve_date_parameters(
    prefix: DataPath, params: InputDateParameters, constants: ConstantProvider, out: OutputAdder
) -> ResolvedDateParameters | None:
    return ResolvedDateParameters(encoding=constants.resolve(params.encoding, out))


def resolve_unit_parameters(
    prefix: DataPath, params: InputUnitParameters, constants: ConstantProvider, out: OutputAdder
) -> ResolvedUnitParameters | None:
    return ResolvedUnitParameters(
        base=constants.resolve(params.base, out),
        decimals=constants.resolve_or_none(params.decimals, out),
        prefix=constants.resolve_or_none(params.prefix, out),
    )


def resolve_enum_parameters(
    prefix: DataPath,
    params: InputEnumParameters,
    enums: dict[Id, EnumDefinition],
    constants: ConstantProvider,
    out: OutputAdder,
) -> ResolvedEnumParameters | None:
    if (enum_id := get_enum_id(params.ref, out)) is None:
        return None
    if get_enum(params.ref, enums, out) is None:
        return None

    return ResolvedEnumParameters(enumId=enum_id)
