from collections.abc import Generator
from typing import Any, assert_never

from caseswitcher import to_title
from pydantic import TypeAdapter
from pydantic_string_url import HttpUrl

from erc7730.common.abi import ABIDataType, compute_signature, get_functions
from erc7730.common.client import get_contract_abis
from erc7730.generate.schema_tree import (
    SchemaArray,
    SchemaLeaf,
    SchemaStruct,
    SchemaTree,
    abi_function_to_tree,
    eip712_schema_to_tree,
)
from erc7730.model.abi import ABI
from erc7730.model.context import EIP712Schema
from erc7730.model.display import AddressNameType, DateEncoding, FieldFormat
from erc7730.model.input.context import (
    InputContract,
    InputContractContext,
    InputDeployment,
    InputEIP712,
    InputEIP712Context,
)
from erc7730.model.input.descriptor import InputERC7730Descriptor
from erc7730.model.input.display import (
    InputAddressNameParameters,
    InputDateParameters,
    InputDisplay,
    InputField,
    InputFieldDescription,
    InputFieldParameters,
    InputFormat,
    InputNestedFields,
)
from erc7730.model.input.metadata import InputMetadata
from erc7730.model.metadata import OwnerInfo
from erc7730.model.paths import ROOT_DATA_PATH, Array, ArrayElement, ArraySlice, DataPath, Field
from erc7730.model.paths.path_ops import data_path_append
from erc7730.model.types import Address


def generate_descriptor(
    chain_id: int,
    contract_address: Address,
    abi: str | bytes | None = None,
    eip712_schema: str | bytes | None = None,
    owner: str | None = None,
    legal_name: str | None = None,
    url: HttpUrl | None = None,
) -> InputERC7730Descriptor:
    """
    Generate an ERC-7730 descriptor.

    If an EIP-712 schema is provided, an EIP-712 descriptor is generated for this schema, otherwise a calldata
    descriptor. If no ABI is supplied, the ABIs are fetched from Etherscan using the chain id / contract address.

    :param chain_id: contract chain id
    :param contract_address: contract address
    :param abi: JSON ABI string or buffer representation (to generate a calldata descriptor)
    :param eip712_schema: JSON EIP-712 schema string or buffer representation (to generate an EIP-712 descriptor)
    :param owner: the display name of the owner or target of the contract / message to be clear signed
    :param legal_name: the full legal name of the owner if different from the owner field
    :param url: URL with more info on the entity the user interacts with
    :return: a generated ERC-7730 descriptor
    """

    context, trees = _generate_context(chain_id, contract_address, abi, eip712_schema)
    metadata = _generate_metadata(legal_name, owner, url)
    display = _generate_display(trees)

    return InputERC7730Descriptor(context=context, metadata=metadata, display=display)


def _generate_metadata(owner: str | None, legal_name: str | None, url: HttpUrl | None) -> InputMetadata:
    info = OwnerInfo(legalName=legal_name, url=url) if legal_name is not None and url is not None else None
    return InputMetadata(owner=owner, info=info)


def _generate_context(
    chain_id: int, contract_address: Address, abi: str | bytes | None, eip712_schema: str | bytes | None
) -> tuple[InputContractContext | InputEIP712Context, dict[str, SchemaTree]]:
    if eip712_schema is not None:
        return _generate_context_eip712(chain_id, contract_address, eip712_schema)
    return _generate_context_calldata(chain_id, contract_address, abi)


def _generate_context_eip712(
    chain_id: int, contract_address: Address, eip712_schema: str | bytes
) -> tuple[InputEIP712Context, dict[str, SchemaTree]]:
    schemas = TypeAdapter(list[EIP712Schema]).validate_json(eip712_schema)

    context = InputEIP712Context(
        eip712=InputEIP712(schemas=schemas, deployments=[InputDeployment(chainId=chain_id, address=contract_address)])
    )

    trees = {schema.primaryType: eip712_schema_to_tree(schema) for schema in schemas}

    return context, trees


def _generate_context_calldata(
    chain_id: int, contract_address: Address, abi: str | bytes | None
) -> tuple[InputContractContext, dict[str, SchemaTree]]:
    if abi is not None:
        abis = TypeAdapter(list[ABI]).validate_json(abi)

    elif (abis := get_contract_abis(chain_id, contract_address)) is None:
        raise Exception("Failed to fetch contract ABIs")

    functions = list(get_functions(abis).functions.values())

    context = InputContractContext(
        contract=InputContract(abi=functions, deployments=[InputDeployment(chainId=chain_id, address=contract_address)])
    )

    trees = {compute_signature(function): abi_function_to_tree(function) for function in functions}

    return context, trees


