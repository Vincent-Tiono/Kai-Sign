// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";

abstract contract DeployParam is Script {
    struct DeployParams {
        address arbitrator;
        uint256 minBond;
        address realityETH;
        uint32 timeout;
    }

    function getDeployParams() internal view returns (DeployParams memory) {
        string memory json = vm.readFile(string.concat(vm.projectRoot(), "/script/input/params.json"));
        bytes memory data = vm.parseJson(json);
        DeployParams memory params = abi.decode(data, (DeployParams));
        return params;
    }
}
