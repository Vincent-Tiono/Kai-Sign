# Kai-Sign
This is the repository for the project Kai-Sign.

## Project Overview
Kai-Sign is a platform where users can create and verify ERC7730 metadata. The workflow involves:

1. Users build ERC7730 metadata specifications
2. These specifications are sent to Reality.eth, a crowdsourced market verification system
3. After passing verification, the metadata is curated and displayed on a single page

This approach ensures trusted and verified metadata through decentralized consensus mechanisms.

## Core Team

Team of talented engineers, web developers and the founder of reality.eth, a crowdsourced market collaborated with Kleros.

- [Vincent-Tiono](https://github.com/Vincent-Tiono)
- [Nathanael349](https://github.com/Nathanael349)
- [keithlim123](https://github.com/keithlim123)
- [edmundedgar](https://github.com/edmundedgar)
- [muhammadaus](https://github.com/muhammadaus)

## Integration with MultiBaas from Curvegrid

- **MultiBaas REST API** integration directly for blockchain data access
- **Event Queries** for verified metadata updates
- **Direct frontend app development** using CORS origins for secure cross-origin requests

*refer to the setup instructions below for more

## Deploying the contracts

Copy `env.example` to `.env` and fill in the blanks.

Fill in `script/input/params.json`

`forge script --chain sepolia script/DeployKaiSign.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --etherscan-api-key $ETHERSCAN_API_KEY --broadcast --verify`

## Using the contracts from forge

### Propose a spec

`ipfs add myspec.json`

`ipfs pin add myspec.json`

`forge script --chain sepolia script/ProposeSpec.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --broadcast --sig="run(address,string)"`

### Oppose a spec

`forge script --chain sepolia script/OpposeSpec.s.sol --private-key $PRIVATE_KEY --rpc-url $SEPOLIA_RPC_URL --broadcast --sig="run(address,string,uint256)"`

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

- [Download Multibaas Slide Deck](Multibaas-slide-deck/Multibaas.pdf)
