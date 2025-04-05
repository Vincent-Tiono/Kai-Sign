import time
import json
import os
import sys
from query_and_evaluate import (
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

# Load environment variables
load_dotenv(dotenv_path='./.env', override=True)

# Configuration
DB_FILE = "/tmp/processed_hashes.json"
MAX_HASHES = 100
ETH_RPC_URL = os.getenv('SEPOLIA_RPC_URL')
CONTRACT_ABI_PATH = "../contracts/abi/RealityETH_v3_0.json"
BOT_ADDRESS = os.getenv('BOT_ADDRESS')
BOT_PRIVATE_KEY = os.getenv('BOT_PRIVATE_KEY')
QUERY_CONTRACT_ADDRESS = "0x2d2f90786a365a2044324f6861697e9EF341F858"
TRANSACTION_CONTRACT_ADDRESS = "0xaf33DcB6E8c5c4D9dDF579f53031b514d19449CA"

# Create Web3 connection
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

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
    # if os.path.exists(DB_FILE):
    #     try:
    #         with open(DB_FILE, 'r') as f:
    #             hashes = json.load(f)
    #             if len(hashes) > MAX_HASHES:
    #                 hashes = hashes[-MAX_HASHES:]
    #             return hashes
    #     except json.JSONDecodeError:
    #         return []
    return []

def save_processed_hashes(processed_hashes):
    """Save the list of processed IPFS hashes, maintaining FIFO with max size."""
    # if len(processed_hashes) > MAX_HASHES:
    #     processed_hashes = processed_hashes[-MAX_HASHES:]
    
    # with open(DB_FILE, 'w') as f:
    #     json.dump(processed_hashes, f, indent=2)
    continue

def submit_challenge(question_id, current_bond, contract_address):
    """Submit a challenge to the contract for a false evaluation using submitAnswer."""
    if not contract_address:
        return False, None
    
    try:
        if not w3.is_connected():
            return False, None
        
        contract_abi = load_contract_abi()
        if not contract_abi:
            return False, None
        
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        account = Account.from_key(BOT_PRIVATE_KEY)
        
        # Calculate required bond amount (double the current bond)
        bond_amount = int(current_bond) * 2
        if bond_amount == 0:
            bond_amount = w3.to_wei(0.01, 'ether')
        
        # The "false" answer in bytes32 format
        false_answer = b'\x00' * 32
        max_previous = int(current_bond)
        nonce = w3.eth.get_transaction_count(account.address)
        
        is_finalized = contract.functions.isFinalized(question_id).call()
        if is_finalized:
            return False, "finalized"
        
        tx = contract.functions.submitAnswer(
            question_id,
            false_answer,
            max_previous
        ).build_transaction({
            "from": account.address,
            "value": bond_amount,
            "nonce": nonce,
        })
        
        gas = w3.eth.estimate_gas(tx)
        tx['gas'] = gas
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=BOT_PRIVATE_KEY).raw_transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx)
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            return True, {"question_id": question_id, "bond": bond_amount, "tx_hash": tx_hash.hex()}
        else:
            return False, None
        
    except web3.exceptions.ContractLogicError:
        return False, None
    except Exception:
        return False, None

def check_for_new_data(interval_seconds, api_key, processed_hashes):
    """Check for new data from the Graph API."""
    try:
        response_data = query_the_graph(QUERY_CONTRACT_ADDRESS, api_key)
        questions = extract_question_data(response_data)
        
        new_found = False
        for question in questions:
            ipfs_hash = question['data']
            question_id = question['questionId']
            bond = question['bond']
            
            if ipfs_hash not in processed_hashes:
                content = fetch_ipfs_content(ipfs_hash)
                result = evaluate_ipfs_hash(ipfs_hash)
                
                if not result:
                    challenge_submitted, challenge_data = submit_challenge(question_id, bond, TRANSACTION_CONTRACT_ADDRESS)
                    if challenge_submitted:
                        print(f'Challenge successful: Question ID="{question_id}", Bond={challenge_data["bond"]}.')
                else:
                    print(f'Evaluation passed: Question ID="{question_id}" meets specifications. No challenge needed.')
                
                processed_hashes.append(ipfs_hash)
                if len(processed_hashes) > MAX_HASHES:
                    processed_hashes.pop(0)
                
                new_found = True
        
        if not new_found:
            print(f"No new challenges found this round. Checking again in {interval_seconds} seconds.")
        
        # save_processed_hashes(processed_hashes)
        
        return processed_hashes, new_found
        
    except Exception as e:
        print(f"Error checking for new data: {e}")
        return processed_hashes, False

def main():
    """Main function to periodically check for new data."""
    interval_seconds = 60
    
    if len(sys.argv) > 1:
        try:
            interval_seconds = int(sys.argv[1])
        except ValueError:
            pass
    
    api_key = "be5ddfca879e5ea553aa90060c35999a"
    processed_hashes = load_processed_hashes()
    
    try:
        while True:
            processed_hashes, _ = check_for_new_data(
                interval_seconds, api_key, processed_hashes
            )
            
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        # save_processed_hashes(processed_hashes)
        pass

if __name__ == "__main__":
    main() 