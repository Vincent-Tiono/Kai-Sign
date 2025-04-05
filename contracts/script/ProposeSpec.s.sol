// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {KaiSign} from "../src/KaiSign.sol";

contract ProposeSpec is Script {
    function setUp() public {}

    function run(address kaisign, string calldata ipfs) public {
        vm.startBroadcast();
        uint256 minBond = KaiSign(kaisign).minBond();
        KaiSign(kaisign).createSpec(ipfs);
        KaiSign(kaisign).proposeSpec{value: minBond}(ipfs);
        vm.stopBroadcast();
    }
}