def _generate_display(trees: dict[str, SchemaTree]) -> InputDisplay:
    return InputDisplay(formats=_generate_formats(trees))


def _generate_formats(trees: dict[str, SchemaTree]) -> dict[str, InputFormat]:
    formats: dict[str, InputFormat] = {}
    for name, tree in trees.items():
        if fields := list(_generate_fields(schema=tree, path=ROOT_DATA_PATH)):
            formats[name] = InputFormat(fields=fields)
    return formats


def _generate_fields(schema: SchemaTree, path: DataPath) -> Generator[InputField, Any, Any]:
    match schema:
        case SchemaStruct(components=components) if path == ROOT_DATA_PATH:
            for name, component in components.items():
                if name:
                    yield from _generate_fields(component, data_path_append(path, Field(identifier=name)))

        case SchemaStruct(components=components):
            fields = [
                field
                for name, component in components.items()
                for field in _generate_fields(component, DataPath(absolute=False, elements=[Field(identifier=name)]))
                if name
            ]
            yield InputNestedFields(path=path, fields=fields)

        case SchemaArray(component=component):
            match component:
                case SchemaStruct() | SchemaArray():
                    yield InputNestedFields(
                        path=data_path_append(path, Array()),
                        fields=list(_generate_fields(component, DataPath(absolute=False, elements=[]))),
                    )
                case SchemaLeaf():
                    yield from _generate_fields(component, data_path_append(path, Array()))
                case _:
                    assert_never(schema)

        case SchemaLeaf(data_type=data_type):
            name = _get_leaf_name(path)
            format, params = _generate_field(name, data_type)
            yield InputFieldDescription(path=path, label=name, format=format, params=params)

        case _:
            assert_never(schema)


def _generate_field(name: str, data_type: ABIDataType) -> tuple[FieldFormat, InputFieldParameters | None]:
    match data_type:
        case ABIDataType.UINT | ABIDataType.INT:
            # other applicable formats could be TOKEN_AMOUNT, UNIT or ENUM, but we can't tell

            if _contains_any_of(name, "duration"):
                return FieldFormat.DURATION, None

            if _contains_any_of(name, "height"):
                return FieldFormat.DATE, InputDateParameters(encoding=DateEncoding.BLOCKHEIGHT)

            if _contains_any_of(name, "deadline", "expiration", "until", "time", "timestamp"):
                return FieldFormat.DATE, InputDateParameters(encoding=DateEncoding.TIMESTAMP)

            if _contains_any_of(name, "amount", "value", "price"):
                return FieldFormat.AMOUNT, None

            return FieldFormat.RAW, None

        case ABIDataType.UFIXED | ABIDataType.FIXED:
            return FieldFormat.RAW, None

        case ABIDataType.ADDRESS:
            if _contains_any_of(name, "collection", "nft"):
                return FieldFormat.NFT_NAME, InputAddressNameParameters(types=[AddressNameType.COLLECTION])

            if _contains_any_of(name, "spender"):
                return FieldFormat.ADDRESS_NAME, InputAddressNameParameters(types=[AddressNameType.CONTRACT])

            if _contains_any_of(name, "asset", "token"):
                return FieldFormat.ADDRESS_NAME, InputAddressNameParameters(types=[AddressNameType.TOKEN])

            if _contains_any_of(name, "from", "to", "owner", "recipient", "receiver", "account"):
                return FieldFormat.ADDRESS_NAME, InputAddressNameParameters(
                    types=[AddressNameType.EOA, AddressNameType.WALLET]
                )

            return FieldFormat.ADDRESS_NAME, InputAddressNameParameters(types=list(AddressNameType))

        case ABIDataType.BOOL:
            return FieldFormat.RAW, None

        case ABIDataType.BYTES:
            if _contains_any_of(name, "calldata"):
                return FieldFormat.CALL_DATA, None

            return FieldFormat.RAW, None

        case ABIDataType.STRING:
            return FieldFormat.RAW, None

        case _:
            assert_never(data_type)


def _get_leaf_name(path: DataPath) -> str:
    for element in reversed(path.elements):
        match element:
            case Field(identifier=name):
                return to_title(name).strip()
            case Array() | ArrayElement() | ArraySlice():
                continue
            case _:
                assert_never(element)
    return "unknown"


def _contains_any_of(name: str, *values: str) -> bool:
    name_lower = name.lower()
    return any(value in name_lower for value in values)
