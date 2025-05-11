from typing import final, override

from erc7730.common.abi import function_to_selector
from erc7730.common.output import OutputAdder
from erc7730.lint import ERC7730Linter
from erc7730.model.paths import DataPath, Field
from erc7730.model.paths.path_ops import data_path_ends_with, path_starts_with, to_absolute
from erc7730.model.paths.path_schemas import (
    compute_abi_schema_paths,
    compute_eip712_schema_paths,
    compute_format_schema_paths,
)
from erc7730.model.resolved.context import EIP712Schema, ResolvedContractContext, ResolvedEIP712Context
from erc7730.model.resolved.descriptor import ResolvedERC7730Descriptor

AUTHORIZED_MISSING_DISPLAY_FIELDS = {
    Field(identifier="nonce"),
    Field(identifier="sigDeadline"),
}


@final
class ValidateDisplayFieldsLinter(ERC7730Linter):
    """
    - for each field of schema/ABI, check that there is a display field
    - for each field, check that display configuration is relevant with field type
    """

    @override
    def lint(self, descriptor: ResolvedERC7730Descriptor, out: OutputAdder) -> None:
        self._validate_eip712_paths(descriptor, out)
        self._validate_abi_paths(descriptor, out)

    @classmethod
    def _validate_eip712_paths(cls, descriptor: ResolvedERC7730Descriptor, out: OutputAdder) -> None:
        if isinstance(descriptor.context, ResolvedEIP712Context) and descriptor.context.eip712.schemas is not None:
            primary_types: set[str] = set()
            for schema in descriptor.context.eip712.schemas:
                if isinstance(schema, EIP712Schema):
                    primary_types.add(schema.primaryType)
                    if schema.primaryType not in schema.types:
                        out.error(
                            title="Invalid EIP712 Schema",
                            message=f"Primary type `{schema.primaryType}` is not present in schema types. Please make "
                            f"sure the EIP-712 schema includes a definition for the primary type.",
                        )
                        continue
                    if schema.primaryType not in descriptor.display.formats:
                        out.error(
                            title="Missing Display Format",
                            message=f"Schema primary type `{schema.primaryType}` must have a display format defined.",
                        )
                        continue
                    eip712_paths = compute_eip712_schema_paths(schema)
                    primary_type_format = descriptor.display.formats[schema.primaryType]
                    format_paths = compute_format_schema_paths(primary_type_format).data_paths

                    if (excluded := primary_type_format.excluded) is not None:
                        excluded_paths = [to_absolute(path) for path in excluded]
                    else:
                        excluded_paths = []

                    for path in eip712_paths - format_paths:
                        if any(path_starts_with(path, excluded_path) for excluded_path in excluded_paths):
                            continue

                        if any(data_path_ends_with(path, allowed) for allowed in AUTHORIZED_MISSING_DISPLAY_FIELDS):
                            out.debug(
                                title="Optional Display field missing",
                                message=f"No display field is defined for path `{path}` in message "
                                f"{schema.primaryType}. If intentionally excluded, please add it to `excluded` "
                                f"list to avoid this warning.",
                            )
                        else:
                            out.warning(
                                title="Missing Display field",
                                message=f"No display field is defined for path `{path}` in {schema.primaryType}. "
                                f"If intentionally excluded, please add it to `excluded` list to avoid this "
                                f"warning.",
                            )
                    for path in format_paths - eip712_paths:
                        out.error(
                            title="Invalid Display field",
                            message=f"A display field is defined for `{path}`, but it does not exist in message "
                            f"{schema.primaryType}. Please check the field path is valid according to the EIP-712 "
                            f"schema.",
                        )

                else:
                    out.error(
                        title="Missing EIP712 Schema",
                        message=f"EIP712 Schema is missing (found {schema})",
                    )

            for fmt in descriptor.display.formats:
                if fmt not in primary_types:
                    out.error(
                        title="Invalid Display Format",
                        message=f"Type `{fmt}` is not in EIP712 schemas. Please check the type is valid according to "
                        f"the EIP-712 schema.",
                    )

    @classmethod
    def _validate_abi_paths(cls, descriptor: ResolvedERC7730Descriptor, out: OutputAdder) -> None:
        if isinstance(descriptor.context, ResolvedContractContext):
            abi_paths_by_selector: dict[str, set[DataPath]] = {}
            for abi in descriptor.context.contract.abi:
                if abi.type == "function":
                    abi_paths_by_selector[function_to_selector(abi)] = compute_abi_schema_paths(abi)

            for selector, fmt in descriptor.display.formats.items():
                if selector not in abi_paths_by_selector:
                    out.error(
                        title="Invalid selector",
                        message=f"Selector {selector} not found in ABI.",
                    )
                    continue
                format_paths = compute_format_schema_paths(fmt).data_paths
                abi_paths = abi_paths_by_selector[selector]

                if (excluded := fmt.excluded) is not None:
                    excluded_paths = [to_absolute(path) for path in excluded]
                else:
                    excluded_paths = []

                for path in abi_paths - format_paths:
                    if any(path_starts_with(path, excluded_path) for excluded_path in excluded_paths):
                        continue

                    if any(data_path_ends_with(path, allowed) for allowed in AUTHORIZED_MISSING_DISPLAY_FIELDS):
                        out.debug(
                            title="Optional Display Field Missing",
                            message=f"No display field is defined for path `{path}` in function {selector}. If "
                            f"intentionally excluded, please add it to `excluded` list to avoid this warning.",
                        )
                    else:
                        out.warning(
                            title="Missing Display field",
                            message=f"No display field is defined for path `{path}` in function {selector}. If "
                            f"intentionally excluded, please add it to `excluded` list to avoid this warning.",
                        )
                for path in format_paths - abi_paths:
                    out.error(
                        title="Invalid Display field",
                        message=f"A display field is defined for `{path}`, but it does not exist in function "
                        f"{selector} ABI. Please check the field path is valid according to the ABI.",
                    )
