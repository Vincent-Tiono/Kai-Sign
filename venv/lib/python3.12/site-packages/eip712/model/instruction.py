from abc import ABC
from enum import Enum
from typing import Literal

from eip712.model.base import Model
from eip712.model.types import ContractAddress, HexString

EIP712Descriptor = HexString
SchemaHash = HexString

DEFAULT_FIELD_PREFIX = 72


class EIP712InstructionType(Enum):
    """
    EIP-712 Instruction Type
    """

    TOKEN = "token"  # nosec B105 - bandit false positive
    AMOUNT = "amount"
    RAW = "raw"
    DATETIME = "datetime"
    TRUSTED_NAME = "trusted-name"


class EIP712Instruction(ABC, Model):
    """
    EIP-712 Instruction abstract base class
    """

    type_prefix: int
    display_name: str
    chain_id: int
    contract_address: ContractAddress
    schema_hash: SchemaHash


class EIP712MessageInstruction(EIP712Instruction):
    """
    EIP-712 Message Instruction
    """

    type: Literal["message"] = "message"
    field_mappers_count: int


class EIP712FieldInstruction(EIP712Instruction):
    """
    EIP-712 Field Instruction
    """

    type: Literal["field"] = "field"
    field_path: str
    format: EIP712InstructionType
    coin_ref: int | None
    name_types: list[int] | None
    name_sources: list[int] | None


EIP712ContractInstructions = dict[SchemaHash, list[EIP712Instruction]]

EIP712DappInstructions = dict[ContractAddress, EIP712ContractInstructions]
