// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {KaiSign} from "../src/KaiSign.sol";

contract ProposeSpec is Script {
    function setUp() public {}

    function run(address kaisign, string calldata ipfs, uint256 bond) public {
        vm.startBroadcast();
        uint256 minBond = KaiSign(kaisign).minBond();
        bond = bond > 0 ? bond : minBond * 2;
        KaiSign(kaisign).assertSpecInvalid{value: bond}(ipfs);
        vm.stopBroadcast();
    }
}
