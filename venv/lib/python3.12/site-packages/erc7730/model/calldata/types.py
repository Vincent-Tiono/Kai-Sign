from enum import StrEnum


class TrustedNameType(StrEnum):
    EOA = "eoa"
    SMART_CONTRACT = "smart_contract"
    COLLECTION = "collection"
    TOKEN = "token"  # nosec B105 - bandit false positive
    WALLET = "wallet"
    CONTEXT_ADDRESS = "context_address"

    @property
    def int_value(self) -> int:
        match self:
            case TrustedNameType.EOA:
                return 1
            case TrustedNameType.SMART_CONTRACT:
                return 2
            case TrustedNameType.COLLECTION:
                return 3
            case TrustedNameType.TOKEN:
                return 4
            case TrustedNameType.WALLET:
                return 5
            case TrustedNameType.CONTEXT_ADDRESS:
                return 6


class TrustedNameSource(StrEnum):
    LOCAL_ADDRESS_BOOK = "local_address_book"
    CRYPTO_ASSET_LIST = "crypto_asset_list"
    ENS = "ens"
    UNSTOPPABLE_DOMAIN = "unstoppable_domain"
    FREENAME = "freename"
    DNS = "dns"
    DYNAMIC_RESOLVER = "dynamic_resolver"

    @property
    def int_value(self) -> int:
        match self:
            case TrustedNameSource.LOCAL_ADDRESS_BOOK:
                return 0
            case TrustedNameSource.CRYPTO_ASSET_LIST:
                return 1
            case TrustedNameSource.ENS:
                return 2
            case TrustedNameSource.UNSTOPPABLE_DOMAIN:
                return 3
            case TrustedNameSource.FREENAME:
                return 4
            case TrustedNameSource.DNS:
                return 5
            case TrustedNameSource.DYNAMIC_RESOLVER:
                return 6
