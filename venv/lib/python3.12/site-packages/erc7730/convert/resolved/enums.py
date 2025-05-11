from erc7730.common.output import OutputAdder
from erc7730.model.metadata import EnumDefinition
from erc7730.model.paths import DescriptorPath, Field
from erc7730.model.paths.path_ops import descriptor_path_strip_prefix
from erc7730.model.types import Id

ENUMS_PATH = DescriptorPath(elements=[Field(identifier="metadata"), Field(identifier="enums")])


def get_enum(ref: DescriptorPath, enums: dict[Id, EnumDefinition], out: OutputAdder) -> dict[str, str] | None:
    if (enum_id := get_enum_id(ref, out)) is None:
        return None

    if (enum := enums.get(enum_id)) is None:
        return out.error(
            title="Invalid enum reference",
            message=f"""Enum "{enum_id}" does not exist, valid ones are: """ f"{', '.join(enums.keys())}.",
        )
    return enum


def get_enum_id(path: DescriptorPath, out: OutputAdder) -> str | None:
    try:
        tail = descriptor_path_strip_prefix(path, ENUMS_PATH)
    except ValueError:
        return out.error(
            title="Invalid enum reference path",
            message=f"Enums must be defined at {ENUMS_PATH}, {path} is not a valid enum reference.",
        )
    if len(tail.elements) != 1:
        return out.error(
            title="Invalid enum reference path",
            message=f"Enums must be defined directly under {ENUMS_PATH}, deep nesting is not allowed, {path} is not a "
            f"valid enum reference.",
        )
    if not isinstance(element := tail.elements[0], Field):
        return out.error(
            title="Invalid enum reference path",
            message=f"Enums must be defined at {ENUMS_PATH}, array operators are not allowed, {path} is not a valid "
            f"enum reference.",
        )

    return element.identifier
