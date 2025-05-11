"""
Conversion of ERC-7730 ABI paths to calldata descriptor binary paths.
"""

from typing import Any, assert_never

from erc7730.common.binary import from_hex
from erc7730.common.output import OutputAdder
from erc7730.convert.calldata.v1.abi import (
    ABIDynamicArray,
    ABIDynamicLeaf,
    ABIStaticArray,
    ABIStaticLeaf,
    ABIStruct,
    ABITree,
)
from erc7730.model.calldata.v1.value import (
    CalldataDescriptorContainerPathV1,
    CalldataDescriptorContainerPathValueV1,
    CalldataDescriptorDataPathV1,
    CalldataDescriptorPathElementArrayV1,
    CalldataDescriptorPathElementLeafV1,
    CalldataDescriptorPathElementRefV1,
    CalldataDescriptorPathElementSliceV1,
    CalldataDescriptorPathElementTupleV1,
    CalldataDescriptorPathElementV1,
    CalldataDescriptorPathLeafType,
    CalldataDescriptorTypeFamily,
    CalldataDescriptorValueConstantV1,
    CalldataDescriptorValuePathV1,
    CalldataDescriptorValueV1,
)
from erc7730.model.input.path import DataPathStr
from erc7730.model.paths import (
    Array,
    ArrayElement,
    ArraySlice,
    ContainerField,
    DataPath,
    DataPathElement,
    Field,
)
from erc7730.model.resolved.display import (
    ResolvedValue,
    ResolvedValueConstant,
    ResolvedValuePath,
)
from erc7730.model.resolved.path import ContainerPath
from erc7730.model.types import HexStr


def convert_value(
    value: ResolvedValue,
    abi: ABITree,
    out: OutputAdder,
) -> CalldataDescriptorValueV1 | None:
    """
    Convert a value to a calldata protocol value.

    @param value: input container path
    @param abi: function ABI
    @param out: error handler
    @return: output value
    """
    match value:
        case ResolvedValuePath() as path:
            return convert_path(path, abi, out)
        case ResolvedValueConstant() as constant:
            return convert_constant(constant, out)
        case _:
            assert_never(value)


def convert_constant(
    constant: ResolvedValueConstant,
    out: OutputAdder,
) -> CalldataDescriptorValueConstantV1 | None:
    """
    Convert a constant to a calldata protocol value.

    @param constant: input constant value
    @param out: error handler
    @return: output value
    """
    return CalldataDescriptorValueConstantV1(
        type_family=CalldataDescriptorTypeFamily[constant.type_family.name],
        type_size=constant.type_size,
        value=constant.value,
        raw=constant.raw,
    )


def convert_path(
    path: ResolvedValuePath,
    abi: ABITree,
    out: OutputAdder,
) -> CalldataDescriptorValuePathV1 | None:
    """
    Convert a path to a calldata protocol value.

    @param path: input path value
    @param abi: function ABI
    @param out: error handler
    @return: output value
    """
    match path.path:
        case ContainerPath() as container_path:
            return convert_container_path(container_path, out)
        case DataPath() as data_path:
            return convert_data_path(data_path, abi, out)
        case _:
            assert_never(path.path)


def convert_container_path(
    path: ContainerPath,
    out: OutputAdder,
) -> CalldataDescriptorValuePathV1 | None:
    """
    Convert a container path to a calldata protocol value.

    @param path: input container path
    @param out: error handler
    @return: output binary data path
    """
    match path.field:
        case ContainerField.FROM:
            field = CalldataDescriptorContainerPathValueV1.FROM
            type_family = CalldataDescriptorTypeFamily.ADDRESS
            type_size = 20
        case ContainerField.TO:
            field = CalldataDescriptorContainerPathValueV1.TO
            type_family = CalldataDescriptorTypeFamily.ADDRESS
            type_size = 20
        case ContainerField.VALUE:
            field = CalldataDescriptorContainerPathValueV1.VALUE
            type_family = CalldataDescriptorTypeFamily.UINT
            type_size = 32
        case _:
            assert_never(path.field)
    return CalldataDescriptorValuePathV1(
        abi_path=path,
        binary_path=CalldataDescriptorContainerPathV1(value=field),
        type_family=type_family,
        type_size=type_size,
    )


