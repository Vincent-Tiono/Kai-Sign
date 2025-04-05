#!/bin/bash

# Read the kaisignContract address from deployment.json
CONTRACT_ADDRESS=$(cat ../deployment.json | grep -o '"kaisignContract": "[^"]*"' | cut -d'"' -f4)

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "Error: Could not find kaisignContract in deployment.json"
    exit 1
fi

echo "Using contract address: $CONTRACT_ADDRESS"

# Use the provided API key
API_KEY="be5ddfca879e5ea553aa90060c35999a"
echo "Using API key: $API_KEY"

# Create the query with the contract address
QUERY="{\"query\": \"{ questions(where: {user: \\\"$CONTRACT_ADDRESS\\\"}) { data } }\", \"operationName\": \"Subgraphs\", \"variables\": {}}"
echo "Query: $QUERY"

# Execute the curl command with API key in URL
echo "Executing curl command..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d "$QUERY" \
  https://gateway.thegraph.com/api/$API_KEY/subgraphs/id/F3XjWNiNFUTbZhNQjXuhP7oDug2NaPwMPZ5XCRx46h5U

echo -e "\n\nDone!" 