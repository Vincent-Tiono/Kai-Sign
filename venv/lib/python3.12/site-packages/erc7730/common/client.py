import json
import os
from abc import ABC
from functools import cache
from typing import Any, TypeVar, final, override

from hishel import CacheTransport, FileStorage
from httpx import URL, BaseTransport, Client, HTTPTransport, Request, Response
from httpx._content import IteratorByteStream
from httpx_file import FileTransport
from limiter import Limiter
from pydantic import ConfigDict, TypeAdapter, ValidationError
from pydantic_string_url import FileUrl, HttpUrl
from xdg_base_dirs import xdg_cache_home

from erc7730.model.abi import ABI
from erc7730.model.base import Model
from erc7730.model.types import Address

ETHERSCAN = "api.etherscan.io"

_T = TypeVar("_T")


class EtherscanChain(Model):
    """Etherscan supported chain info."""

    model_config = ConfigDict(strict=False, frozen=True, extra="ignore")
    chainname: str
    chainid: int
    blockexplorer: HttpUrl


@cache
def get_supported_chains() -> list[EtherscanChain]:
    """
    Get supported chains from Etherscan.

    :return: Etherscan supported chains, with name/chain id/block explorer URL
    """
    return get(url=HttpUrl(f"https://{ETHERSCAN}/v2/chainlist"), model=list[EtherscanChain])


def get_contract_abis(chain_id: int, contract_address: Address) -> list[ABI]:
    """
    Get contract ABIs from Etherscan.

    :param chain_id: EIP-155 chain ID
    :param contract_address: EVM contract address
    :return: deserialized list of ABIs
    :raises NotImplementedError: if chain id not supported, API key not setup, or unexpected response
    """
    try:
        return get(
            url=HttpUrl(f"https://{ETHERSCAN}/v2/api"),
            chainid=chain_id,
            module="contract",
            action="getabi",
            address=contract_address,
            model=list[ABI],
        )
    except Exception as e:
        if "Contract source code not verified" in str(e):
            raise Exception("contract source is not available on Etherscan") from e
        if "Max calls per sec rate limit reached" in str(e):
            raise Exception("Etherscan rate limit exceeded, please retry") from e
        raise e


def get_contract_explorer_url(chain_id: int, contract_address: Address) -> HttpUrl:
    """
    Get contract explorer site URL (for opening in a browser).

    :param chain_id: EIP-155 chain ID
    :param contract_address: EVM contract address
    :return: URL to the contract explorer site
    :raises NotImplementedError: if chain id not supported
    """
    for chain in get_supported_chains():
        if chain.chainid == chain_id:
            return HttpUrl(f"{chain.blockexplorer}/address/{contract_address}#code")
    raise NotImplementedError(
        f"Chain ID {chain_id} is not supported, please report this to authors of python-erc7730 library"
    )


def get(model: type[_T], url: HttpUrl | FileUrl, **params: Any) -> _T:
    """
    Fetch data from a file or an HTTP URL and deserialize it.

    This method implements some automated adaptations to handle user provided URLs:
     - GitHub: adaptation to "raw.githubusercontent.com"
     - Etherscan: rate limiting, API key parameter injection, "result" field unwrapping

    :param url: URL to get data from
    :param model: Pydantic model to deserialize the data
    :return: deserialized response
    :raises Exception: if URL type is not supported, API key not setup, or unexpected response
    """
    with _client() as client:
        response = client.get(url, params=params).raise_for_status().content
    try:
        return TypeAdapter(model).validate_json(response)
    except ValidationError as e:
        raise Exception(f"Received unexpected response from {url}: {response.decode(errors='replace')}") from e


def _client() -> Client:
    """
    Create a new HTTP client with GitHub and Etherscan specific transports.
    :return:
    """
    cache_storage = FileStorage(base_path=xdg_cache_home() / "erc7730", ttl=7 * 24 * 3600, check_ttl_every=24 * 3600)
    http_transport = HTTPTransport()
    http_transport = GithubTransport(http_transport)
    http_transport = EtherscanTransport(http_transport)
    http_transport = CacheTransport(transport=http_transport, storage=cache_storage)
    file_transport = FileTransport()
    # TODO file storage: authorize relative paths only
    transports = {"https://": http_transport, "file://": file_transport}
    return Client(mounts=transports, timeout=10)


class DelegateTransport(ABC, BaseTransport):
    """Base class for wrapping httpx transport."""

    def __init__(self, delegate: BaseTransport) -> None:
        self._delegate = delegate

    def handle_request(self, request: Request) -> Response:
        return self._delegate.handle_request(request)

    def close(self) -> None:
        self._delegate.close()


@final
class GithubTransport(DelegateTransport):
    """GitHub specific transport for handling raw content requests."""

    GITHUB, GITHUB_RAW = "github.com", "raw.githubusercontent.com"

    def __init__(self, delegate: BaseTransport) -> None:
        super().__init__(delegate)

    @override
    def handle_request(self, request: Request) -> Response:
        if request.url.host != self.GITHUB:
            return super().handle_request(request)

        # adapt URL
        request.url = URL(str(request.url).replace(self.GITHUB, self.GITHUB_RAW).replace("/blob/", "/"))
        request.headers.update({"Host": self.GITHUB_RAW})
        return super().handle_request(request)


@final
class EtherscanTransport(DelegateTransport):
    """Etherscan specific transport for handling rate limiting, API key parameter injection, response unwrapping."""

    ETHERSCAN_API_HOST = "ETHERSCAN_API_HOST"
    ETHERSCAN_API_KEY = "ETHERSCAN_API_KEY"

    @Limiter(rate=5, capacity=5, consume=1)
    @override
    def handle_request(self, request: Request) -> Response:
        if request.url.host != ETHERSCAN:
            return super().handle_request(request)

        # substitute base URL if provided
        if (api_host := os.environ.get(self.ETHERSCAN_API_HOST)) is not None:
            request.url = request.url.copy_with(host=api_host)
            request.headers.update({"Host": api_host})

        # add API key if provided
        if (api_key := os.environ.get(self.ETHERSCAN_API_KEY)) is not None or (
            api_key := os.environ.get(f"SCAN_{self.ETHERSCAN_API_KEY}")
        ) is not None:
            request.url = request.url.copy_add_param("apikey", api_key)

        # read response
        response = super().handle_request(request)
        response.read()
        response.close()

        # unwrap result, sometimes containing JSON directly, sometimes JSON in a string
        try:
            if (result := response.json().get("result")) is not None:
                data = result if isinstance(result, str) else json.dumps(result)
                return Response(status_code=response.status_code, stream=IteratorByteStream([data.encode()]))
        except Exception:
            pass  # nosec B110 - intentional try/except/pass

        raise Exception(f"Unexpected response from Etherscan: {response.content.decode(errors='replace')}")
