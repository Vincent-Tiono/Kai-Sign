from typing import Annotated

from pydantic import Field as PydanticField
from pydantic import GetPydanticSchema
from pydantic_core import core_schema
from pydantic_core.core_schema import (
    chain_schema,
    is_instance_schema,
    json_or_python_schema,
    no_info_plain_validator_function,
    str_schema,
    to_string_ser_schema,
)

from erc7730.common.pydantic import ErrorTypeLabel
from erc7730.model.paths import ContainerPath, DataPath, DescriptorPath
from erc7730.model.paths.path_parser import to_path

CONTAINER_PATH_STR_JSON_SCHEMA = chain_schema(
    [str_schema(), no_info_plain_validator_function(to_path), is_instance_schema(ContainerPath)]
)
CONTAINER_PATH_STR_CORE_SCHEMA = json_or_python_schema(
    json_schema=CONTAINER_PATH_STR_JSON_SCHEMA,
    python_schema=core_schema.union_schema([is_instance_schema(ContainerPath), CONTAINER_PATH_STR_JSON_SCHEMA]),
    serialization=to_string_ser_schema(),
)
ContainerPathStr = Annotated[
    ContainerPath,
    GetPydanticSchema(lambda _type, _handler: CONTAINER_PATH_STR_CORE_SCHEMA),
    PydanticField(
        title="Input Path",
        description="A path applying to the container of the structured data to be signed. Such paths are prefixed "
        """with "@".""",
    ),
    ErrorTypeLabel(
        "path applying to the container of the structured data to be signed, such as " + '"@.to" or "@.value".'
    ),
]

DATA_PATH_STR_JSON_SCHEMA = chain_schema(
    [str_schema(), no_info_plain_validator_function(to_path), is_instance_schema(DataPath)]
)
DATA_PATH_STR_CORE_SCHEMA = json_or_python_schema(
    json_schema=DATA_PATH_STR_JSON_SCHEMA,
    python_schema=core_schema.union_schema([is_instance_schema(DataPath), DATA_PATH_STR_JSON_SCHEMA]),
    serialization=to_string_ser_schema(),
)
DataPathStr = Annotated[
    DataPath,
    GetPydanticSchema(lambda _type, _handler: DATA_PATH_STR_CORE_SCHEMA),
    PydanticField(
        title="Data Path",
        description="A path applying to the structured data schema (ABI path for contracts, path in the message types "
        "itself for EIP-712). A data path can reference multiple values if it contains array elements or slices. Such "
        """paths are prefixed with "#".""",
    ),
    ErrorTypeLabel("data path referencing a value in the structured data schema, such as " + '"#.foo.[0].bar.[0:-1]".'),
]

DESCRIPTOR_PATH_STR_JSON_SCHEMA = chain_schema(
    [str_schema(), no_info_plain_validator_function(to_path), is_instance_schema(DescriptorPath)]
)
DESCRIPTOR_PATH_STR_CORE_SCHEMA = json_or_python_schema(
    json_schema=DESCRIPTOR_PATH_STR_JSON_SCHEMA,
    python_schema=core_schema.union_schema([is_instance_schema(DescriptorPath), DESCRIPTOR_PATH_STR_JSON_SCHEMA]),
    serialization=to_string_ser_schema(),
)
DescriptorPathStr = Annotated[
    DescriptorPath,
    GetPydanticSchema(lambda _type, _handler: DESCRIPTOR_PATH_STR_CORE_SCHEMA),
    PydanticField(
        title="Descriptor Path",
        description="A path applying to the current file describing the structured data formatting, after merging "
        "with includes. A descriptor path can only reference a single value in the document. Such paths are prefixed "
        """with "$".""",
        examples=["$.foo.bar"],
    ),
    ErrorTypeLabel(
        "descriptor path referencing a value in the descriptor document using jsonpath syntax, such as "
        + '"$.foo.bar".'
    ),
]
