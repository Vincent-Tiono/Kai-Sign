"""
Encoding of calldata descriptor instructions to TLV format.

See https://github.com/LedgerHQ/generic_parser for specifications of these payloads.
"""

from datetime import datetime
from enum import IntEnum
from typing import assert_never

from erc7730.common.binary import from_hex, tlv
from erc7730.common.pydantic import pydantic_enum_by_name
from erc7730.model.calldata.types import TrustedNameSource, TrustedNameType
from erc7730.model.calldata.v1.instruction import (
    CalldataDescriptorInstructionEnumValueV1,
    CalldataDescriptorInstructionFieldV1,
    CalldataDescriptorInstructionTransactionInfoV1,
)
from erc7730.model.calldata.v1.param import (
    CalldataDescriptorParamAmountV1,
    CalldataDescriptorParamDatetimeV1,
    CalldataDescriptorParamDurationV1,
    CalldataDescriptorParamEnumV1,
    CalldataDescriptorParamNFTV1,
    CalldataDescriptorParamRawV1,
    CalldataDescriptorParamTokenAmountV1,
    CalldataDescriptorParamTrustedNameV1,
    CalldataDescriptorParamType,
    CalldataDescriptorParamUnitV1,
)
from erc7730.model.calldata.v1.value import (
    CalldataDescriptorContainerPathV1,
    CalldataDescriptorDataPathV1,
    CalldataDescriptorPathElementArrayV1,
    CalldataDescriptorPathElementLeafV1,
    CalldataDescriptorPathElementRefV1,
    CalldataDescriptorPathElementSliceV1,
    CalldataDescriptorPathElementTupleV1,
    CalldataDescriptorPathElementV1,
    CalldataDescriptorValueConstantV1,
    CalldataDescriptorValuePathV1,
    CalldataDescriptorValueV1,
)


@pydantic_enum_by_name
class CalldataDescriptorTransactionInfoTag(IntEnum):
    VERSION = 0x00
    CHAIN_ID = 0x01
    CONTRACT_ADDR = 0x02
    SELECTOR = 0x03
    FIELDS_HASH = 0x04
    OPERATION_TYPE = 0x05
    CREATOR_NAME = 0x06
    CREATOR_LEGAL_NAME = 0x07
    CREATOR_URL = 0x08
    CONTRACT_NAME = 0x09
    DEPLOY_DATE = 0x0A
    SIGNATURE = 0xFF


@pydantic_enum_by_name
class CalldataDescriptorEnumValueTag(IntEnum):
    VERSION = 0x00
    CHAIN_ID = 0x01
    CONTRACT_ADDR = 0x02
    SELECTOR = 0x03
    ID = 0x04
    VALUE = 0x05
    NAME = 0x06


@pydantic_enum_by_name
class CalldataDescriptorFieldTag(IntEnum):
    VERSION = 0x00
    NAME = 0x01
    PARAM_TYPE = 0x02
    PARAM = 0x03


@pydantic_enum_by_name
class CalldataDescriptorParamRawTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01


@pydantic_enum_by_name
class CalldataDescriptorParamAmountTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01


@pydantic_enum_by_name
class CalldataDescriptorParamTokenAmountTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01
    TOKEN = 0x02
    NATIVE_CURRENCY = 0x03
    THRESHOLD = 0x04
    ABOVE_THRESHOLD_MSG = 0x05


@pydantic_enum_by_name
class CalldataDescriptorParamNFTTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01
    COLLECTION = 0x02


@pydantic_enum_by_name
class CalldataDescriptorParamDateTimeTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01
    TYPE = 0x02


@pydantic_enum_by_name
class CalldataDescriptorParamDurationTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01


@pydantic_enum_by_name
class CalldataDescriptorParamUnitTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01
    BASE = 0x02
    DECIMALS = 0x03
    PREFIX = 0x04


@pydantic_enum_by_name
class CalldataDescriptorParamEnumTag(IntEnum):
    VERSION = 0x00
    ID = 0x01
    VALUE = 0x02


@pydantic_enum_by_name
class CalldataDescriptorParamTrustedNameTag(IntEnum):
    VERSION = 0x00
    VALUE = 0x01
    TYPES = 0x02
    SOURCES = 0x03


