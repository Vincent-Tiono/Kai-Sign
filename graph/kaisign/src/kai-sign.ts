import {
  LogAssertSpecInvalid as LogAssertSpecInvalidEvent,
  LogAssertSpecValid as LogAssertSpecValidEvent,
  LogCreateSpec as LogCreateSpecEvent,
  LogHandleResult as LogHandleResultEvent,
  LogProposeSpec as LogProposeSpecEvent
} from "../generated/KaiSign/KaiSign"
import {
  LogAssertSpecInvalid,
  LogAssertSpecValid,
  LogCreateSpec,
  LogHandleResult,
  LogProposeSpec,
  Spec
} from "../generated/schema"

export function handleLogAssertSpecInvalid(
  event: LogAssertSpecInvalidEvent
): void {
  let entity = new LogAssertSpecInvalid(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.user = event.params.user
  entity.specID = event.params.specID
  entity.questionId = event.params.questionId
  entity.bond = event.params.bond

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleLogAssertSpecValid(event: LogAssertSpecValidEvent): void {
  let entity = new LogAssertSpecValid(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.user = event.params.user
  entity.specID = event.params.specID
  entity.questionId = event.params.questionId
  entity.bond = event.params.bond

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleLogCreateSpec(event: LogCreateSpecEvent): void {
  let entity = new LogCreateSpec(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.user = event.params.user
  entity.specID = event.params.specID
  entity.ipfs = event.params.ipfs

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()

  let spec = new Spec(
    event.params.specID
  )
  spec.user = event.params.user
  spec.ipfs = event.params.ipfs
  spec.save()
}

export function handleLogHandleResult(event: LogHandleResultEvent): void {
  let entity = new LogHandleResult(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.specID = event.params.specID
  entity.isAccepted = event.params.isAccepted

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()

  let spec = Spec.load(event.params.specID)
  if (spec != null) {
    spec.isFinalized = true
    spec.isAccepted = event.params.isAccepted
  }
}

export function handleLogProposeSpec(event: LogProposeSpecEvent): void {
  let entity = new LogProposeSpec(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.user = event.params.user
  entity.specID = event.params.specID
  entity.questionId = event.params.questionId
  entity.bond = event.params.bond

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()

  let spec = Spec.load(event.params.specID)
  if (spec != null) {
    spec.questionId = event.params.questionId;
    spec.save()
  }
}
