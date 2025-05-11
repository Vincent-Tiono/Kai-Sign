"""
Base model for library, using pydantic.

See https://docs.pydantic.dev
"""

from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict

from eip712.common.pydantic import (
    model_from_json_file,
    model_from_json_file_or_none,
    model_to_json_file,
    model_to_json_str,
)


class Model(BaseModel):
    """
    Base model for library, using pydantic.

    See https://docs.pydantic.dev
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        validate_default=True,
        validate_return=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
        allow_inf_nan=False,
    )

    @classmethod
    def load(cls, path: Path) -> Self:
        """
        Load a model from a JSON file.

        :param path: file path
        :return: validated in-memory representation of model
        :raises Exception: if the file does not exist or has validation errors
        """
        return model_from_json_file(path, cls)

    @classmethod
    def load_or_none(cls, path: Path) -> Self | None:
        """
        Load a model from a JSON file.

        :param path: file path
        :return: validated in-memory representation of descriptor, or None if file does not exist
        :raises Exception: if the file has validation errors
        """
        return model_from_json_file_or_none(path, cls)

    def save(self, path: Path) -> None:
        """
        Write a model to a JSON file, creating parent directories as needed.
        """
        model_to_json_file(path, self)

    def to_json_string(self) -> str:
        """
        Serialize the model to a JSON string.

        :return: JSON representation of model, serialized as a string
        """
        return model_to_json_str(self)