@pydantic_enum_by_name
class CalldataDescriptorValueTag(IntEnum):
    VERSION = 0x00
    TYPE_FAMILY = 0x01
    TYPE_SIZE = 0x02
    DATA_PATH = 0x03
    CONTAINER_PATH = 0x04
    CONSTANT = 0x05


@pydantic_enum_by_name
class CalldataDescriptorPathElementTag(IntEnum):
    VERSION = 0x00
    TUPLE = 0x01
    ARRAY = 0x02
    REF = 0x03
    LEAF = 0x04
    SLICE = 0x05


@pydantic_enum_by_name
class CalldataDescriptorPathArrayElementTag(IntEnum):
    WEIGHT = 0x01
    START = 0x02
    END = 0x03


@pydantic_enum_by_name
class CalldataDescriptorPathSliceElementTag(IntEnum):
    START = 0x01
    END = 0x02


def tlv_transaction_info(obj: CalldataDescriptorInstructionTransactionInfoV1) -> bytes:
    """
    Encode a struct of type TRANSACTION_INFO.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorTransactionInfoTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorTransactionInfoTag.CHAIN_ID, obj.chain_id.to_bytes(8))
    out += tlv(CalldataDescriptorTransactionInfoTag.CONTRACT_ADDR, from_hex(obj.address))
    out += tlv(CalldataDescriptorTransactionInfoTag.SELECTOR, from_hex(obj.selector))
    out += tlv(CalldataDescriptorTransactionInfoTag.FIELDS_HASH, from_hex(obj.hash))
    out += tlv(CalldataDescriptorTransactionInfoTag.OPERATION_TYPE, obj.operation_type)

    if (creator_name := obj.creator_name) is not None:
        out += tlv(CalldataDescriptorTransactionInfoTag.CREATOR_NAME, creator_name)

    if (creator_legal_name := obj.creator_legal_name) is not None:
        out += tlv(CalldataDescriptorTransactionInfoTag.CREATOR_LEGAL_NAME, creator_legal_name)

    if (creator_url := obj.creator_url) is not None:
        out += tlv(CalldataDescriptorTransactionInfoTag.CREATOR_URL, creator_url)

    if (contract_name := obj.contract_name) is not None:
        out += tlv(CalldataDescriptorTransactionInfoTag.CONTRACT_NAME, contract_name)

    if (deploy_date := obj.deploy_date) is not None:
        tstamp = int(datetime.fromisoformat(deploy_date).timestamp())
        out += tlv(CalldataDescriptorTransactionInfoTag.DEPLOY_DATE, tstamp.to_bytes(4))

    return out


def tlv_enum_value(obj: CalldataDescriptorInstructionEnumValueV1) -> bytes:
    """
    Encode a struct of type ENUM_VALUE.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorEnumValueTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorEnumValueTag.CHAIN_ID, obj.chain_id.to_bytes(8))
    out += tlv(CalldataDescriptorEnumValueTag.CONTRACT_ADDR, from_hex(obj.address))
    out += tlv(CalldataDescriptorEnumValueTag.SELECTOR, from_hex(obj.selector))
    out += tlv(CalldataDescriptorEnumValueTag.ID, obj.id.to_bytes(1))
    out += tlv(CalldataDescriptorEnumValueTag.VALUE, obj.value.to_bytes(1))
    out += tlv(CalldataDescriptorEnumValueTag.NAME, obj.name)
    return out


