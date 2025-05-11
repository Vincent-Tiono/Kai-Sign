from typing import Annotated

from pydantic import Field

from eip712.model.base import Model

# ruff: noqa: N815 - camel case field names are tolerated to match schema


EIP712Type = Annotated[
    str, Field(title="EIP12 Type Identifier", description="An EIP-712 scalar or structured type identifier.")
]


class EIP712SchemaField(Model):
    """
    EIP-712 schema field, which is a tuple of a name and a type.
    """

    name: str = Field(title="Name", description="The EIP-712 field name.")

    type: EIP712Type = Field(title="Type", description="The EIP-712 field type identifier.")


EIP712Schema = dict[EIP712Type, list[EIP712SchemaField]]
