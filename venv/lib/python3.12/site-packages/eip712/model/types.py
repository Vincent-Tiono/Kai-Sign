from enum import Enum
from typing import Annotated

from pydantic import Field


class EIP712Format(str, Enum):
    AMOUNT = "amount"
    RAW = "raw"
    DATETIME = "datetime"
    TRUSTED_NAME = "trusted-name"


class EIP712NameType(str, Enum):
    EOA = "eoa"
    SMART_CONTRACT = "smart_contract"
    COLLECTION = "collection"
    TOKEN = "token"  # nosec B105 - bandit false positive
    WALLET = "wallet"
    CONTEXT_ADDRESS = "context_address"


class EIP712NameSource(str, Enum):
    LOCAL_ADDRESS_BOOK = "local_address_book"
    CRYPTO_ASSET_LIST = "crypto_asset_list"
    ENS = "ens"
    UNSTOPPABLE_DOMAIN = "unstoppable_domain"
    FREENAME = "freename"
    DNS = "dns"
    DYNAMIC_RESOLVER = "dynamic_resolver"


class EIP712Version(Enum):
    V1 = 1
    V2 = 2


HexString = Annotated[str, Field(pattern=r"^[a-f0-9]+$")]

ContractAddress = Annotated[str, Field(pattern=r"^(0x)?[a-f0-9]{40}$")]
