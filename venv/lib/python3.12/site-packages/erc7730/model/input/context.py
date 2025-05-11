from pydantic import Field
from pydantic_string_url import HttpUrl

from erc7730.model.abi import ABI
from erc7730.model.base import Model
from erc7730.model.context import EIP712Schema
from erc7730.model.types import Id, MixedCaseAddress

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class InputDomain(Model):
    """
    EIP 712 Domain Binding constraint.

    Each value of the domain constraint MUST match the corresponding eip 712 message domain value.
    """

    name: str | None = Field(default=None, title="Name", description="The EIP-712 domain name.")

    version: str | None = Field(default=None, title="Version", description="The EIP-712 version.")

    chainId: int | None = Field(default=None, title="Chain ID", description="The EIP-155 chain id.")

    verifyingContract: MixedCaseAddress | None = Field(
        default=None, title="Verifying Contract", description="The EIP-712 verifying contract address."
    )


class InputDeployment(Model):
    """
    A deployment describing where the contract is deployed.

    The target contract (Tx to or factory) MUST match one of those deployments.
    """

    chainId: int = Field(title="Chain ID", description="The deployment EIP-155 chain id.")

    address: MixedCaseAddress = Field(title="Contract Address", description="The deployment contract address.")


class InputFactory(Model):
    """
    A factory constraint is used to check whether the target contract is deployed by a specified factory.
    """

    deployments: list[InputDeployment] = Field(
        title="Deployments",
        description="An array of deployments describing where the contract is deployed. The target contract (Tx to or"
        "factory) MUST match one of those deployments.",
    )

    deployEvent: str = Field(
        title="Deploy Event signature",
        description="The event signature that the factory emits when deploying a new contract.",
    )


class InputBindingContext(Model):
    deployments: list[InputDeployment] = Field(
        title="Deployments",
        description="An array of deployments describing where the contract is deployed. The target contract (Tx to or"
        "factory) MUST match one of those deployments.",
        min_length=1,
    )


class InputContract(InputBindingContext):
    """
    The contract binding context is a set constraints that are used to bind the ERC7730 file to a specific smart
    contract.
    """

    abi: list[ABI] | HttpUrl = Field(
        title="ABI",
        description="The ABI of the target contract. This can be either an array of ABI objects or an URL pointing to"
        "the ABI.",
    )

    addressMatcher: HttpUrl | None = Field(
        None,
        title="Address Matcher",
        description="An URL of a contract address matcher that should be used to match the contract address.",
    )

    factory: InputFactory | None = Field(
        None,
        title="Factory Constraint",
        description="A factory constraint is used to check whether the target contract is deployed by a specified"
        "factory.",
    )


class InputEIP712(InputBindingContext):
    """
    EIP 712 Binding.

    The EIP-712 binding context is a set of constraints that must be verified by the message being signed.
    """

    domain: InputDomain | None = Field(
        default=None,
        title="EIP 712 Domain Binding constraint",
        description="Each value of the domain constraint MUST match the corresponding eip 712 message domain value.",
    )

    domainSeparator: str | None = Field(
        default=None,
        title="Domain Separator constraint",
        description="The domain separator value that must be matched by the message. In hex string representation.",
    )

    schemas: list[EIP712Schema | HttpUrl] = Field(
        title="EIP-712 messages schemas", description="Schemas of all messages."
    )


class InputContractContext(Model):
    """
    Contract Binding Context.

    The contract binding context is a set constraints that are used to bind the ERC7730 file to a specific smart
    contract.
    """

    id: Id | None = Field(
        alias="$id",
        default=None,
        title="Id",
        description="An internal identifier that can be used either for clarity specifying what the element is or as a"
        "reference in device specific sections.",
    )

    contract: InputContract = Field(
        title="Contract Binding Context",
        description="The contract binding context is a set constraints that are used to bind the ERC7730 file to a"
        "specific smart contract.",
    )


class InputEIP712Context(Model):
    """
    EIP 712 Binding.

    The EIP-712 binding context is a set of constraints that must be verified by the message being signed.
    """

    id: Id | None = Field(
        alias="$id",
        default=None,
        title="Id",
        description="An internal identifier that can be used either for clarity specifying what the element is or as a"
        "reference in device specific sections.",
    )

    eip712: InputEIP712 = Field(
        title="EIP 712 Binding",
        description="The EIP-712 binding context is a set of constraints that must be verified by the message being"
        "signed.",
    )
