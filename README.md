# Kai-Sign
This is the repository for the project Kai-Sign.



## Deploying the contracts

Copy `env.example` to `.env` and fill in the blanks.

Fill in `script/input/params.json`

`forge script --chain sepolia script/DeployKaiSign.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --etherscan-api-key $ETHERSCAN_API_KEY --broadcast --verify`

## Using the contracts from forge

### Propose a spec

`ipfs add myspec.json`

`ipfs pin add myspec.json`

`forge script --chain sepolia script/ProposeSpec.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --broadcast --sig="run(address,string)"
