from typing import assert_never, cast

from eip712.model.instruction import (
    DEFAULT_FIELD_PREFIX,
    EIP712FieldInstruction,
    EIP712Instruction,
    EIP712InstructionType,
    EIP712MessageInstruction,
)
from eip712.model.types import EIP712Version


def _serialize_int(value: int) -> str:
    return value.to_bytes(1, byteorder="big").hex()


def _serialize_chain_id(chain_id: int) -> str:
    return chain_id.to_bytes(8, byteorder="big").hex()


def _serialize_contract_address(contract_address: str) -> str:
    return contract_address[2:].lower()


def _serialize_string(name: str) -> str:
    return name.encode("utf-8").hex()


def _serialize_list(list: list[int]) -> str:
    return "".join(_serialize_int(item) for item in list)


def _serialize_message_instruction(instruction: EIP712MessageInstruction, version: EIP712Version) -> str:
    return (
        _serialize_int(instruction.type_prefix)
        + _serialize_chain_id(instruction.chain_id)
        + _serialize_contract_address(instruction.contract_address)
        + instruction.schema_hash
        + _serialize_int(instruction.field_mappers_count)
        + _serialize_string(instruction.display_name)
    )


def _serialize_field_data_v2(instruction: EIP712FieldInstruction) -> str:
    match instruction.format:
        case EIP712InstructionType.TOKEN:
            return _serialize_int(cast(int, instruction.coin_ref))
        case EIP712InstructionType.AMOUNT:
            return _serialize_string(instruction.display_name) + _serialize_int(cast(int, instruction.coin_ref))
        case EIP712InstructionType.TRUSTED_NAME:
            return (
                _serialize_string(instruction.display_name)
                + _serialize_list(cast(list[int], instruction.name_types))
                + _serialize_list(cast(list[int], instruction.name_sources))
            )
        case _:
            return _serialize_string(instruction.display_name)


def _serialize_field_instruction(instruction: EIP712FieldInstruction, version: EIP712Version) -> str:
    match version:
        case EIP712Version.V1:
            return (
                _serialize_int(DEFAULT_FIELD_PREFIX)
                + _serialize_chain_id(instruction.chain_id)
                + _serialize_contract_address(instruction.contract_address)
                + instruction.schema_hash
                + _serialize_string(instruction.field_path)
                + _serialize_string(instruction.display_name)
            )
        case EIP712Version.V2:
            return (
                _serialize_int(instruction.type_prefix)
                + _serialize_chain_id(instruction.chain_id)
                + _serialize_contract_address(instruction.contract_address)
                + instruction.schema_hash
                + _serialize_string(instruction.field_path)
                + _serialize_field_data_v2(instruction)
            )
        case _:
            assert_never(version)


def serialize_instruction(instruction: EIP712Instruction, version: EIP712Version) -> str:
    """
    Serialize an EIP-712 instruction
    """

    match instruction:
        case EIP712MessageInstruction():
            return _serialize_message_instruction(instruction, version)
        case EIP712FieldInstruction():
            return _serialize_field_instruction(instruction, version)
        case _:
            raise ValueError(f"unexpected instruction: `{instruction}`")
