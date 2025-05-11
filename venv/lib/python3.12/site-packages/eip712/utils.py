import hashlib

from pydantic import RootModel

from eip712.common.pydantic import model_to_json_str
from eip712.model.input.descriptor import InputEIP712DAppDescriptor
from eip712.model.instruction import SchemaHash
from eip712.model.resolved.descriptor import ResolvedEIP712DAppDescriptor
from eip712.model.schema import EIP712Schema, EIP712Type


class MissingRootTypeError(RuntimeError):
    """
    Exception raised when a no root type is found.
    """

    pass


class MultipleRootTypesError(RuntimeError):
    """
    Exception raised when multiple root types are found.
    """

    pass


def get_primary_type(schema: EIP712Schema) -> EIP712Type:
    """
    Determines the primary type from a given EIP-712 schema.

    The primary type is the root type that is not referenced by any other type in the schema,
    excluding the "EIP712Domain" type. If there are multiple root types or no root type,
    appropriate exceptions are raised.
    """
    referenced_types = {field.type.rstrip("[]") for _, type_fields in schema.items() for field in type_fields}
    match len(roots := set(schema.keys()) - referenced_types - {"EIP712Domain"}):
        case 0:
            raise MissingRootTypeError("Invalid EIP-712 schema: no root type found.")
        case 1:
            return next(iter(roots))
        case _:
            raise MultipleRootTypesError("Invalid EIP-712 schema: multiple root types found.")


def get_schema_hash(schema: EIP712Schema) -> SchemaHash:
    """
    Computes the schema hash of an EIP-712 schema.
    Schema hash is sha224 of the compact JSON UTF-8 encoded representation of the schema.
    """
    sorted_schema = dict(sorted(schema.items()))
    schema_str = model_to_json_str(RootModel[EIP712Schema](sorted_schema), indent=None)
    return hashlib.sha224(schema_str.encode("utf-8")).hexdigest()


def get_schemas_by_hash(
    descriptor: InputEIP712DAppDescriptor | ResolvedEIP712DAppDescriptor,
) -> dict[SchemaHash, EIP712Schema]:
    """
    Extracts and returns a dictionary of EIP-712 schemas indexed by their hash.
    """
    schema_dict: dict[SchemaHash, EIP712Schema] = {}
    for contract in descriptor.contracts:
        for message in contract.messages:
            schema_dict[get_schema_hash(message.schema_)] = message.schema_
    return schema_dict