def tlv_field(obj: CalldataDescriptorInstructionFieldV1) -> bytes:
    """
    Encode a struct of type FIELD.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorFieldTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorFieldTag.NAME, obj.name)

    param_type: CalldataDescriptorParamType
    param_value: bytes
    match obj.param:
        case CalldataDescriptorParamRawV1():
            param_type = CalldataDescriptorParamType.RAW
            param_value = tlv_param_raw(obj.param)
        case CalldataDescriptorParamAmountV1():
            param_type = CalldataDescriptorParamType.AMOUNT
            param_value = tlv_param_amount(obj.param)
        case CalldataDescriptorParamTokenAmountV1():
            param_type = CalldataDescriptorParamType.TOKEN_AMOUNT
            param_value = tlv_param_token_amount(obj.param)
        case CalldataDescriptorParamNFTV1():
            param_type = CalldataDescriptorParamType.NFT
            param_value = tlv_param_nft(obj.param)
        case CalldataDescriptorParamDatetimeV1():
            param_type = CalldataDescriptorParamType.DATETIME
            param_value = tlv_param_datetime(obj.param)
        case CalldataDescriptorParamDurationV1():
            param_type = CalldataDescriptorParamType.DURATION
            param_value = tlv_param_duration(obj.param)
        case CalldataDescriptorParamUnitV1():
            param_type = CalldataDescriptorParamType.UNIT
            param_value = tlv_param_unit(obj.param)
        case CalldataDescriptorParamEnumV1():
            param_type = CalldataDescriptorParamType.ENUM
            param_value = tlv_param_enum(obj.param)
        case CalldataDescriptorParamTrustedNameV1():
            param_type = CalldataDescriptorParamType.TRUSTED_NAME
            param_value = tlv_param_trusted_name(obj.param)
        case _:
            assert_never(obj.param)

    out += tlv(CalldataDescriptorFieldTag.PARAM_TYPE, param_type.value.to_bytes(1))
    out += tlv(CalldataDescriptorFieldTag.PARAM, param_value)

    return out


def tlv_param_raw(obj: CalldataDescriptorParamRawV1) -> bytes:
    """
    Encode a struct of type PARAM_RAW.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamRawTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamRawTag.VALUE, tlv_value(obj.value))
    return out


def tlv_param_amount(obj: CalldataDescriptorParamAmountV1) -> bytes:
    """
    Encode a struct of type PARAM_AMOUNT.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamAmountTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamAmountTag.VALUE, tlv_value(obj.value))
    return out


def tlv_param_token_amount(obj: CalldataDescriptorParamTokenAmountV1) -> bytes:
    """
    Encode a struct of type PARAM_TOKEN_AMOUNT.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamTokenAmountTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamTokenAmountTag.VALUE, tlv_value(obj.value))

    if (token := obj.token) is not None:
        out += tlv(CalldataDescriptorParamTokenAmountTag.TOKEN, tlv_value(token))

    if (native_currencies := obj.native_currencies) is not None:
        for currency in native_currencies:
            out += tlv(CalldataDescriptorParamTokenAmountTag.NATIVE_CURRENCY, from_hex(currency))

    if (threshold := obj.threshold) is not None:
        out += tlv(CalldataDescriptorParamTokenAmountTag.THRESHOLD, from_hex(threshold))

    if (above_threshold_message := obj.above_threshold_message) is not None:
        out += tlv(CalldataDescriptorParamTokenAmountTag.ABOVE_THRESHOLD_MSG, above_threshold_message)

    return out


def tlv_param_nft(obj: CalldataDescriptorParamNFTV1) -> bytes:
    """
    Encode a struct of type PARAM_NFT.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamNFTTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamNFTTag.VALUE, tlv_value(obj.value))
    out += tlv(CalldataDescriptorParamNFTTag.COLLECTION, tlv_value(obj.collection))
    return out


def tlv_param_datetime(obj: CalldataDescriptorParamDatetimeV1) -> bytes:
    """
    Encode a struct of type PARAM_DATETIME.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamDateTimeTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamDateTimeTag.VALUE, tlv_value(obj.value))
    out += tlv(CalldataDescriptorParamDateTimeTag.TYPE, obj.date_type.to_bytes(1))
    return out


def tlv_param_duration(obj: CalldataDescriptorParamDurationV1) -> bytes:
    """
    Encode a struct of type PARAM_DURATION.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamDurationTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamDurationTag.VALUE, tlv_value(obj.value))
    return out


def tlv_param_unit(obj: CalldataDescriptorParamUnitV1) -> bytes:
    """
    Encode a struct of type PARAM_UNIT.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamUnitTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamUnitTag.VALUE, tlv_value(obj.value))
    out += tlv(CalldataDescriptorParamUnitTag.BASE, obj.base)

    if (decimals := obj.decimals) is not None:
        out += tlv(CalldataDescriptorParamUnitTag.DECIMALS, decimals.to_bytes(1))

    if (prefix := obj.prefix) is not None:
        out += tlv(CalldataDescriptorParamUnitTag.PREFIX, prefix.to_bytes(1))

    return out


