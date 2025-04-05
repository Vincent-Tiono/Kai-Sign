import time
import json
import os
import sys
from query_and_evaluate import (
    load_deployment_config,
    query_the_graph,
    extract_question_data,
    fetch_ipfs_content,
    evaluate_ipfs_hash
)
import web3
from web3 import Web3
from eth_utils import to_bytes
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables from the contract directory
load_dotenv(dotenv_path='./.env', override=True)  # Add override=True to ensure values aren't cached
print("Read .env file")

# Database file to store processed IPFS hashes
DB_FILE = "processed_hashes.json"
MAX_HASHES = 100  # Maximum number of hashes to store

# Get RPC URL from environment (simpler approach like in the tutorial)
ETH_RPC_URL = os.getenv('SEPOLIA_RPC_URL')
print(f"Using RPC URL: {ETH_RPC_URL}")
CONTRACT_ABI_PATH = "../contracts/abi/RealityETH_v3_0.json"  # Path to contract ABI

# Bot wallet settings from environment
BOT_ADDRESS = os.getenv('BOT_ADDRESS')
BOT_PRIVATE_KEY = os.getenv('BOT_PRIVATE_KEY')

# Create Web3 connection
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# Print connection status
print(f"Connected to Ethereum: {w3.is_connected()}")
if w3.is_connected():
    print(f"Current block number: {w3.eth.block_number}")
else:
    print("Warning: Failed to connect to Ethereum node. Please check your SEPOLIA_RPC_URL in the .env file.")

def load_contract_abi():
    """Load the contract ABI from the JSON file."""
    try:
        with open(CONTRACT_ABI_PATH, 'r') as f:
            contract_data = json.load(f)
            return contract_data["abi"]
    except Exception as e:
        print(f"Error loading contract ABI: {e}")
        return None

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

def submit_challenge(question_id, current_bond, contract_address):
    """Submit a challenge to the contract for a false evaluation using submitAnswer."""
    if not contract_address:
        print("Error: No contract address provided")
        return False
    
    try:
        # We'll use the global w3 instance already established
        if not w3.is_connected():
            print(f"Error: Not connected to Ethereum node")
            return False
        
        # Load contract ABI
        contract_abi = load_contract_abi()
        if not contract_abi:
            print("Error: Could not load contract ABI")
            return False
        
        # Load contract
        print(f"Loading contract at address {contract_address}")
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        # Set up account from private key (similar to the tutorial)
        account = Account.from_key(BOT_PRIVATE_KEY)
        print(f"Using account: {account.address}")
        
        # Calculate required bond amount (double the current bond)
        bond_amount = int(current_bond) * 2
        if bond_amount == 0:
            # If current bond is 0, use a minimum amount
            bond_amount = w3.to_wei(0.01, 'ether')
        
        print(f"Required bond amount: {bond_amount} wei")
        
        # The "false" answer in bytes32 format (0x0 for False)
        false_answer = b'\x00' * 32  # 0 in bytes32 format
        
        # Max previous is the current bond amount
        max_previous = int(current_bond)
        
        # Get nonce for the transaction
        nonce = w3.eth.get_transaction_count(account.address)
        
        print("Checking if question is finalized------------------")
        print(question_id)
        print(contract)
        
        is_finalized = contract.functions.isFinalized(question_id).call()
        print(f"Is finalized: {is_finalized}")
        
        if is_finalized:
            print(f"Question {question_id} is already finalized. Cannot submit challenge.")
            return False
        
        # Call submitAnswer function (similar to the tutorial's sendTX)
        tx = contract.functions.submitAnswer(
            question_id,    # The question ID
            false_answer,   # The answer (0x0 for false)
            max_previous    # Max previous bond
        ).build_transaction({
            "from": account.address,
            "value": bond_amount,
            "nonce": nonce,
        })
        
        # Estimate gas
        gas = w3.eth.estimate_gas(tx)
        print(f"Gas estimate: {gas}")
        tx['gas'] = gas
        
        # Sign and send the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=BOT_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"Transaction sent: {tx_hash.hex()}")
        print("Waiting for transaction to be mined...")
        
        # Wait for the transaction to be mined
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print(f"Challenge submitted successfully! Transaction hash: {tx_hash.hex()}")
            return True
        else:
            print(f"Challenge transaction failed! Transaction hash: {tx_hash.hex()}")
            return False
        
    except web3.exceptions.ContractLogicError as err:
        print(f"Contract logic error: {err}")
        return False
    except Exception as e:
        print(f"Error submitting challenge: {e}")
        return False

def check_for_new_data(interval_seconds, api_key, processed_hashes):
    """Check for new data from the Graph API."""
    # Load configuration
    try:
        # Use the specific contract address for querying The Graph
        query_contract_address = "0x2d2f90786a365a2044324f6861697e9EF341F858"
        print(f"Querying The Graph API for contract: {query_contract_address}")
        
        # Query The Graph API
        response_data = query_the_graph(query_contract_address, api_key)
        
        # Print raw response data for debugging
        print(f"Graph API response: {json.dumps(response_data, indent=2)}")
        
        # For blockchain transactions/challenges, use this specific address
        transaction_contract_address = "0xaf33DcB6E8c5c4D9dDF579f53031b514d19449CA"
        
        # Extract question data
        questions = extract_question_data(response_data)
        
        # Check for new questions
        new_found = False
        for question in questions:
            ipfs_hash = question['data']
            question_id = question['questionId']
            bond = question['bond']
            
            if ipfs_hash not in processed_hashes:
                print(f"New data found: {ipfs_hash} (Question ID: {question_id})")
                
                # Fetch content from IPFS
                content = fetch_ipfs_content(ipfs_hash)
                
                # Evaluate using LLM
                result = evaluate_ipfs_hash(ipfs_hash)
                
                if result:
                    print("Evaluation result: Good - No challenge needed")
                else:
                    print("Evaluation result: Bad - Submitting challenge...")
                    # Submit challenge to the contract
                    challenge_submitted = submit_challenge(question_id, bond, transaction_contract_address)
                    if challenge_submitted:
                        print(f"Successfully challenged question {question_id}")
                    else:
                        print(f"Failed to challenge question {question_id}")
                
                # Add to processed list (FIFO - will be trimmed if exceeds MAX_HASHES)
                processed_hashes.append(ipfs_hash)
                if len(processed_hashes) > MAX_HASHES:
                    removed_hash = processed_hashes.pop(0)  # Remove oldest hash (FIFO)
                    print(f"Database limit reached. Removed oldest hash: {removed_hash}")
                
                new_found = True
        
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
    print(f"Using bot wallet address: {BOT_ADDRESS}")
    
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