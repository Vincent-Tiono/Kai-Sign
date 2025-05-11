from collections.abc import Generator
from pathlib import Path

from rich import print

from erc7730 import ERC_7730_REGISTRY_CALLDATA_PREFIX, ERC_7730_REGISTRY_EIP712_PREFIX
from erc7730.common.output import (
    ConsoleOutputAdder,
    OutputAdder,
)


def list_all(paths: list[Path]) -> bool:
    """
    List all ERC-7730 descriptor files at given paths.

    Paths can be files or directories, in which case all descriptor files in the directory are recursively listed.

    :param paths: paths to search for descriptor files
    :return: true if no error occurred
    """
    out = ConsoleOutputAdder()

    for file in get_erc7730_files(*paths, out=out):
        print(file)

    return not out.has_errors


def get_erc7730_files(*paths: Path, out: OutputAdder) -> Generator[Path, None, None]:
    """
    List all ERC-7730 descriptor files at given paths.

    Paths can be files or directories, in which case all descriptor files in the directory are recursively listed.

    :param paths: paths to search for descriptor files
    :param out: error handler
    """
    for path in paths:
        if path.is_file():
            if is_erc7730_file(path):
                yield path
            else:
                out.error(title="Invalid path", message=f"{path} is not an ERC-7730 descriptor file")
        elif path.is_dir():
            for file in path.rglob("*.json"):
                if is_erc7730_file(file):
                    yield file
        else:
            out.error(title="Invalid path", message=f"{path} is not a file or directory")


def is_erc7730_file(path: Path) -> bool:
    """
    Check if a file is an ERC-7730 descriptor file.

    :param path: file path
    :return: true if the file is an ERC-7730 descriptor file
    """
    return path.is_file() and (
        path.name.startswith(ERC_7730_REGISTRY_CALLDATA_PREFIX) or path.name.startswith(ERC_7730_REGISTRY_EIP712_PREFIX)
    )
