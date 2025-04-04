// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {KaiSign} from "../src/KaiSign.sol";
import {RealityETH_v3_0} from "../staticlib/RealityETH-3.0.sol";

contract KaiSignTest is Test {
    KaiSign public kaisign;
    RealityETH_v3_0 public realityETH = new RealityETH_v3_0();
    address public arbitrator;
    uint256 minBond = 1000000000000000;
    uint32 timeout = 86400;

    function setUp() public {
        kaisign = new KaiSign(address(realityETH), arbitrator, minBond, timeout);
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        kaisign.createSpec(ipfs_hash);
    }

    function test_submitEntryCreatesEntry() public view {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        assertGt(kaisign.getCreatedTimestamp(ipfs_hash), 0);
    }

    function test_submitDuplicateEntryFails() public {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        vm.expectRevert();
        kaisign.createSpec(ipfs_hash);
    }

    function test_proposeWithBond() public {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        kaisign.proposeSpec{value: minBond}(ipfs_hash);
    }

    function test_challengeEntry() public {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        kaisign.proposeSpec{value: minBond}(ipfs_hash);
        kaisign.assertSpecInvalid{value: minBond * 2}(ipfs_hash);
        bytes32 questionId = kaisign.getQuestionId(ipfs_hash);
        assertEq(realityETH.getBestAnswer(questionId), bytes32(0));
    }

    function test_getResultAcceptance() public {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        kaisign.proposeSpec{value: minBond}(ipfs_hash);
        assertFalse(kaisign.isAccepted(ipfs_hash));
        vm.warp(block.timestamp + timeout + 1);
        kaisign.handleResult(ipfs_hash);
        assertTrue(kaisign.isAccepted(ipfs_hash));
    }

    function test_getResultRejection() public {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        kaisign.proposeSpec{value: minBond}(ipfs_hash);
        assertFalse(kaisign.isAccepted(ipfs_hash));

        bytes32 questionId = kaisign.getQuestionId(ipfs_hash);
        RealityETH_v3_0(realityETH).submitAnswer{value: minBond * 2}(questionId, bytes32(uint256(0)), 0);

        vm.warp(block.timestamp + timeout + 1);
        kaisign.handleResult(ipfs_hash);
        assertFalse(kaisign.isAccepted(ipfs_hash));
    }
}
