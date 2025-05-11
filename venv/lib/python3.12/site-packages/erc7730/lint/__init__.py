from abc import ABC, abstractmethod

from erc7730.common.output import OutputAdder
from erc7730.model.resolved.descriptor import ResolvedERC7730Descriptor


class ERC7730Linter(ABC):
    """
    Linter for ERC-7730 descriptors, inspects a (structurally valid) descriptor and emits notes, warnings, or
    errors.

    A linter may emit false positives or false negatives. It is up to the user to interpret the output.
    """

    @abstractmethod
    def lint(self, descriptor: ResolvedERC7730Descriptor, out: OutputAdder) -> None:
        raise NotImplementedError()
