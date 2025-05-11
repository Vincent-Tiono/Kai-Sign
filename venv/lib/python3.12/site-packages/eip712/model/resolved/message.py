from pydantic import Field

from eip712.model.base import Model
from eip712.model.schema import EIP712Schema
from eip712.model.types import EIP712Format, EIP712NameSource, EIP712NameType

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class ResolvedEIP712MapperField(Model):
    """
    EIP-712 mapper field
    """

    path: str
    label: str
    assetPath: str | None = None
    format: EIP712Format | None = None
    coinRef: int | None = None
    nameTypes: list[EIP712NameType] | None = None
    nameSources: list[EIP712NameSource] | None = None


class ResolvedEIP712Mapper(Model):
    """Defines fields to be displayed on device with their mapping to schema fields."""

    label: str
    fields: list[ResolvedEIP712MapperField]


class ResolvedEIP712Message(Model):
    """
    Resolved Descriptor for a single message.

    Defines message fields and how we want to display them on device.
    """

    schema_: EIP712Schema = Field(alias="schema")
    mapper: ResolvedEIP712Mapper
