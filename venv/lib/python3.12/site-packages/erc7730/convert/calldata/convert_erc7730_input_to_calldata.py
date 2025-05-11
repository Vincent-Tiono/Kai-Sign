from pydantic_string_url import HttpUrl

from erc7730.common.output import ConsoleOutputAdder
from erc7730.convert.calldata.v1.descriptor import (
    convert_descriptor,
)
from erc7730.model.calldata.descriptor import CalldataDescriptor
from erc7730.model.input.context import InputContractContext
from erc7730.model.input.descriptor import InputERC7730Descriptor
from erc7730.model.input.lenses import get_chain_ids


def erc7730_descriptor_to_calldata_descriptors(
    input_descriptor: InputERC7730Descriptor, source: HttpUrl | None = None, chain_id: int | None = None
) -> list[CalldataDescriptor]:
    """
    Generate output calldata descriptors from input ERC-7730 descriptor with contract context.

    If descriptor is invalid, an empty list is returned. If the descriptor is partially invalid, a partial list is
    returned. Errors are logged as warnings.

    :param input_descriptor: input descriptor
    :param source: source of the descriptor file
    :param chain_id: if set, only emit calldata descriptors for given chain IDs
    :return: output calldata descriptors (1 per chain + selector)
    """

    out = ConsoleOutputAdder()
    try:
        if not isinstance(input_descriptor.context, InputContractContext):
            return []

        if chain_id is not None and chain_id not in get_chain_ids(input_descriptor):
            return []

        return convert_descriptor(input_descriptor=input_descriptor, source=source, chain_id=chain_id, out=out)

    except Exception:
        out.warning(f"Error processing ERC-7730 file {source}, skipping it")

    return []
