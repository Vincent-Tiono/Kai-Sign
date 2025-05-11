from typing import final, override

from erc7730.lint.classifier import Classifier, TxClass
from erc7730.model.abi import ABI


@final
class ABIClassifier(Classifier[list[ABI]]):
    """Given an ABI, classify the transaction type with some predefined ruleset.
    (not implemented)
    """

    @override
    def classify(self, schema: list[ABI]) -> TxClass | None:
        pass
