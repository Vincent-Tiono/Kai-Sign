import { newMockEvent } from "matchstick-as"
import { ethereum, Address, Bytes, BigInt } from "@graphprotocol/graph-ts"
import {
  LogAssertSpecInvalid,
  LogAssertSpecValid,
  LogCreateSpec,
  LogHandleResult,
  LogProposeSpec
} from "../generated/KaiSign/KaiSign"

export function createLogAssertSpecInvalidEvent(
  user: Address,
  specID: Bytes,
  questionId: Bytes,
  bond: BigInt
): LogAssertSpecInvalid {
  let logAssertSpecInvalidEvent =
    changetype<LogAssertSpecInvalid>(newMockEvent())

  logAssertSpecInvalidEvent.parameters = new Array()

  logAssertSpecInvalidEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )
  logAssertSpecInvalidEvent.parameters.push(
    new ethereum.EventParam("specID", ethereum.Value.fromFixedBytes(specID))
  )
  logAssertSpecInvalidEvent.parameters.push(
    new ethereum.EventParam(
      "questionId",
      ethereum.Value.fromFixedBytes(questionId)
    )
  )
  logAssertSpecInvalidEvent.parameters.push(
    new ethereum.EventParam("bond", ethereum.Value.fromUnsignedBigInt(bond))
  )

  return logAssertSpecInvalidEvent
}

export function createLogAssertSpecValidEvent(
  user: Address,
  specID: Bytes,
  questionId: Bytes,
  bond: BigInt
): LogAssertSpecValid {
  let logAssertSpecValidEvent = changetype<LogAssertSpecValid>(newMockEvent())

  logAssertSpecValidEvent.parameters = new Array()

  logAssertSpecValidEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )
  logAssertSpecValidEvent.parameters.push(
    new ethereum.EventParam("specID", ethereum.Value.fromFixedBytes(specID))
  )
  logAssertSpecValidEvent.parameters.push(
    new ethereum.EventParam(
      "questionId",
      ethereum.Value.fromFixedBytes(questionId)
    )
  )
  logAssertSpecValidEvent.parameters.push(
    new ethereum.EventParam("bond", ethereum.Value.fromUnsignedBigInt(bond))
  )

  return logAssertSpecValidEvent
}

export function createLogCreateSpecEvent(
  user: Address,
  specID: Bytes,
  ipfs: string
): LogCreateSpec {
  let logCreateSpecEvent = changetype<LogCreateSpec>(newMockEvent())

  logCreateSpecEvent.parameters = new Array()

  logCreateSpecEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )
  logCreateSpecEvent.parameters.push(
    new ethereum.EventParam("specID", ethereum.Value.fromFixedBytes(specID))
  )
  logCreateSpecEvent.parameters.push(
    new ethereum.EventParam("ipfs", ethereum.Value.fromString(ipfs))
  )

  return logCreateSpecEvent
}

export function createLogHandleResultEvent(
  specID: Bytes,
  isAccepted: boolean
): LogHandleResult {
  let logHandleResultEvent = changetype<LogHandleResult>(newMockEvent())

  logHandleResultEvent.parameters = new Array()

  logHandleResultEvent.parameters.push(
    new ethereum.EventParam("specID", ethereum.Value.fromFixedBytes(specID))
  )
  logHandleResultEvent.parameters.push(
    new ethereum.EventParam(
      "isAccepted",
      ethereum.Value.fromBoolean(isAccepted)
    )
  )

  return logHandleResultEvent
}

export function createLogProposeSpecEvent(
  user: Address,
  specID: Bytes,
  questionId: Bytes,
  bond: BigInt
): LogProposeSpec {
  let logProposeSpecEvent = changetype<LogProposeSpec>(newMockEvent())

  logProposeSpecEvent.parameters = new Array()

  logProposeSpecEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )
  logProposeSpecEvent.parameters.push(
    new ethereum.EventParam("specID", ethereum.Value.fromFixedBytes(specID))
  )
  logProposeSpecEvent.parameters.push(
    new ethereum.EventParam(
      "questionId",
      ethereum.Value.fromFixedBytes(questionId)
    )
  )
  logProposeSpecEvent.parameters.push(
    new ethereum.EventParam("bond", ethereum.Value.fromUnsignedBigInt(bond))
  )

  return logProposeSpecEvent
}
