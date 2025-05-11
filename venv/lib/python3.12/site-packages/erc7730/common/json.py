import json
import os
from collections.abc import Iterator
from json import JSONEncoder
from pathlib import Path
from typing import Any, override


def read_jsons_with_includes(paths: list[Path]) -> Any:
    """
    Read a list JSON files, recursively inlining any included files.

    Keys from the calling file override those of the included file (the included file defines defaults).
    Keys from the later files in the list override those of the first files.

    Note:
      - circular includes are not detected and will result in a stack overflow.
      - "includes" key can only be used at root level of an object.
    """
    result: dict[str, Any] = {}
    for path in paths:
        # noinspection PyTypeChecker
        result = _merge_dicts(result, read_json_with_includes(path))
    return result


def read_json_with_includes(path: Path) -> Any:
    """
    Read a JSON file, recursively inlining any included files.

    Keys from the calling file override those of the included file (the included file defines defaults).

    If include is a list, files are included in other they are defined, with later files overriding previous files.

    Note:
      - circular includes are not detected and will result in a stack overflow.
      - "includes" key can only be used at root level of an object.
    """
    result: dict[str, Any] = dict_from_json_file(path)
    if isinstance(result, dict) and (includes := result.pop("includes", None)) is not None:
        if isinstance(includes, list):
            parent = read_jsons_with_includes(paths=[path.parent / p for p in includes])
        else:
            # noinspection PyTypeChecker
            parent = read_json_with_includes(path.parent / includes)
        result = _merge_dicts(parent, result)
    return result


def _merge_dicts(d1: dict[str, Any], d2: dict[str, Any]) -> dict[str, Any]:
    """
    Merge d1 and d2, with priority to d2.

    Recursively called when dicts are encountered.

    This function assumes that if the same field is in both dicts, then the types must be the same.
    """
    merged = {}
    for key, val1 in d1.items():
        if (val2 := d2.get(key)) is not None:
            if isinstance(val1, dict):
                merged[key] = _merge_dicts(d1=val1, d2=val2)
            else:
                merged[key] = val2
        else:
            merged[key] = val1
    return {**d2, **merged}


def dict_from_json_str(value: str) -> dict[str, Any]:
    """Deserialize a dict from a JSON string."""
    return json.loads(value)


def dict_from_json_file(path: Path) -> dict[str, Any]:
    """Deserialize a dict from a JSON file."""
    with open(path, "rb") as f:
        return json.load(f)


def dict_to_json_str(values: dict[str, Any]) -> str:
    """Serialize a dict into a JSON string."""
    return json.dumps(values, indent=2, cls=CompactJSONEncoder)


def dict_to_json_file(path: Path, values: dict[str, Any]) -> None:
    """Serialize a dict into a JSON file, creating parent directories as needed."""
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as f:
        f.write(dict_to_json_str(values))
        f.write("\n")


class CompactJSONEncoder(JSONEncoder):
    """A JSON Encoder that puts small containers on single lines."""

    CONTAINER_TYPES = (list, tuple, dict)
    """Container datatypes include primitives or other containers."""

    MAX_WIDTH = 120
    """Maximum width of a container that might be put on a single line."""

    MAX_ITEMS = 10
    """Maximum number of items in container that might be put on single line."""

    PRIMITIVES_ONLY = False
    """Only put containers containing primitives only on a single line."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if kwargs.get("indent") is None:
            kwargs["indent"] = 2
        super().__init__(*args, **kwargs)
        self.indentation_level = 0

    @override
    def encode(self, o: Any) -> str:
        if isinstance(o, list | tuple):
            return self._encode_list(o)
        if isinstance(o, dict):
            return self._encode_object(o)
        if isinstance(o, float):  # Use scientific notation for floats
            return format(o, "g")
        return json.dumps(
            obj=o,
            skipkeys=self.skipkeys,
            ensure_ascii=self.ensure_ascii,
            check_circular=self.check_circular,
            allow_nan=self.allow_nan,
            sort_keys=self.sort_keys,
            indent=self.indent,
            separators=(self.item_separator, self.key_separator),
            default=self.default if hasattr(self, "default") else None,
        )

    def _encode_list(self, o: list[Any] | tuple[Any]) -> str:
        if self._put_on_single_line(o):
            return "[" + ", ".join(self.encode(el) for el in o) + "]"
        self.indentation_level += 1
        output = [self.indent_str + self.encode(el) for el in o]
        self.indentation_level -= 1
        return "[\n" + ",\n".join(output) + "\n" + self.indent_str + "]"

    def _encode_object(self, o: Any) -> str:
        if not o:
            return "{}"

        o = {str(k) if k is not None else "null": v for k, v in o.items()}

        if self.sort_keys:
            o = dict(sorted(o.items(), key=lambda x: x[0]))

        if self._put_on_single_line(o):
            return "{ " + ", ".join(f"{json.dumps(k)}: {self.encode(el)}" for k, el in o.items()) + " }"

        self.indentation_level += 1
        output = [f"{self.indent_str}{json.dumps(k)}: {self.encode(v)}" for k, v in o.items()]
        self.indentation_level -= 1

        return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"

    @override
    def iterencode(self, o: Any, _one_shot: bool = False) -> Iterator[str]:
        return self.encode(o)  # type: ignore

    def _put_on_single_line(self, o: Any) -> bool:
        return self._primitives_only(o) and len(o) <= self.MAX_ITEMS and len(str(o)) - 2 <= self.MAX_WIDTH

    def _primitives_only(self, o: list[Any] | tuple[Any] | dict[Any, Any]) -> bool:
        if not self.PRIMITIVES_ONLY:
            return True
        if isinstance(o, list | tuple):
            return not any(isinstance(el, self.CONTAINER_TYPES) for el in o)
        elif isinstance(o, dict):
            return not any(isinstance(el, self.CONTAINER_TYPES) for el in o.values())

    @property
    def indent_str(self) -> str:
        if isinstance(self.indent, int):
            return " " * (self.indentation_level * self.indent)
        elif isinstance(self.indent, str):
            return self.indentation_level * self.indent
        else:
            raise ValueError(f"indent must either be of type int or str (is: {type(self.indent)})")
