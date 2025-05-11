from typing import final, override

from erc7730.common.output import OutputAdder
from erc7730.lint import ERC7730Linter
from erc7730.model.resolved.descriptor import ResolvedERC7730Descriptor


@final
class MultiLinter(ERC7730Linter):
    """A linter that runs multiple linters in sequence."""

    def __init__(self, linters: list[ERC7730Linter]):
        self.lints = linters

    @override
    def lint(self, descriptor: ResolvedERC7730Descriptor, out: OutputAdder) -> None:
        for linter in self.lints:
            linter.lint(descriptor, out)
