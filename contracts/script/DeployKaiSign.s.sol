// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {DeployParam} from "./DeployParam.sol";
import {KaiSign} from "../src/KaiSign.sol";

contract KaiSignScript is Script, DeployParam {
    function setUp() public {}

    function run() public {
        vm.startBroadcast();
        DeployParams memory params = getDeployParams();
        new KaiSign(params.realityETH, params.arbitrator, params.minBond, params.timeout);
        vm.stopBroadcast();
    }
}
