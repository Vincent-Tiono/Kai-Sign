// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {KaiSign} from "../src/KaiSign.sol";

contract KaiSignScript is Script {
    struct DeployParameters {
        address arbitrator;
        uint256 minBond;
        address realityETH;
        uint32 timeout;
    }

    string json = vm.readFile(string.concat(vm.projectRoot(), "/script/input/params.json"));
    bytes data = vm.parseJson(json);
    DeployParameters params = abi.decode(data, (DeployParameters));

    function setUp() public {}

    function run() public {
        vm.startBroadcast();
        new KaiSign(params.realityETH, params.arbitrator, params.minBond, params.timeout);
        vm.stopBroadcast();
    }
}
