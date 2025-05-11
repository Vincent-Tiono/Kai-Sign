from typing import assert_never

from pydantic import TypeAdapter, ValidationError

from erc7730.common.abi import ABIDataType
from erc7730.common.output import OutputAdder
from erc7730.convert.resolved.constants import ConstantProvider
from erc7730.model.display import FieldFormat
from erc7730.model.input.display import InputFieldBase
from erc7730.model.paths import ContainerPath, DataPath, DescriptorPath
from erc7730.model.paths.path_ops import data_or_container_path_concat
from erc7730.model.resolved.display import ResolvedValue, ResolvedValueConstant, ResolvedValuePath
from erc7730.model.types import HexStr, ScalarType


def resolve_field_value(
    prefix: DataPath,
    input_field: InputFieldBase,
    input_field_format: FieldFormat | None,
    constants: ConstantProvider,
    out: OutputAdder,
) -> ResolvedValue | None:
    """
    Resolve value, as a data path or constant value, for a field or reference.

    :param prefix: current path prefix
    :param input_field: field description or definition
    :param input_field_format: input field format
    :param constants: descriptor paths constants resolver
    :param out: error handler
    :return: resolved value or None if error
    """
    match input_field_format:
        case None | FieldFormat.RAW:
            abi_type = ABIDataType.STRING
        case (
            FieldFormat.AMOUNT
            | FieldFormat.TOKEN_AMOUNT
            | FieldFormat.DURATION
            | FieldFormat.DATE
            | FieldFormat.UNIT
            | FieldFormat.NFT_NAME
            | FieldFormat.ENUM
        ):
            abi_type = ABIDataType.UINT
        case FieldFormat.ADDRESS_NAME:
            abi_type = ABIDataType.ADDRESS
        case FieldFormat.CALL_DATA:
            abi_type = ABIDataType.BYTES
        case _:
            assert_never(input_field_format)

    if (
        value := resolve_path_or_constant_value(
            prefix=prefix,
            input_path=input_field.path,
            input_value=input_field.value,
            abi_type=abi_type,
            constants=constants,
            out=out,
        )
    ) is None:
        return out.error(title="Invalid field", message="Field must have either a path or a value.")
    return value


def resolve_path_or_constant_value(
    prefix: DataPath,
    input_path: DescriptorPath | DataPath | ContainerPath | None,
    input_value: DescriptorPath | ScalarType | None,
    abi_type: ABIDataType,
    constants: ConstantProvider,
    out: OutputAdder,
) -> ResolvedValue | None:
    """
    Resolve value, as a data path or constant value.

    :param prefix: current path prefix
    :param input_path: input data path, if provided
    :param input_value: input constant value, if provided
    :param abi_type: expected encoded value data type
    :param constants: descriptor paths constants resolver
    :param out: error handler
    :return: resolved value or None if error or value resolves to None
    """
    if input_path is not None:
        if input_value is not None:
            return out.error(
                title="Invalid field",
                message="Field cannot have both a path and a value.",
            )

        if (path := constants.resolve_path(input_path, out)) is None:
            return None

        return ResolvedValuePath(path=data_or_container_path_concat(prefix, path))

    if input_value is not None:
        if (value := constants.resolve(input_value, out)) is None:
            return None

        if not isinstance(value, str | bool | int | float):
            return out.error(
                title="Invalid constant value",
                message="Constant value must be a scalar type (string, boolean or number).",
            )

        if (raw := encode_value(value, abi_type, out)) is None:
            return None

        return ResolvedValueConstant(type_family=abi_type, type_size=len(raw) // 2 - 1, value=value, raw=raw)

    return None


def encode_value(value: ScalarType, abi_type: ABIDataType, out: OutputAdder) -> HexStr | None:
    if isinstance(value, str) and value.startswith("0x"):
        try:
            return TypeAdapter(HexStr).validate_strings(value)
        except ValidationError:
            return out.error(
                title="Invalid hex string",
                message=f""""{value}" is not a valid hexadecimal string.""",
            )

    # this uses a custom specific encoding because this is what the Ledger app expects
    try:
        match abi_type:
            case ABIDataType.UFIXED | ABIDataType.FIXED:
                return out.error(title="Invalid constant", message="""Fixed precision numbers are not supported""")

            case ABIDataType.UINT:
                if not isinstance(value, int) or value < 0:
                    return out.error(title="Invalid constant", message=f"""Value "{value}" is not an unsigned int""")
                encoded = value.to_bytes(length=(max(value.bit_length(), 1) + 7) // 8, signed=False)

            case ABIDataType.INT:
                if not isinstance(value, int):
                    return out.error(title="Invalid constant", message=f"""Value "{value}" is not an integer""")
                encoded = value.to_bytes(length=(max(value.bit_length(), 1) + 7) // 8, signed=True)

            case ABIDataType.BOOL:
                if not isinstance(value, bool):
                    return out.error(title="Invalid constant", message=f"""Value "{value}" is not a boolean""")
                encoded = value.to_bytes()

            case ABIDataType.STRING:
                if not isinstance(value, str):
                    return out.error(title="Invalid constant", message=f"""Value "{value}" is not a string""")
                encoded = value.encode(encoding="ascii", errors="replace")

            case ABIDataType.ADDRESS:
                return out.error(
                    title="Invalid constant", message=f"""Value "{value}" is not a valid address hexadecimal string."""
                )

            case ABIDataType.BYTES:
                return out.error(
                    title="Invalid constant", message=f"""Value "{value}" is not a valid hexadecimal string."""
                )

            case _:
                assert_never(abi_type)
    except OverflowError:
        return out.error(
            title="Invalid constant",
            message=f"""Value "{value}" is too large for the specified type.""",
        )

    return HexStr("0x" + encoded.hex())
