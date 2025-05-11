import re
import threading
from builtins import print as builtin_print
from contextlib import AbstractContextManager
from enum import IntEnum, auto
from itertools import groupby
from types import TracebackType
from typing import assert_never, final, override

from pydantic import BaseModel, ConfigDict, FilePath, ValidationError
from pydantic_core import ErrorDetails
from rich import print

MUX = threading.Lock()


class Output(BaseModel):
    """An output info/debug/warning/error."""

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        validate_default=True,
        validate_return=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
        allow_inf_nan=False,
    )

    class Level(IntEnum):
        """ERC7730Linter output level."""

        DEBUG = auto()
        INFO = auto()
        WARNING = auto()
        ERROR = auto()

    file: FilePath | None
    line: int | None
    title: str | None
    message: str
    level: Level = Level.ERROR


class OutputAdder:
    """An output debug/info/warning/error sink."""

    def __init__(self) -> None:
        self.has_infos = False
        self.has_warnings = False
        self.has_errors = False

    def add(self, output: Output) -> None:
        match output.level:
            case Output.Level.DEBUG:
                pass
            case Output.Level.INFO:
                self.has_infos = True
            case Output.Level.WARNING:
                self.has_warnings = True
            case Output.Level.ERROR:
                self.has_errors = True
            case _:
                assert_never(output.level)

    @final
    def debug(
        self, message: str, file: FilePath | None = None, line: int | None = None, title: str | None = None
    ) -> None:
        self.add(Output(file=file, line=line, title=title, message=message, level=Output.Level.DEBUG))

    @final
    def info(
        self, message: str, file: FilePath | None = None, line: int | None = None, title: str | None = None
    ) -> None:
        self.add(Output(file=file, line=line, title=title, message=message, level=Output.Level.INFO))

    @final
    def warning(
        self, message: str, file: FilePath | None = None, line: int | None = None, title: str | None = None
    ) -> None:
        self.add(Output(file=file, line=line, title=title, message=message, level=Output.Level.WARNING))

    @final
    def error(
        self, message: str, file: FilePath | None = None, line: int | None = None, title: str | None = None
    ) -> None:
        self.add(Output(file=file, line=line, title=title, message=message, level=Output.Level.ERROR))


@final
class ListOutputAdder(OutputAdder):
    """An output adder that stores outputs in a list."""

    def __init__(self) -> None:
        super().__init__()
        self.outputs: list[Output] = []

    def add(self, output: Output) -> None:
        super().add(output)
        self.outputs.append(output)


@final
class SetOutputAdder(OutputAdder):
    """An output adder that stores outputs in a set."""

    def __init__(self) -> None:
        super().__init__()
        self.outputs: set[Output] = set()

    def add(self, output: Output) -> None:
        super().add(output)
        self.outputs.add(output)


class ConsoleOutputAdder(OutputAdder):
    """An output adder that prints to the console."""

    @override
    def add(self, output: Output) -> None:
        super().add(output)
        match output.level:
            case Output.Level.DEBUG:
                style = "italic"
                prefix = "⚪️ "
            case Output.Level.INFO:
                style = "blue"
                prefix = "🔵 "
            case Output.Level.WARNING:
                style = "yellow"
                prefix = "🟠 warning: "
            case Output.Level.ERROR:
                style = "red"
                prefix = "🔴 error: "
            case _:
                assert_never(output.level)

        log = f"[{style}]{prefix}"
        context = []
        if output.file is not None:
            context.append(f"{output.file}")
        if output.line is not None:
            context.append(f"line {output.line}")
        if context:
            log += ", ".join(context) + ": "
        if output.title is not None:
            log += f"{output.title}: "
        log += f"[/{style}]"
        if "\n" in output.message:
            log += "\n"
        log += output.message

        print(log)


class RaisingOutputAdder(ConsoleOutputAdder):
    """An output adder that raises warnings/errors, otherwise prints to the console."""

    @override
    def add(self, output: Output) -> None:
        super().add(output)
        match output.level:
            case Output.Level.DEBUG | Output.Level.INFO:
                super().add(output)
            case Output.Level.WARNING | Output.Level.ERROR:
                log = f"{output.level.name}: "
                if output.file is not None:
                    log += f"file={output.file.name}"
                if output.line is not None:
                    log += f"line {output.line}: "
                if output.title is not None:
                    log += f"{output.title}: "
                log += f"{output.message}"
                raise Exception(log)
            case _:
                assert_never(output.level)


