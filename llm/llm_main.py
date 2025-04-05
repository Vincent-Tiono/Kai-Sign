import time
import json
import os
import sys
from query_and_evaluate import (
    load_deployment_config,
    query_the_graph,
    extract_ipfs_hashes,
    fetch_ipfs_content,
    evaluate_ipfs_hash
)

# Database file to store processed IPFS hashes
DB_FILE = "processed_hashes.json"
MAX_HASHES = 100  # Maximum number of hashes to store

def load_processed_hashes():
    """Load the list of already processed IPFS hashes."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                hashes = json.load(f)
                # Ensure we only keep the most recent MAX_HASHES
                if len(hashes) > MAX_HASHES:
                    hashes = hashes[-MAX_HASHES:]  # Keep only the most recent ones
                return hashes
        except json.JSONDecodeError:
            print(f"Error reading {DB_FILE}, starting with empty database")
    return []

def save_processed_hashes(processed_hashes):
    """Save the list of processed IPFS hashes, maintaining FIFO with max size."""
    # Ensure we only keep the most recent MAX_HASHES
    if len(processed_hashes) > MAX_HASHES:
        processed_hashes = processed_hashes[-MAX_HASHES:]  # Keep only the most recent ones
    
    with open(DB_FILE, 'w') as f:
        json.dump(processed_hashes, f, indent=2)

def check_for_new_data(interval_seconds, api_key, processed_hashes):
    """Check for new data from the Graph API."""
    # Load configuration
    try:
        config = load_deployment_config()
        contract_address = config.get('kaisignContract')
        
        if not contract_address:
            print("Error: kaisignContract address not found in deployment.json")
            return processed_hashes, False
        
        # Query The Graph API
        response_data = query_the_graph(contract_address, api_key)
        
        # Extract IPFS hashes
        ipfs_hashes = extract_ipfs_hashes(response_data)
        
        # Check for new hashes
        new_found = False
        for ipfs_hash in ipfs_hashes:
            if ipfs_hash not in processed_hashes:
                print(f"New data found: {ipfs_hash}")
                
                # Fetch content from IPFS
                content = fetch_ipfs_content(ipfs_hash)
                
                # Evaluate using LLM
                result = evaluate_ipfs_hash(ipfs_hash)
                
                # Add to processed list (FIFO - will be trimmed if exceeds MAX_HASHES)
                processed_hashes.append(ipfs_hash)
                if len(processed_hashes) > MAX_HASHES:
                    removed_hash = processed_hashes.pop(0)  # Remove oldest hash (FIFO)
                    print(f"Database limit reached. Removed oldest hash: {removed_hash}")
                
                new_found = True
                
                print(f"Evaluated result: {'Good' if result else 'Bad'}")
        
        if not new_found:
            print(f"No new data found. Checking again in {interval_seconds} seconds...")
        
        # Save updated list
        save_processed_hashes(processed_hashes)
        
        return processed_hashes, new_found
        
    except Exception as e:
        print(f"Error checking for new data: {e}")
        return processed_hashes, False

def main():
    """Main function to periodically check for new data."""
    # Default checking interval in seconds
    interval_seconds = 60
    
    # Allow command-line override of interval
    if len(sys.argv) > 1:
        try:
            interval_seconds = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval: {sys.argv[1]}. Using default: {interval_seconds} seconds")
    
    print(f"Starting periodic checks every {interval_seconds} seconds...")
    print(f"Database limited to {MAX_HASHES} hashes (FIFO)")
    
    # API key
    api_key = "be5ddfca879e5ea553aa90060c35999a"
    
    # Load already processed hashes
    processed_hashes = load_processed_hashes()
    print(f"Loaded {len(processed_hashes)} previously processed hashes")
    
    try:
        while True:
            processed_hashes, new_found = check_for_new_data(
                interval_seconds, api_key, processed_hashes
            )
            
            # Sleep for the interval
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nStopping periodic checks...")
        # Save processed hashes one last time
        save_processed_hashes(processed_hashes)

if __name__ == "__main__":
    main() 