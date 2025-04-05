#!/bin/bash

# This script simulates getting IPFS hashes and evaluating them with hash_prob.py
# since we are experiencing authentication issues with The Graph API

echo "=== Testing hash_prob.py with sample IPFS hashes ==="

# Create a directory for sample specs
mkdir -p sample_specs

# Sample IPFS hashes for testing
# These are just examples, you should replace them with real IPFS hashes if available
SAMPLE_HASHES=(
  "QmP1GgHq8y9HimUJzrSDCFg54FvHpiD1hqVhF7YeC171jH"
  "QmU2kfV4YsUxpZ2cVnpMGKYJnP7sUAd2HZs14RrwmBpEDs"
)

echo "Found ${#SAMPLE_HASHES[@]} sample IPFS hashes for testing."

# Process each sample hash
for i in "${!SAMPLE_HASHES[@]}"; do
  HASH="${SAMPLE_HASHES[$i]}"
  
  echo -e "\n=== Processing IPFS hash $((i+1))/${#SAMPLE_HASHES[@]}: $HASH ==="
  
  # Save the hash to a file
  echo "$HASH" > "sample_specs/ipfs_hash_$((i+1)).txt"
  
  # Run hash_prob.py with the sample hash
  echo "Running: python hash_prob.py $HASH"
  python hash_prob.py "$HASH"
  
  # Check if the evaluation was successful
  if [ $? -eq 0 ]; then
    echo "Successfully evaluated IPFS hash."
  else
    echo "Failed to evaluate IPFS hash."
  fi
done

echo -e "\n=== Testing complete ===" 