@final
class GithubAnnotationsAdder(OutputAdder):
    """An output adder that formats errors to be parsed as Github annotations."""

    @override
    def add(self, output: Output) -> None:
        super().add(output)

        match output.level:
            case Output.Level.DEBUG:
                return
            case Output.Level.INFO:
                lvl = "notice"
            case Output.Level.WARNING:
                lvl = "warning"
            case Output.Level.ERROR:
                lvl = "error"
            case _:
                assert_never(output.level)

        log = f"::{lvl} "
        if output.file is not None:
            log += f"file={output.file}"
        if output.line is not None:
            log += f",line={output.line}"
        if output.title is not None:
            log += f",title={output.title}"
        message = output.message.replace("\n", "%0A")
        log += f"::{message}"

        builtin_print(log)


class AddFileOutputAdder(OutputAdder):
    """An output adder wrapper that adds a specific file to all outputs."""

    def __init__(self, delegate: OutputAdder, file: FilePath) -> None:
        super().__init__()
        self.delegate: OutputAdder = delegate
        self.file: FilePath = file

    @override
    def add(self, output: Output) -> None:
        super().add(output)
        self.delegate.add(output.model_copy(update={"file": self.file}))


class DropFileOutputAdder(OutputAdder):
    """An output adder wrapper that drops file information from all outputs."""

    def __init__(self, delegate: OutputAdder) -> None:
        super().__init__()
        self.delegate: OutputAdder = delegate

    @override
    def add(self, output: Output) -> None:
        super().add(output)
        self.delegate.add(output.model_copy(update={"file": None}))


@final
class BufferAdder(AbstractContextManager[OutputAdder]):
    """A context manager that buffers outputs and outputs them all at once, sorted and deduplicated."""

    def __init__(self, delegate: OutputAdder, prolog: str | None = None, epilog: str | None = None) -> None:
        self._buffer = SetOutputAdder()
        self._delegate = delegate
        self._prolog = prolog
        self._epilog = epilog

    @override
    def __enter__(self) -> OutputAdder:
        return self._buffer

    @override
    def __exit__(self, etype: type[BaseException] | None, e: BaseException | None, tb: TracebackType | None) -> None:
        MUX.acquire()
        try:
            if self._prolog is not None:
                print(self._prolog)
            if self._buffer.outputs:
                for output in sorted(self._buffer.outputs, key=lambda x: (x.file, x.line, x.level, x.title, x.message)):
                    self._delegate.add(output)
            else:
                print("no issue found ✔️")
            if self._epilog is not None:
                print(self._epilog)
        finally:
            MUX.release()
        return None


@final
class ExceptionsToOutput(AbstractContextManager[None]):
    """A context manager that catches exceptions and redirects them to an OutputAdder."""

    def __init__(self, delegate: OutputAdder) -> None:
        self._delegate = delegate

    @override
    def __enter__(self) -> None:
        return None

    @override
    def __exit__(self, etype: type[BaseException] | None, e: BaseException | None, tb: TracebackType | None) -> bool:
        if isinstance(e, Exception):
            exception_to_output(e, self._delegate)
            return True
        return False


def exception_to_output(e: Exception, out: OutputAdder) -> None:
    """
    Sanitize an exception and add it to an OutputAdder.

    :param e: exception to handle
    :param out: output handler
    """
    match e:
        case ValidationError() as e:
            pydantic_error_to_output(e, out)
        case Exception() as e:
            out.error(title="Failed processing descriptor", message=str(e))
        case _:
            assert_never(e)


def pydantic_error_to_output(e: ValidationError, out: OutputAdder) -> None:
    """
    Sanitize a pydantic validation exception and add it to an OutputAdder.

    This cleans up location, and groups errors by location to avoid outputting multiple errors when not necessary, for
    instance for union types.

    :param e: exception to handle
    :param out: output handler
    """

    def filter_location(loc: int | str) -> bool:
        if isinstance(loc, int):
            return True
        return bool(re.match(r"(list|set)\[.*", loc))

    def get_location(ex: ErrorDetails) -> str:
        if not (loc := ex.get("loc")):
            return "unknown location"
        return ".".join(map(str, filter(filter_location, loc[:-1])))

    def get_value(ex: ErrorDetails) -> str:
        return str(ex.get("input", "unknown value"))

    def get_details(ex: ErrorDetails) -> str:
        return ex.get("msg", "unknown error")

    def get_message(ex: ErrorDetails) -> str:
        return f"""Value "{get_value(ex)}" is not valid: {get_details(ex)}"""

    for location, location_errors in groupby(e.errors(include_url=False), get_location):
        if (len(errors := list(location_errors))) > 1:
            out.error(title=f"Invalid value at {location}", message="* " + "\n * ".join(map(get_message, errors)))
        else:
            out.error(title=f"Invalid value at {location}", message=get_message(errors[0]))
