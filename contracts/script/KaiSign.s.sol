// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {KaiSign} from "../src/KaiSign.sol";

contract KaiSignScript is Script {
    KaiSign public counter;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        //counter = new KaiSign();

        vm.stopBroadcast();
    }
}
