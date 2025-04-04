// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract KaiSign {
    enum Status {
        Submitted,
        Accepted,
        Rejected
    }

    struct ERC7730Spec {
        uint64 createdTimestamp;
        Status status;
        string ipfs;
    }

    mapping(bytes32 => ERC7730Spec) public specs;

    function createSpec(string calldata ipfs) external {
        bytes32 specID = keccak256(bytes(ipfs));
        require(specs[specID].createdTimestamp == 0, "Already proposed");
        specs[specID] = ERC7730Spec(uint64(block.timestamp), Status.Submitted, ipfs);
    }

    function getCreatedTimestamp(bytes32 id) external returns (uint64) {
        return specs[id].createdTimestamp;
    }

    function getStatus(bytes32 id) external returns (Status) {
        return specs[id].status;
    }

    function getIPFS(bytes32 id) external returns (string memory) {
        return specs[id].ipfs;
    }
}