def convert_data_path(
    path: DataPath,
    abi: ABITree,
    out: OutputAdder,
) -> CalldataDescriptorValuePathV1 | None:
    """
    Convert a data path (representing the path to reach a value in the function ABI) to a Ledger specific binary path,
    representing cursor movements to reach the same value in a serialized transaction calldata payload.

    @param path: input data path (ABI path)
    @param abi: function ABI
    @param out: error handler
    @return: output binary data path
    """
    if len(path.elements) == 0:
        return out.error(
            title="Invalid data path",
            message="Path must refer to a single value in ABI function but an empty path was provided",
        )

    # current partial path in the ABI + error callback, to raise contextualized errors
    current_path_in: list[DataPathElement] = []

    def error(message: str) -> CalldataDescriptorValuePathV1 | None:
        return out.error(
            title="Invalid data path",
            message=f"""Path {path} cannot be applied to ABI function "{abi.model_dump_json(indent=2)}: at """
            f"{DataPathStr(absolute=True, elements=current_path_in)}, {message}",
        )

    # output path elements
    path_out: list[CalldataDescriptorPathElementV1] = []

    # current ABI element - note we enrich the ABI for easier processing
    current_abi_element = abi

    # static paths special case: instead of emitting tuple/array elements, we will accumulate the offset and emit a
    # single tuple element
    is_static: bool = not current_abi_element.is_dynamic
    static_offset: int = 0

    # leaf slice special case: pop it from the path, and we will handle it at the end after the whole path (slice is
    # only allowed as last element)
    leaf_slice: ArraySlice | None
    path_in: list[DataPathElement]
    match path.elements[-1]:
        case Array() | Field() | ArrayElement():
            path_in = path.elements
            leaf_slice = None
        case ArraySlice() as s:
            path_in = path.elements[:-1]
            leaf_slice = s
        case _:
            assert_never(path.elements[-1])

    # iterate data path elements, moving in the ABI tree / emitting binary path elements as needed
    for current_path_element in path_in:
        current_path_in.append(current_path_element)

        match (current_path_element, current_abi_element):
            # field element on a struct => emit a tuple element
            case (Field(identifier=identifier), ABIStruct(components=abi_components, offsets=abi_offsets)):
                if (component := abi_components.get(identifier)) is None:
                    return error(f"""ABI element has no "{identifier}" field""")
                if (field_offset := abi_offsets.get(identifier)) is None:
                    return error(f"""ABI element has no offset for "{identifier}" field""")

                if is_static:
                    static_offset += field_offset
                else:
                    path_out.append(CalldataDescriptorPathElementTupleV1(offset=field_offset))

                current_abi_element = component

            # field element on anything else => invalid
            case (Field(identifier=identifier), _):
                return error(
                    f"""cannot reference a struct field ("{identifier}") on a "{current_abi_element.type}" """
                    "ABI element"
                )

            # array element on a static array => emit a tuple element
            case (ArrayElement(index=index), ABIStaticArray(dimension=dimension, component=component)):
                if index >= dimension or index < -dimension:
                    return error(f"""index {index}" is out of bounds for array of dimension {dimension}""")

                array_offset = (index if index >= 0 else dimension + index) * component.size

                if is_static:
                    static_offset += array_offset
                else:
                    path_out.append(CalldataDescriptorPathElementTupleV1(offset=array_offset))

                current_abi_element = component

            # array element on a dynamic array => emit an array element
            case (ArrayElement(index=index), ABIDynamicArray(component=component)):
                if is_static:
                    return error("""illegal state: a static path cannot be used on a dynamic array""")

                path_out.append(
                    CalldataDescriptorPathElementArrayV1(
                        start=index,
                        end=None if index == -1 else index + 1,  # edge case for last element
                        weight=component.size,
                    )
                )

                current_abi_element = component

            # array element on anything else => invalid
            case (ArrayElement(), _):
                return error(f"""cannot reference an array element on a "{current_abi_element.type}" ABI element""")

            # full array on a static array => emit an array element with no offset
            case (Array(), ABIStaticArray()):
                # FIXME We should emit one path per static array element, using
                #  CalldataDescriptorPathElementTupleV1
                return error("""full static array is not supported yet""")

            # full array on a dynamic array => emit an array element with no offset
            case (Array(), ABIDynamicArray(component=component)):
                path_out.append(CalldataDescriptorPathElementArrayV1(start=None, end=None, weight=component.size))

                current_abi_element = component

            # full array on anything else => invalid
            case (Array(), _):
                return error(f"""cannot reference an array on a "{current_abi_element.type}" ABI element""")

            # array slice as inner element => not allowed
            case (ArraySlice(), _):
                return error("array slice can only be used as last element of the path")

            case (path_element, abi_element):
                return error(
                    f"path does not match ABI structure (path element: {path_element}, ABI element: {abi_element})"
                )

        # if current element is dynamic, we need to dereference it
        if current_abi_element.is_dynamic:
            path_out.append(CalldataDescriptorPathElementRefV1())

    # emit a last static offset to a static value
    if is_static:
        path_out.append(CalldataDescriptorPathElementTupleV1(offset=static_offset))

    # append leaf element
    type_family: CalldataDescriptorTypeFamily
    type_size: int | None
    match current_abi_element:
        case ABIStaticArray() | ABIDynamicArray():
            raise NotImplementedError("Array leaf is not supported in v1 of protocol")
        case ABIStruct():
            raise NotImplementedError("Tuple leaf is not supported in v1 of protocol")
        case ABIDynamicLeaf():
            leaf_type = CalldataDescriptorPathLeafType.DYNAMIC_LEAF
            type_family = current_abi_element.type_family
            type_size = current_abi_element.type_size
        case ABIStaticLeaf():
            leaf_type = CalldataDescriptorPathLeafType.STATIC_LEAF
            type_family = current_abi_element.type_family
            type_size = current_abi_element.type_size
        case _:
            assert_never(current_abi_element)
    path_out.append(CalldataDescriptorPathElementLeafV1(leaf_type=leaf_type))

    # if slice is present, emit a slice element
    if leaf_slice is not None:
        path_out.append(CalldataDescriptorPathElementSliceV1(start=leaf_slice.start, end=leaf_slice.end))

    return CalldataDescriptorValuePathV1(
        abi_path=path,
        binary_path=CalldataDescriptorDataPathV1(elements=path_out),
        type_family=type_family,
        type_size=type_size,
    )


