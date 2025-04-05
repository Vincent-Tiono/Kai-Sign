import {
  assert,
  describe,
  test,
  clearStore,
  beforeAll,
  afterAll
} from "matchstick-as/assembly/index"
import { Address, Bytes, BigInt } from "@graphprotocol/graph-ts"
import { LogAssertSpecInvalid } from "../generated/schema"
import { LogAssertSpecInvalid as LogAssertSpecInvalidEvent } from "../generated/KaiSign/KaiSign"
import { handleLogAssertSpecInvalid } from "../src/kai-sign"
import { createLogAssertSpecInvalidEvent } from "./kai-sign-utils"

// Tests structure (matchstick-as >=0.5.0)
// https://thegraph.com/docs/en/developer/matchstick/#tests-structure-0-5-0

describe("Describe entity assertions", () => {
  beforeAll(() => {
    let user = Address.fromString("0x0000000000000000000000000000000000000001")
    let specID = Bytes.fromI32(1234567890)
    let questionId = Bytes.fromI32(1234567890)
    let bond = BigInt.fromI32(234)
    let newLogAssertSpecInvalidEvent = createLogAssertSpecInvalidEvent(
      user,
      specID,
      questionId,
      bond
    )
    handleLogAssertSpecInvalid(newLogAssertSpecInvalidEvent)
  })

  afterAll(() => {
    clearStore()
  })

  // For more test scenarios, see:
  // https://thegraph.com/docs/en/developer/matchstick/#write-a-unit-test

  test("LogAssertSpecInvalid created and stored", () => {
    assert.entityCount("LogAssertSpecInvalid", 1)

    // 0xa16081f360e3847006db660bae1c6d1b2e17ec2a is the default address used in newMockEvent() function
    assert.fieldEquals(
      "LogAssertSpecInvalid",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "user",
      "0x0000000000000000000000000000000000000001"
    )
    assert.fieldEquals(
      "LogAssertSpecInvalid",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "specID",
      "1234567890"
    )
    assert.fieldEquals(
      "LogAssertSpecInvalid",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "questionId",
      "1234567890"
    )
    assert.fieldEquals(
      "LogAssertSpecInvalid",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "bond",
      "234"
    )

    // More assert options:
    // https://thegraph.com/docs/en/developer/matchstick/#asserts
  })
})
