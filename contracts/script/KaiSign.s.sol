// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {KaiSign} from "../src/KaiSign.sol";

contract KaiSignScript is Script {

    // Oracle settings for sepolia from:
    // https://github.com/RealityETH/reality-eth-monorepo/blob/main/packages/contracts/chains/deployments/11155111/ETH/RealityETH-3.0.json
    address realityETH = 0xaf33DcB6E8c5c4D9dDF579f53031b514d19449CA; // reality.eth 3.0 sepolia
    address arbitrator = 0x05B942fAEcfB3924970E3A28e0F230910CEDFF45; // kleros arbitrator sepolia

    uint256 minBond = 100000000000000;
    uint32 timeout = 60; // special short timeout for demos

    function setUp() public {}

    function run() public {
        vm.startBroadcast();
        new KaiSign(realityETH, arbitrator, minBond, timeout);
        vm.stopBroadcast();
    }
}
