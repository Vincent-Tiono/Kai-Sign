"""
Base types for ERC-7730 descriptors.

Specification: https://github.com/LedgerHQ/clear-signing-erc7730-registry/tree/master/specs
JSON schema: https://github.com/LedgerHQ/clear-signing-erc7730-registry/blob/master/specs/erc7730-v1.schema.json
"""

from typing import Annotated

from pydantic import BeforeValidator, Field

from erc7730.common.pydantic import ErrorTypeLabel

Id = Annotated[
    str,
    Field(
        title="Id",
        description="An internal identifier that can be used either for clarity specifying what the element is or as a "
        "reference in device specific sections.",
        min_length=1,
        examples=["some_identifier"],
    ),
    ErrorTypeLabel('identifier, such as "some_identifier".'),
]

MixedCaseAddress = Annotated[
    str,
    Field(
        title="Contract Address",
        description="An Ethereum contract address, can be lowercase or EIP-55.",
        min_length=42,
        max_length=42,
        pattern=r"^0x[a-fA-F0-9]+$",
    ),
    ErrorTypeLabel(
        '20 bytes, hexadecimal Ethereum address prefixed with "0x" (EIP-55 or lowercase), such as '
        + '"0xdac17f958d2ee523a2206206994597c13d831ec7".'
    ),
]

Address = Annotated[
    str,
    Field(
        title="Contract Address",
        description="An Ethereum contract address (normalized to lowercase).",
        min_length=42,
        max_length=42,
        pattern=r"^0x[a-f0-9]+$",
    ),
    BeforeValidator(lambda v: v.lower()),
    ErrorTypeLabel(
        '20 bytes, lowercase hexadecimal Ethereum address prefixed with "0x", such as '
        + '"0xdac17f958d2ee523a2206206994597c13d831ec7".'
    ),
]

Selector = Annotated[
    str,
    Field(
        title="Selector",
        description="An Ethereum contract function identifier, in 4 bytes, hex encoded form.",
        min_length=10,
        max_length=10,
        pattern=r"^0x[a-z0-9]+$",
    ),
    ErrorTypeLabel(
        '4 bytes, lowercase hexadecimal Ethereum function selector prefixed with "0x", such as ' + '"0xdac17f95".'
    ),
]

HexStr = Annotated[
    str,
    Field(
        title="Hexadecimal string",
        description="A byte array encoded as an hexadecimal string.",
        pattern=r"^0x[a-f0-9]+$",
    ),
    BeforeValidator(lambda v: v.lower()),
    ErrorTypeLabel('lowercase hexadecimal string prefixed with "0x", such as "0xdac17f95".'),
]

ScalarType = str | int | bool | float