def apply_path(calldata: HexStr, path: CalldataDescriptorValuePathV1) -> Any:
    """
    Evaluate a path against encoded calldata, to get a decoded value.

    @param calldata: serialized function call data
    @param path: binary path
    @return: decoded value
    """
    match path.binary_path:
        case CalldataDescriptorContainerPathV1():
            raise ValueError("This function only supports data paths")
        case CalldataDescriptorDataPathV1():
            raw_value = apply_path_raw(calldata, path.binary_path)
        case _:
            assert_never(path.binary_path)

    match path.type_family:
        case CalldataDescriptorTypeFamily.INT:
            return int.from_bytes(raw_value, signed=True)
        case CalldataDescriptorTypeFamily.UINT:
            return int.from_bytes(raw_value, signed=False)
        case CalldataDescriptorTypeFamily.FIXED:
            raise NotImplementedError("Fixed point numbers are not supported")
        case CalldataDescriptorTypeFamily.UFIXED:
            raise NotImplementedError("Unsigned fixed point numbers are not supported")
        case CalldataDescriptorTypeFamily.ADDRESS:
            return "0x" + raw_value.hex()
        case CalldataDescriptorTypeFamily.BOOL:
            return bool(int.from_bytes(raw_value))
        case CalldataDescriptorTypeFamily.BYTES:
            return "0x" + raw_value.hex()
        case CalldataDescriptorTypeFamily.STRING:
            return raw_value.decode("ascii")
        case _:
            assert_never(path.type_family)


