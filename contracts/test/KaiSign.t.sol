// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {KaiSign} from "../src/KaiSign.sol";

contract KaiSignTest is Test {
    KaiSign public kaisign;
    address public realityETH;
    address public arbitrator;

    function setUp() public {
        kaisign = new KaiSign(realityETH, arbitrator, uint256(1000000000000000));
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        kaisign.createSpec(ipfs_hash);
    }

    function test_submitEntryCreatesEntry() public {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        bytes32 id = keccak256(bytes(ipfs_hash));
        assertGt(kaisign.getCreatedTimestamp(id), 0);
    }

    function test_submitDuplicateEntryFails() public {
        string memory ipfs_hash = "Qmbdr7gTLeWZYLVHALapahbcDQtsGDvoYRcVS73QYGnTmk";
        bytes32 id = keccak256(bytes(ipfs_hash));
        vm.expectRevert();
        kaisign.createSpec(ipfs_hash);
    }
}
