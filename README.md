# Kai-Sign

## What this is for

People keep losing money because they don't know what their wallets are signing. ByBit lost 1.4 Billion dollars. Ledger made a standard called ERC7730 to help describe contract actions in English so they the wallet can display them to the user. But it uses a centralized repo controlled by them. Other hardware wallets don't want to use that.

We built a tool for decentralized on-chain curation of ERC7730 specs using the reality.eth optimistic oracle and Kleros, and we forked the [Ledger ERC7730 creation tool](https://github.com/LedgerHQ/clear-signing-erc7730-builder) to link it up to the on-chain system. 

We also built an AI bot to detect bad ERC7730 submissions and challenge them. Anyone can run their own bot and improve on it and make money by detecting bad submissions.

## Workflow

Kai-Sign is a platform where users can create and verify ERC7730 metadata. The workflow involves:

1. Users build ERC7730 metadata specifications.
2. These specifications are sent to Reality.eth, a crowdsourced verification system using an escalation game, backstopped by Kleros.
3. After passing verification, the metadata is curated and displayed on a single page.

This approach ensures trusted and verified metadata through decentralized consensus mechanisms.

## Core Team

Three students from the National Taiwan University and two guys they met on Discord.

- [Vincent-Tiono](https://github.com/Vincent-Tiono)
- [Nathanael349](https://github.com/Nathanael349)
- [keithlim123](https://github.com/keithlim123)
- [edmundedgar](https://github.com/edmundedgar) (built [reality.eth](https://reality.eth.link/) )
- [muhammadaus](https://github.com/muhammadaus)

## Deploying the contracts

Copy `env.example` to `.env` and fill in the blanks.

Fill in `script/input/params.json`

`forge script --chain sepolia script/DeployKaiSign.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --etherscan-api-key $ETHERSCAN_API_KEY --broadcast --verify`

### Deployed contracts
(main repository)

Sepolia: [0x2d2f90786a365a2044324f6861697e9EF341F858](https://sepolia.etherscan.io/address/0x2d2f90786a365a2044324f6861697e9EF341F858)

(celo-deployment repository)

Celo: [0x64b1601A844F2E83715168E2f7C3e05135CBaB0a](https://celoscan.io/address/0x64b1601A844F2E83715168E2f7C3e05135CBaB0a)

## Using the contracts from forge

### Propose a spec

`ipfs add myspec.json`

`ipfs pin add myspec.json`

`forge script --chain sepolia script/ProposeSpec.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --broadcast --sig="run(address,string)"`

### Oppose a spec

`forge script --chain sepolia script/OpposeSpec.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --broadcast --sig="run(address,string,uint256)"`

## Integration with MultiBaas from Curvegrid

- **MultiBaas REST API** integration directly for blockchain data access
- **Event Queries** for verified metadata updates
- **Direct frontend app development** using CORS origins for secure cross-origin requests

*refer to the setup instructions below for more

## MultiBaas Setup and Testing

### Prerequisites
- MultiBaas instance access (from [Curvegrid](https://www.curvegrid.com/))
- JWT authentication token for API access

### Environment Setup
1. Set up environment variables in your `.env` file:
   ```
   CURVEGRID_JWT=your_jwt_token
   ```

2. Make sure your JWT token is properly formatted:
   ```javascript
   // Clean the JWT token by removing spaces
   const rawJwt = env.CURVEGRID_JWT || "";
   const jwt = rawJwt.trim().replace(/\s*=\s*/, '=').replace(/^"(.*)"$/, '$1');
   ```

### Fetching Event Data
To fetch contract events such as `LogHandleResult` directly from the MultiBaas API:

```javascript
// Example API call for event queries
async function fetchLogHandleResults() {
  const hostname = "your-instance.multibaas.com";
  const jwt = process.env.CURVEGRID_JWT;
  
  const response = await fetch(
    `https://${hostname}/api/v0/queries`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${jwt}`
      },
      body: JSON.stringify({
        events: [
          {
            select: [
              { name: "specID", type: "input", alias: "", inputIndex: 0 },
              { name: "isAccepted", type: "input", alias: "", inputIndex: 1 },
              { name: "block_number", type: "block_number", alias: "" },
              { name: "tx_hash", type: "tx_hash", alias: "" },
              { name: "triggered_at", type: "triggered_at", alias: "" }
            ],
            eventName: "LogHandleResult(bytes32,bool)"
          }
        ]
      })
    }
  );

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }
  
  const data = await response.json();
  return data.result.rows;
}
```

### Processing Event Data
Example of processing the event data returned from MultiBaas:

```javascript
// Process event data into application format
function processEvents(rows) {
  return rows.map(row => {
    let specID = row.specid || row.specID;
    if (Array.isArray(specID)) {
      specID = '0x' + Array.from(specID)
        .map(num => num.toString(16).padStart(2, '0'))
        .join('');
    }
    
    const isAccepted = 
      row.isaccepted === true || 
      row.isaccepted === "true" || 
      row.isaccepted === 1 ||
      row.isAccepted === true || 
      row.isAccepted === "true" || 
      row.isAccepted === 1;
    
    return {
      blockNumber: parseInt(row.block_number, 10) || 0,
      transactionHash: row.tx_hash || "",
      timestamp: Math.floor(new Date(row.triggered_at).getTime() / 1000),
      args: {
        specID: specID,
        isAccepted: isAccepted
      }
    };
  });
}
```

### Multibaas feedback

A simple approach to access the front end without manipulating the actual scripts.
Easy to monitor tools on managing smart contracts without relying blockchain explorers.
Customizable logic for data pipeline.

Note: Cloud Wallet usage requires Azure registration

### Slide Deck for MultiBaas integration.

- [Multibaas Slide Deck](Multibaas-slide-deck/Multibaas.pdf)
