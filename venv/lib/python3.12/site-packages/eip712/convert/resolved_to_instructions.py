from typing import assert_never

from eip712.model.instruction import (
    DEFAULT_FIELD_PREFIX,
    EIP712DappInstructions,
    EIP712FieldInstruction,
    EIP712Instruction,
    EIP712InstructionType,
    EIP712MessageInstruction,
)
from eip712.model.resolved.descriptor import ResolvedEIP712DAppDescriptor
from eip712.model.types import EIP712Format, EIP712NameSource, EIP712NameType
from eip712.utils import get_schema_hash


class EIP712ResolvedToInstructionsConverter:
    def convert(self, descriptor: ResolvedEIP712DAppDescriptor) -> EIP712DappInstructions:
        """
        Convert a resolved EIP712 descriptor to a dictionary of EIP712 instructions.
        """
        instructions: EIP712DappInstructions = {}
        for contract in descriptor.contracts:
            instructions[contract.address] = {}
            for message in contract.messages:
                schema_hash = get_schema_hash(message.schema_)
                instructions_list: list[EIP712Instruction] = []
                for field in message.mapper.fields:
                    match field.format:
                        case EIP712Format.AMOUNT:
                            # special case: if assetPath is None, the token referenced is EIP712Domain.verifyingContract
                            # we generate only one instruction with coin_ref=0xFF
                            if field.assetPath is None:
                                instructions_list.append(
                                    EIP712FieldInstruction(
                                        type_prefix=22,
                                        display_name=field.label,
                                        chain_id=descriptor.chainId,
                                        contract_address=contract.address,
                                        schema_hash=schema_hash,
                                        field_path=field.path,
                                        format=EIP712InstructionType.AMOUNT,
                                        coin_ref=255,
                                        name_types=None,
                                        name_sources=None,
                                    )
                                )
                            else:
                                # General case: amount format generates two instructions:
                                # - in v1, this will result in 2 screens (raw token contract address, then raw amount)
                                # - in v2, this will result in 1 screen (amount with token)

                                if field.coinRef is None:
                                    raise ValueError(f"EIP712 amount value should have coin_ref: {self}")

                                instructions_list.extend(
                                    [
                                        EIP712FieldInstruction(
                                            type_prefix=11,
                                            display_name=field.label,
                                            chain_id=descriptor.chainId,
                                            contract_address=contract.address,
                                            schema_hash=schema_hash,
                                            field_path=field.assetPath,
                                            format=EIP712InstructionType.TOKEN,
                                            coin_ref=field.coinRef,
                                            name_types=None,
                                            name_sources=None,
                                        ),
                                        EIP712FieldInstruction(
                                            type_prefix=22,
                                            display_name=field.label,
                                            chain_id=descriptor.chainId,
                                            contract_address=contract.address,
                                            schema_hash=schema_hash,
                                            field_path=field.path,
                                            format=EIP712InstructionType.AMOUNT,
                                            coin_ref=field.coinRef,
                                            name_types=None,
                                            name_sources=None,
                                        ),
                                    ]
                                )
                        case EIP712Format.DATETIME:
                            instructions_list.append(
                                EIP712FieldInstruction(
                                    type_prefix=33,
                                    display_name=field.label,
                                    chain_id=descriptor.chainId,
                                    contract_address=contract.address,
                                    schema_hash=schema_hash,
                                    field_path=field.path,
                                    format=EIP712InstructionType.DATETIME,
                                    coin_ref=None,
                                    name_types=None,
                                    name_sources=None,
                                )
                            )
                        case EIP712Format.TRUSTED_NAME:
                            instructions_list.append(
                                EIP712FieldInstruction(
                                    type_prefix=44,
                                    display_name=field.label,
                                    chain_id=descriptor.chainId,
                                    contract_address=contract.address,
                                    schema_hash=schema_hash,
                                    field_path=field.path,
                                    format=EIP712InstructionType.TRUSTED_NAME,
                                    coin_ref=None,
                                    name_types=[self.name_type_to_int(name_type) for name_type in field.nameTypes],  # type: ignore
                                    name_sources=[
                                        self.name_source_to_int(name_source) for name_source in field.nameSources
                                    ]
                                    if field.nameSources is not None
                                    else [],
                                )
                            )
                        case _:
                            instructions_list.append(
                                EIP712FieldInstruction(
                                    type_prefix=DEFAULT_FIELD_PREFIX,
                                    display_name=field.label,
                                    chain_id=descriptor.chainId,
                                    contract_address=contract.address,
                                    schema_hash=schema_hash,
                                    field_path=field.path,
                                    format=EIP712InstructionType.RAW,
                                    coin_ref=None,
                                    name_types=None,
                                    name_sources=None,
                                )
                            )

                # Insert MessageInstruction at the beginning of the list
                # This is done after because it requires the length of the field instructions
                # computed above
                instructions_list.insert(
                    0,
                    EIP712MessageInstruction(
                        type_prefix=183,
                        display_name=message.mapper.label,
                        chain_id=descriptor.chainId,
                        contract_address=contract.address,
                        schema_hash=schema_hash,
                        field_mappers_count=len(instructions_list),
                    ),
                )
                instructions[contract.address][schema_hash] = instructions_list

        return instructions

    @classmethod
    def name_type_to_int(cls, name_type: EIP712NameType) -> int:
        match name_type:
            case EIP712NameType.EOA:
                return 1
            case EIP712NameType.SMART_CONTRACT:
                return 2
            case EIP712NameType.COLLECTION:
                return 3
            case EIP712NameType.TOKEN:
                return 4
            case EIP712NameType.WALLET:
                return 5
            case EIP712NameType.CONTEXT_ADDRESS:
                return 6
            case _:
                assert_never(name_type)

    @classmethod
    def name_source_to_int(cls, name_source: EIP712NameSource) -> int:
        match name_source:
            case EIP712NameSource.LOCAL_ADDRESS_BOOK:
                return 0
            case EIP712NameSource.CRYPTO_ASSET_LIST:
                return 1
            case EIP712NameSource.ENS:
                return 2
            case EIP712NameSource.UNSTOPPABLE_DOMAIN:
                return 3
            case EIP712NameSource.FREENAME:
                return 4
            case EIP712NameSource.DNS:
                return 5
            case EIP712NameSource.DYNAMIC_RESOLVER:
                return 6
            case _:
                assert_never(name_source)

    @classmethod
    def int_to_name_source(cls, value: int) -> EIP712NameSource:
        match value:
            case 0:
                return EIP712NameSource.LOCAL_ADDRESS_BOOK
            case 1:
                return EIP712NameSource.CRYPTO_ASSET_LIST
            case 2:
                return EIP712NameSource.ENS
            case 3:
                return EIP712NameSource.UNSTOPPABLE_DOMAIN
            case 4:
                return EIP712NameSource.FREENAME
            case 5:
                return EIP712NameSource.DNS
            case 6:
                return EIP712NameSource.DYNAMIC_RESOLVER
            case _:
                raise ValueError(f"Unknown EIP712NameSource value: {value}")

    @classmethod
    def int_to_name_type(cls, value: int) -> EIP712NameType:
        match value:
            case 1:
                return EIP712NameType.EOA
            case 2:
                return EIP712NameType.SMART_CONTRACT
            case 3:
                return EIP712NameType.COLLECTION
            case 4:
                return EIP712NameType.TOKEN
            case 5:
                return EIP712NameType.WALLET
            case 6:
                return EIP712NameType.CONTEXT_ADDRESS
            case _:
                raise ValueError(f"Unknown EIP712NameType value: {value}")
