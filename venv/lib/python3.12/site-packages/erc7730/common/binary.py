"""Utilities for binary data manipulation."""

from enum import IntEnum


def from_hex(value: str) -> bytes:
    """
    Convert an hex string to a byte array.

    @param value: hex string (can be prefixed with 0x or not)
    @return: decoded byte array
    """
    return bytes.fromhex(value.removeprefix("0x"))


def tlv(tag: int | IntEnum, *value: bytes | str | None) -> bytes:
    """
    Encode a value in TLV format (Tag-Length-Value)

    If value is not encoded, it will be encoded as ASCII.
    If input string is not ASCII, and UnicodeEncodeError is raised.

    If encoded value is longer than 255 bytes, an OverflowError is raised.

    @param tag: the tag (can be an enum)
    @param value: the value (can be already encoded, or a string)
    @return: encoded TLV
    """
    values_encoded = bytearray()
    for v in value:
        if v is not None:
            values_encoded.extend(v.encode("ascii", errors="strict") if isinstance(v, str) else v)
    return (
        (tag.value if isinstance(tag, IntEnum) else tag).to_bytes(1, "big")
        + len(values_encoded).to_bytes(1, "big")
        + values_encoded
    )


def length_value(value: bytes | str | None) -> bytes:
    """
    Prepend the length of the value encoded on 1 byte to the value itself.

    If value is not encoded, it will be encoded as ASCII.
    If input string is not ASCII, and UnicodeEncodeError is raised.

    If encoded value is longer than 255 bytes, an OverflowError is raised.

    @param value: the value (can be already encoded, or a string)
    @return: encoded TLV
    """
    if value is None:
        return (0).to_bytes(1, "big")
    value_encoded = value.encode("ascii", errors="strict") if isinstance(value, str) else value
    return len(value_encoded).to_bytes(1, "big") + value_encoded
