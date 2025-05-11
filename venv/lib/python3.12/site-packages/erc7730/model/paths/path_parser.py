from typing import Any

from lark import Lark, UnexpectedInput
from lark.exceptions import VisitError
from lark.visitors import Transformer_InPlaceRecursive
from pydantic import TypeAdapter, ValidationError

from erc7730.model.paths import (
    Array,
    ArrayElement,
    ArrayIndex,
    ArraySlice,
    ContainerField,
    ContainerPath,
    DataPath,
    DescriptorPath,
    Field,
)

PATH_PARSER = Lark(
    grammar=r"""
        ?path: descriptor_path | container_path | data_path
    
        descriptor_path: "$." descriptor_path_component ("." descriptor_path_component)*
        ?descriptor_path_component: field | array_element
    
        container_path: "@." container_field
        !container_field: "from" | "to" | "value"
    
        ?data_path: absolute_data_path | relative_data_path
        absolute_data_path: "#." data_path_component ("." data_path_component)*
        relative_data_path: data_path_component ("." data_path_component)*
        ?data_path_component: field | array | array_element | array_slice

        field: /[a-zA-Z0-9_]+/
        array: "[]"
        array_index: /-?[0-9]+/
        array_element: "[" array_index "]"
        slice_array_index: array_index?
        array_slice: "[" slice_array_index ":" slice_array_index "]"
    """,
    start="path",
)


class PathTransformer(Transformer_InPlaceRecursive):
    """Visitor to transform the parsed path AST into path domain model objects."""

    def field(self, ast: Any) -> Field:
        (value,) = ast
        return Field(identifier=value.value)

    def array(self, ast: Any) -> Array:
        return Array()

    def array_index(self, ast: Any) -> ArrayIndex:
        (value,) = ast
        return TypeAdapter(ArrayIndex).validate_strings(value)

    def array_element(self, ast: Any) -> ArrayElement:
        (value,) = ast
        return ArrayElement(index=value)

    def slice_array_index(self, ast: Any) -> ArrayIndex | None:
        if len(ast) == 1:
            (value,) = ast
            return value
        return None

    def array_slice(self, ast: Any) -> ArraySlice:
        (start, end) = ast
        return ArraySlice(start=start, end=end)

    def container_field(self, ast: Any) -> ContainerField:
        (value,) = ast
        return ContainerField(value)

    def descriptor_path(self, ast: Any) -> DescriptorPath:
        return DescriptorPath(elements=ast)

    def container_path(self, ast: Any) -> ContainerPath:
        (value,) = ast
        return ContainerPath(field=value)

    def absolute_data_path(self, ast: Any) -> DataPath:
        return DataPath(elements=ast, absolute=True)

    def relative_data_path(self, ast: Any) -> DataPath:
        return DataPath(elements=ast, absolute=False)


PATH_TRANSFORMER = PathTransformer()


def to_path(path: str) -> ContainerPath | DataPath | DescriptorPath:
    """
    Parse a path string into a domain model object.

    :param path: the path input string
    :return: an union of all possible path types
    :raises ValueError: if the input string is not a valid path
    :raises Exception: if the path parsing fails for an unexpected reason
    """
    try:
        return PATH_TRANSFORMER.transform(PATH_PARSER.parse(path))
    except UnexpectedInput as e:
        # TODO improve error reporting, see:
        #  https://github.com/lark-parser/lark/blob/master/examples/advanced/error_reporting_lalr.py
        raise ValueError(f"""Invalid path "{path}": {e}""") from None
    except VisitError as e:
        if isinstance(e.orig_exc, ValidationError):
            raise ValueError(f"""Invalid path "{path}": {e.orig_exc}`""") from None
        raise Exception(
            f"""Failed to parse path "{path}": {e}`\n"""
            "This is most likely a bug in the ERC-7730 library, please report it to authors."
        ) from e
    except Exception as e:
        raise Exception(
            f"""Failed to parse path "{path}": {e}`\n"""
            "This is most likely a bug in the ERC-7730 library, please report it to authors."
        ) from e
