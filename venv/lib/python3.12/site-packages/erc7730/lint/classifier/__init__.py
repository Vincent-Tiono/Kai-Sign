from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import Generic, TypeVar

from erc7730.model.abi import ABI
from erc7730.model.context import EIP712Schema


class TxClass(StrEnum):
    STAKE = auto()
    SWAP = auto()
    PERMIT = auto()
    WITHDRAW = auto()


Schema = TypeVar("Schema", list[ABI], EIP712Schema)


class Classifier(ABC, Generic[Schema]):
    """Given a schema (which is an EIP712 schema or an ABI schema), classify the transaction type
    with some predefined ruleset.
    """

    @abstractmethod
    def classify(self, schema: Schema) -> TxClass | None:
        raise NotImplementedError()
