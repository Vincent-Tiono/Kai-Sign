"""
Object model for Solidity ABIs.

See https://docs.soliditylang.org/en/latest/abi-spec.html
"""

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field

from erc7730.model.base import Model

# ruff: noqa: N815 - camel case field names are tolerated to match schema


class StateMutability(StrEnum):
    pure = "pure"
    view = "view"
    nonpayable = "nonpayable"
    payable = "payable"


class Component(Model):
    name: str
    type: str
    internalType: str | None = None
    components: list[Self] | None = None


class InputOutput(Model):
    name: str
    type: str
    internalType: str | None = None
    components: list[Component] | None = None
    indexed: bool | None = None
    unit: str | None = None


class Function(Model):
    type: Literal["function"] = "function"
    name: str | None = None
    inputs: list[InputOutput] | None = None
    outputs: list[InputOutput] | None = None
    stateMutability: StateMutability | None = None
    constant: bool | None = None
    payable: bool | None = None
    gas: int | None = None
    signature: str | None = None


class Constructor(Model):
    type: Literal["constructor"] = "constructor"
    name: str | None = None
    inputs: list[InputOutput] | None = None
    outputs: list[InputOutput] | None = None
    stateMutability: StateMutability | None = None
    constant: bool | None = None
    payable: bool | None = None
    gas: int | None = None
    signature: str | None = None


class Receive(Model):
    type: Literal["receive"] = "receive"
    name: str | None = None
    inputs: list[InputOutput] | None = None
    outputs: list[InputOutput] | None = None
    stateMutability: StateMutability | None = None
    constant: bool | None = None
    payable: bool | None = None
    gas: int | None = None
    signature: str | None = None


class Fallback(Model):
    type: Literal["fallback"] = "fallback"
    name: str | None = None
    inputs: list[InputOutput] | None = None
    outputs: list[InputOutput] | None = None
    stateMutability: StateMutability | None = None
    constant: bool | None = None
    payable: bool | None = None
    gas: int | None = None
    signature: str | None = None


class Event(Model):
    type: Literal["event"] = "event"
    name: str
    inputs: list[InputOutput]
    anonymous: bool = False
    signature: str | None = None


class Error(Model):
    type: Literal["error"] = "error"
    name: str
    inputs: list[InputOutput]
    signature: str | None = None


ABI = Annotated[Constructor | Event | Function | Fallback | Error | Receive, Field(discriminator="type")]
