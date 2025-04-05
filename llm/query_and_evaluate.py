import json
import requests
import subprocess
import sys

# Global variable to store the final result
result = False

def load_deployment_config():
    """Load the deployment configuration to get the kaisignContract address."""
    with open('../deployment.json', 'r') as f:
        config = json.load(f)
    return config


def query_the_graph(contract_address, api_key):
    """Query The Graph API for questions related to the contract address."""
    url = "https://gateway.thegraph.com/api/73380b22a17017c081123ec9c0e34677/subgraphs/id/F3XjWNiNFUTbZhNQjXuhP7oDug2NaPwMPZ5XCRx46h5U"
    
    # The GraphQL query
    query = {
        "query": f"""
        {{
          questions(where: {{user: "{contract_address}"}}) {{
            questionId,
            data
          }}
        }}
        """,
        "variables": {}
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=query, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Bad")
        sys.exit(1)

def extract_ipfs_hashes(response_data):
    """Extract IPFS hashes from the query response."""
    ipfs_hashes = []
    
    if response_data and 'data' in response_data and response_data['data'] and 'questions' in response_data['data']:
        for question in response_data['data']['questions']:
            if 'data' in question:
                ipfs_hashes.append(question['data'])
    
    return ipfs_hashes

def fetch_ipfs_content(ipfs_hash):
    """Fetch content from IPFS given a hash."""
    url = f"https://ipfs.io/ipfs/{ipfs_hash}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Bad")
        sys.exit(1)

def evaluate_ipfs_hash(ipfs_hash):
    """Run hash_prob.py to evaluate the given IPFS hash and return True for Good, False for Bad."""
    try:
        result = subprocess.run(
            ["python", "hash_prob.py", ipfs_hash],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        
        # Parse the output to determine if Good or Bad has higher probability
        if "Good" in output and "Bad" in output:
            # Extract probabilities (assuming format like "Good: 0.8, Bad: 0.2")
            parts = output.split(',')
            good_prob = float(parts[0].split(':')[1].strip())
            bad_prob = float(parts[1].split(':')[1].strip())
            
            is_good = good_prob > bad_prob
            result_text = "Good" if is_good else "Bad"
            print(result_text)
            return is_good
        else:
            print("Bad")
            return False
            
    except subprocess.CalledProcessError as e:
        print("Bad")
        return False

def main():
    global result
    # Load configuration
    config = load_deployment_config()
    contract_address = config.get('kaisignContract')
    
    if not contract_address:
        print("Bad")
        sys.exit(1)
    
    # Use the provided API key
    api_key = "be5ddfca879e5ea553aa90060c35999a"
    
    # Query The Graph API
    response_data = query_the_graph(contract_address, api_key)
    
    # Extract IPFS hashes
    ipfs_hashes = extract_ipfs_hashes(response_data)
    
    if not ipfs_hashes:
        print("Bad")
        result = False
        return result
    
    # Process first IPFS hash
    ipfs_hash = ipfs_hashes[0]
    
    # Fetch content from IPFS (needed for evaluation)
    content = fetch_ipfs_content(ipfs_hash)
    
    # Evaluate the IPFS hash
    result = evaluate_ipfs_hash(ipfs_hash)
    return result

if __name__ == "__main__":
    main()
    # Print result value for debugging
    print(f"Final result value: {result}") 