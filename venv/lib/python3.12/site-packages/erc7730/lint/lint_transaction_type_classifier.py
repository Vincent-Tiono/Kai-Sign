from typing import final, override

from erc7730.common.output import OutputAdder
from erc7730.lint import ERC7730Linter
from erc7730.lint.classifier import TxClass
from erc7730.lint.classifier.abi_classifier import ABIClassifier
from erc7730.lint.classifier.eip712_classifier import EIP712Classifier
from erc7730.model.resolved.context import EIP712Schema, ResolvedContractContext, ResolvedEIP712Context
from erc7730.model.resolved.descriptor import ResolvedERC7730Descriptor
from erc7730.model.resolved.display import ResolvedDisplay, ResolvedFormat


@final
class ClassifyTransactionTypeLinter(ERC7730Linter):
    """- given schema/ABI, classify the transaction type
    - if class found, check descriptor display fields against predefined ruleset
    - possible class (swap, staking withdraw, staking deposit)
    """

    @override
    def lint(self, descriptor: ResolvedERC7730Descriptor, out: OutputAdder) -> None:
        if descriptor.context is None:
            return None
        if (tx_class := self._determine_tx_class(descriptor)) is None:
            # could not determine transaction type
            return None
        if (display := descriptor.display) is None:
            return None
        DisplayFormatChecker(tx_class, display).check(out)

    @classmethod
    def _determine_tx_class(cls, descriptor: ResolvedERC7730Descriptor) -> TxClass | None:
        if isinstance(descriptor.context, ResolvedEIP712Context):
            classifier = EIP712Classifier()
            if descriptor.context.eip712.schemas is not None:
                first_schema = descriptor.context.eip712.schemas[0]
                if isinstance(first_schema, EIP712Schema):
                    return classifier.classify(first_schema)
                # url should have been resolved earlier
        elif isinstance(descriptor.context, ResolvedContractContext):
            abi_classifier = ABIClassifier()
            if descriptor.context.contract.abi is not None:
                return abi_classifier.classify(descriptor.context.contract.abi)
        return None


class DisplayFormatChecker:
    """Given a transaction class and a display formats, check if all the required fields of a given
    transaction class are being displayed.
    If a field is missing emit an error.
    """

    def __init__(self, tx_class: TxClass, display: ResolvedDisplay):
        self.tx_class = tx_class
        self.display = display

    def check(self, out: OutputAdder) -> None:
        match self.tx_class:
            case TxClass.PERMIT:
                formats = self.display.formats
                fields = self._get_all_displayed_fields(formats)
                if not self._fields_contain("spender", fields):
                    out.warning(
                        title="Expected Display field missing",
                        message="Contract detected as Permit but no spender field displayed",
                    )
                if not self._fields_contain("amount", fields):
                    out.warning(
                        title="Expected Display field missing",
                        message="Contract detected as Permit but no amount field displayed",
                    )
                if (
                    not self._fields_contain("valid until", fields)
                    and not self._fields_contain("expiry", fields)
                    and not self._fields_contain("expiration", fields)
                    and not self._fields_contain("deadline", fields)
                ):
                    out.warning(
                        title="Expected Display field missing",
                        message="Contract detected as Permit but no expiration field displayed",
                    )
            case _:
                pass

    @classmethod
    def _get_all_displayed_fields(cls, formats: dict[str, ResolvedFormat]) -> set[str]:
        fields: set[str] = set()
        for format in formats.values():
            if format.fields is not None:
                for field in format.fields:
                    fields.add(str(field))
        return fields

    @classmethod
    def _fields_contain(cls, word: str, fields: set[str]) -> bool:
        """Check if the provided keyword is contained in one of the fields (case insensitive)"""
        return any(word.lower() in field.lower() for field in fields)
