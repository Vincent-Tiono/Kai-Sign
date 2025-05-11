"""Package implementing an object model for ERC-7730 descriptors."""

from enum import StrEnum, auto


class ERC7730ModelType(StrEnum):
    """
    The type of the ERC-7730 model.
    """

    INPUT = auto()
    RESOLVED = auto()
