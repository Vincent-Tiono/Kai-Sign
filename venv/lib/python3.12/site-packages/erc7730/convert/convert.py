from pathlib import Path

from rich import print

from erc7730.common.output import ConsoleOutputAdder, RaisingOutputAdder
from erc7730.common.pydantic import model_to_json_file
from erc7730.convert import ERC7730Converter, InputType, OutputType


def convert_to_file_and_print_errors(
    input_descriptor: InputType, output_file: Path, converter: ERC7730Converter[InputType, OutputType]
) -> bool:
    """
    Convert an input descriptor to an output file using a converter, and print any errors encountered.

    :param input_descriptor: loaded, valid input descriptor
    :param output_file: output file path (overwritten if already exists)
    :param converter: converter to use
    :return: True if output file was written (if no errors, or only non-fatal errors encountered)
    """
    if (output_descriptor := convert_and_print_errors(input_descriptor, converter)) is not None:
        if isinstance(output_descriptor, dict):
            for identifier, descriptor in output_descriptor.items():
                descriptor_file = output_file.with_suffix(f".{identifier}{output_file.suffix}")
                model_to_json_file(descriptor_file, descriptor)
                print(f"[green]generated {descriptor_file} ✅[/green]")
        else:
            model_to_json_file(output_file, output_descriptor)
            print(f"[green]generated {output_file} ✅[/green]")
        return True

    print("[red]conversion failed ❌[/red]")
    return False


def convert_and_print_errors(
    input_descriptor: InputType, converter: ERC7730Converter[InputType, OutputType]
) -> OutputType | dict[str, OutputType] | None:
    """
    Convert an input descriptor using a converter, print any errors encountered, and return the result model.

    :param input_descriptor: loaded, valid input descriptor
    :param converter: converter to use
    :return: output descriptor (if no errors, or only non-fatal errors encountered), None otherwise
    """
    return _normalize_result(converter.convert(input_descriptor, ConsoleOutputAdder()))


def convert_and_raise_errors(
    input_descriptor: InputType, converter: ERC7730Converter[InputType, OutputType]
) -> OutputType | dict[str, OutputType] | None:
    """
    Convert an input descriptor using a converter, raising any errors encountered, and return the result model.

    :param input_descriptor: loaded, valid input descriptor
    :param converter: converter to use
    :return: output descriptor (if no errors, or only non-fatal errors encountered), None otherwise
    """
    return _normalize_result(converter.convert(input_descriptor, RaisingOutputAdder()))


def _normalize_result(result: OutputType | dict[str, OutputType] | None) -> OutputType | dict[str, OutputType] | None:
    if isinstance(result, dict):
        match len(result):
            case 0:
                return None
            case 1:
                return next(iter(result.values()))
            case _:
                return result
    return result