def apply_path_raw(calldata: HexStr, path: CalldataDescriptorDataPathV1) -> bytes:
    """
    Evaluate a path against encoded calldata, to get a raw value.

    @param calldata: serialized function call data
    @param path: binary path
    @return: raw value byte array
    """
    # decode calldata, strip selector part
    argdata = from_hex(calldata)[4:]

    # leaf slice special case: pop it from the path, and we will handle it at the end after the whole path (slice is
    # only allowed as last element)
    leaf_slice: CalldataDescriptorPathElementSliceV1 | None
    path_in: list[CalldataDescriptorPathElementV1]
    match path.elements[-1]:
        case (
            CalldataDescriptorPathElementTupleV1()
            | CalldataDescriptorPathElementArrayV1()
            | CalldataDescriptorPathElementRefV1()
            | CalldataDescriptorPathElementLeafV1()
        ):
            path_in = path.elements
            leaf_slice = None
        case CalldataDescriptorPathElementSliceV1() as s:
            path_in = path.elements[:-1]
            leaf_slice = s
        case _:
            assert_never(path.elements[-1])

    offset = 0
    ref_offset = 0

    for element in path_in:
        match element:
            case CalldataDescriptorPathElementTupleV1():
                ref_offset = offset
                offset += element.offset * 32

            case CalldataDescriptorPathElementArrayV1():
                ref_offset = offset
                array_length = int.from_bytes(argdata[offset : offset + 32], byteorder="big")

                start = 0 if element.start is None else element.start
                if start < 0:
                    start += array_length

                end = array_length if element.end is None else element.end
                if end < 0:
                    end += array_length

                if start >= array_length or start < 0:
                    raise IndexError(f"Array index {element.start} out of bounds")

                if end > array_length or end <= 0:
                    raise IndexError(f"Array index {element.end} out of bounds")

                if start != end - 1:
                    raise NotImplementedError("Only array slices of length 1 are supported by this implementation")

                offset += 32 + start * element.weight * 32

            case CalldataDescriptorPathElementRefV1():
                offset = ref_offset + int.from_bytes(argdata[offset : offset + 32], byteorder="big")

            case CalldataDescriptorPathElementSliceV1():
                raise ValueError("Slice can only be used as last element of the path")

            case CalldataDescriptorPathElementLeafV1():
                match element.leaf_type:
                    case CalldataDescriptorPathLeafType.ARRAY_LEAF:
                        raise NotImplementedError("Array leaf is not supported in v1 of protocol")

                    case CalldataDescriptorPathLeafType.TUPLE_LEAF:
                        raise NotImplementedError("Tuple leaf is not supported in v1 of protocol")

                    case CalldataDescriptorPathLeafType.STATIC_LEAF:
                        # TODO slice ? https://github.com/LedgerHQ/generic_parser/pull/9
                        return argdata[offset : offset + 32]

                    case CalldataDescriptorPathLeafType.DYNAMIC_LEAF:
                        length = int.from_bytes(argdata[offset : offset + 32], byteorder="big")

                        if leaf_slice is None:
                            return argdata[offset + 32 : offset + 32 + length]

                        leaf_slice_start = 0 if leaf_slice.start is None else leaf_slice.start
                        start = leaf_slice_start if leaf_slice_start >= 0 else length + leaf_slice_start

                        leaf_slice_end = length - 1 if leaf_slice.end is None else leaf_slice.end
                        end = leaf_slice_end if leaf_slice_end >= 0 else length + leaf_slice_end

                        if start < 0 or end < 0 or start >= length or end >= length:
                            raise IndexError("Slice out of bounds")

                        return argdata[offset + 32 + start : offset + 32 + end]

                    case _:
                        assert_never(element.leaf_type)

            case _:
                assert_never(element)

    raise ValueError("Path did not resolve to a leaf element")
