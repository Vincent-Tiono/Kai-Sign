import sys

def evaluate_hash(ipfs_hash):
    # Simplified evaluation for testing
    # In a real scenario, this would call your LLM evaluation logic
    # For testing, let's say all hashes ending with 'a' are "Good"
    if ipfs_hash.endswith('a'):
        return "Good: 0.8, Bad: 0.2"
    else:
        return "Good: 0.2, Bad: 0.8"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ipfs_hash = sys.argv[1]
        result = evaluate_hash(ipfs_hash)
        print(result)
    else:
        print("Please provide an IPFS hash")
