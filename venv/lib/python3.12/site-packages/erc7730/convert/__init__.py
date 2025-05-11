from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from erc7730.common.output import OutputAdder

InputType = TypeVar("InputType", bound=BaseModel)
OutputType = TypeVar("OutputType", bound=BaseModel)


class ERC7730Converter(ABC, Generic[InputType, OutputType]):
    """
    Converter from/to ERC-7730 descriptor.

    A converter may fail partially, in which case it should emit errors with ERROR level, or totally, in which case it
    should emit errors with FATAL level.
    """

    @abstractmethod
    def convert(self, descriptor: InputType, out: OutputAdder) -> OutputType | dict[str, OutputType] | None:
        """
        Convert a descriptor from/to ERC-7730.

        Conversion may fail partially, in which case it should emit errors with WARNING level, or totally, in which case
        it should emit errors with ERROR level.

        Conversion can return a single descriptor, or multiple ones, in the form of a dictionary with unique
        identifiers.

        :param descriptor: input descriptor to convert
        :param out: output sink
        :return: converted descriptor, or None if conversion failed
        """
        raise NotImplementedError()