def tlv_param_enum(obj: CalldataDescriptorParamEnumV1) -> bytes:
    """
    Encode a struct of type PARAM_ENUM.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamEnumTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamEnumTag.VALUE, tlv_value(obj.value))
    out += tlv(CalldataDescriptorParamEnumTag.ID, obj.id.to_bytes(1))
    return out


def tlv_param_trusted_name(obj: CalldataDescriptorParamTrustedNameV1) -> bytes:
    """
    Encode a struct of type PARAM_TRUSTED_NAME.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorParamTrustedNameTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorParamTrustedNameTag.VALUE, tlv_value(obj.value))

    out_types = bytearray()
    for name_type in obj.types:
        out_types += TrustedNameType(name_type).int_value.to_bytes(1)
    out += tlv(CalldataDescriptorParamTrustedNameTag.TYPES, out_types)

    out_sources = bytearray()
    for name_source in obj.sources:
        out_sources += TrustedNameSource(name_source).int_value.to_bytes(1)
    out += tlv(CalldataDescriptorParamTrustedNameTag.SOURCES, out_sources)

    return out


def tlv_value(obj: CalldataDescriptorValueV1) -> bytes:
    """
    Encode a struct of type VALUE.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    out += tlv(CalldataDescriptorValueTag.VERSION, obj.version.to_bytes(1))
    out += tlv(CalldataDescriptorValueTag.TYPE_FAMILY, obj.type_family.value.to_bytes(1))

    if (type_size := obj.type_size) is not None:
        try:
            out += tlv(CalldataDescriptorValueTag.TYPE_SIZE, type_size.to_bytes(1))
        except OverflowError:
            raise OverflowError(f"Type {obj.type_family} with size {type_size} bits is too big to convert") from None

    match obj:
        case CalldataDescriptorValuePathV1() as path:
            match path.binary_path:
                case CalldataDescriptorContainerPathV1() as container_path:
                    out += tlv(CalldataDescriptorValueTag.CONTAINER_PATH, container_path.value.to_bytes(1))
                case CalldataDescriptorDataPathV1() as data_path:
                    out_path = bytearray()
                    out_path += tlv(CalldataDescriptorPathElementTag.VERSION, path.version.to_bytes(1))
                    for element in data_path.elements:
                        out_path += tlv_data_path_element(element)
                    out += tlv(CalldataDescriptorValueTag.DATA_PATH, out_path)
                case _:
                    assert_never(path.binary_path)
        case CalldataDescriptorValueConstantV1() as constant:
            out += tlv(CalldataDescriptorValueTag.CONSTANT, from_hex(constant.raw))
        case _:
            assert_never(obj)

    return out


def tlv_data_path_element(obj: CalldataDescriptorPathElementV1) -> bytes:
    """
    Encode a struct of type PATH_ELEMENT.

    @param obj: object representation of struct
    @return: encoded struct TLV
    """
    out = bytearray()
    match obj:
        case CalldataDescriptorPathElementTupleV1() as tup:
            out += tlv(CalldataDescriptorPathElementTag.TUPLE, tup.offset.to_bytes(2))

        case CalldataDescriptorPathElementArrayV1() as arr:
            array_out = bytearray()
            array_out += tlv(CalldataDescriptorPathArrayElementTag.WEIGHT, arr.weight.to_bytes(1))

            if (start := arr.start) is not None:
                array_out += tlv(CalldataDescriptorPathArrayElementTag.START, start.to_bytes(2, signed=True))

            if (end := arr.end) is not None:
                array_out += tlv(CalldataDescriptorPathArrayElementTag.END, end.to_bytes(2, signed=True))

            out += tlv(CalldataDescriptorPathElementTag.ARRAY, bytes(array_out))

        case CalldataDescriptorPathElementRefV1():
            out += tlv(CalldataDescriptorPathElementTag.REF)

        case CalldataDescriptorPathElementLeafV1() as leaf:
            out += tlv(CalldataDescriptorPathElementTag.LEAF, leaf.leaf_type.value.to_bytes(1))

        case CalldataDescriptorPathElementSliceV1() as slice:
            slice_out = bytearray()

            if (start := slice.start) is not None:
                slice_out += tlv(CalldataDescriptorPathSliceElementTag.START, start.to_bytes(2, signed=True))

            if (end := slice.end) is not None:
                slice_out += tlv(CalldataDescriptorPathSliceElementTag.END, end.to_bytes(2, signed=True))

            out += tlv(CalldataDescriptorPathElementTag.SLICE, bytes(slice_out))

        case _:
            assert_never(obj)
    return out
