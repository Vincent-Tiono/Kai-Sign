import os
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

from rich import print

from erc7730.common.json import dict_from_json_file, dict_to_json_file
from erc7730.common.output import (
    AddFileOutputAdder,
    BufferAdder,
    ConsoleOutputAdder,
    DropFileOutputAdder,
    ExceptionsToOutput,
    OutputAdder,
)
from erc7730.list.list import get_erc7730_files


def format_all_and_print_errors(paths: list[Path]) -> bool:
    """
    Format all ERC-7730 descriptor files at given paths and print errors.

    :param paths: paths to apply formatter on
    :return: true if not errors occurred
    """
    out = DropFileOutputAdder(delegate=ConsoleOutputAdder())

    count = format_all(paths, out)

    if out.has_errors:
        print(f"[bold][red]formatted {count} descriptor files, some errors occurred ❌[/red][/bold]")
        return False

    if out.has_warnings:
        print(f"[bold][yellow]formatted {count} descriptor files, some warnings occurred ⚠️[/yellow][/bold]")
        return True

    print(f"[bold][green]formatted {count} descriptor files, no errors occurred ✅[/green][/bold]")
    return True


def format_all(paths: list[Path], out: OutputAdder) -> int:
    """
    Format all ERC-7730 descriptor files at given paths.

    Paths can be files or directories, in which case all descriptor files in the directory are recursively formatted.

    :param paths: paths to apply formatter on
    :param out: output adder
    :return: number of files formatted
    """
    files = list(get_erc7730_files(*paths, out=out))

    if len(files) <= 1 or not (root_path := os.path.commonpath(files)):
        root_path = None

    def label(f: Path) -> Path | None:
        return f.relative_to(root_path) if root_path is not None else None

    if len(files) > 1:
        print(f"📝 formatting {len(files)} descriptor files…\n")

    with ThreadPoolExecutor() as executor:
        for future in (executor.submit(format_file, file, out, label(file)) for file in files):
            future.result()

    return len(files)


def format_file(path: Path, out: OutputAdder, show_as: Path | None = None) -> None:
    """
    Format a single ERC-7730 descriptor file.

    :param path: ERC-7730 descriptor file path
    :param show_as: if provided, print this label instead of the file path
    :param out: error handler
    """

    label = path if show_as is None else show_as
    file_out = AddFileOutputAdder(delegate=out, file=path)

    with BufferAdder(file_out, prolog=f"➡️ formatting [bold]{label}[/bold]…", epilog="") as out, ExceptionsToOutput(out):
        dict_to_json_file(path, dict_from_json_file(path))
