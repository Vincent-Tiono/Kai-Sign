from typing import Annotated

from pydantic import AfterValidator, Field

from erc7730.model.paths import ContainerPath, DataPath


def _validate_absolute(path: ContainerPath | DataPath) -> ContainerPath | DataPath:
    if isinstance(path, ContainerPath):
        return path
    if isinstance(path, DataPath):
        if not path.absolute:
            raise ValueError("A resolved data path must be absolute")
        return path
    raise ValueError(f"Invalid path type: {type(path)}")


ResolvedPath = Annotated[
    ContainerPath | DataPath,
    Field(
        title="Resolved Path",
        description="A path in the input designating value(s) either in the container of the structured data to be"
        "signed or the structured data schema (ABI path for contracts, path in the message types itself for EIP-712).",
        discriminator="type",
    ),
    AfterValidator(_validate_absolute),
]
