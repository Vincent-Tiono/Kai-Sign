import json
import requests
import subprocess
import sys
import os
from main import evaluate_specification  # Import the evaluation function

# Global variable to store the final result
result = False

# def load_deployment_config():
#     """Load the deployment configuration to get the kaisignContract address."""
#     with open('../deployment.json', 'r') as f:
#         config = json.load(f)
#     return config


def query_the_graph(contract_address, api_key):
    """Query The Graph API for questions related to the contract address."""
    url = "https://gateway.thegraph.com/api/73380b22a17017c081123ec9c0e34677/subgraphs/id/F3XjWNiNFUTbZhNQjXuhP7oDug2NaPwMPZ5XCRx46h5U"
    
    # The GraphQL query
    query = {
        "query": f"""
        {{
          questions(where: {{user: "{contract_address}"}}) {{
            questionId,
            data,
            lastBond
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

def extract_question_data(response_data):
    """Extract question data including questionId, data (IPFS hash), and bond."""
    questions = []
    
    # print(f"Extracting question data from response: {json.dumps(response_data, indent=2)}")
    
    if response_data and 'data' in response_data and response_data['data'] and 'questions' in response_data['data']:
        for question in response_data['data']['questions']:
            if 'questionId' in question and 'data' in question:
                questions.append({
                    'questionId': question['questionId'],
                    'data': question['data'],  # IPFS hash
                    'bond': question.get('lastBond', '0')  # Default to 0 if not present
                })
                # print(f"Found question: {question['questionId']} with data hash: {question['data']}")
    else:
        print("No questions found in response data or malformed response")
    
    return questions

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
    """Evaluate the given IPFS hash using the LLM and return True for Good, False for Bad."""
    try:
        # Print the hash that we're evaluating
        # print(f"Evaluating IPFS hash: {ipfs_hash}")
        
        # First fetch the content from IPFS
        content = fetch_ipfs_content(ipfs_hash)
        
        # No file operations - process everything in memory
        # Directly use the imported evaluation function
        result_dict = evaluate_specification(content)
        
        
        # print(f"Evaluation results: {result_dict}\n")
        
        # Parse the result to determine if Good or Bad has higher probability
        try:
            # Handle both string with % and integer values
            good_val = result_dict.get("Good", "0%")
            bad_val = result_dict.get("Bad", "0%")
            
            # Convert to numeric values
            if isinstance(good_val, str):
                good_prob = float(good_val.strip("%"))
            else:
                good_prob = float(good_val)
                
            if isinstance(bad_val, str):
                bad_prob = float(bad_val.strip("%"))
            else:
                bad_prob = float(bad_val)
            
            is_good = good_prob > bad_prob
            
            result_text = "Good" if is_good else "Bad"
            print(f"{result_text} - Good: {good_prob}%, Bad: {bad_prob}%")
            return is_good
        except (ValueError, AttributeError):
            # Default to Bad if parsing fails
            print("Bad - Unable to parse evaluation results")
            return False
            
    except Exception as e:
        print(f"Bad - Error during evaluation: {e}")
        return False

def main():
    global result
    # Load configuration
    # config = load_deployment_config()
    contract_address = "0x2d2f90786a365a2044324f6861697e9EF341F858"
    
    if not contract_address:
        print("Bad")
        sys.exit(1)
    
    # Use the provided API key
    api_key = "be5ddfca879e5ea553aa90060c35999a"
    
    # Query The Graph API
    response_data = query_the_graph(contract_address, api_key)
    
    # Extract question data
    questions = extract_question_data(response_data)
    
    if not questions:
        print("Bad")
        result = False
        return result
    
    # Process first question
    question = questions[5]
    ipfs_hash = question['data']
    
    # Evaluate the IPFS hash
    result = evaluate_ipfs_hash(ipfs_hash)
    
    # Return all the needed data
    return {
        'result': result,
        'questionId': question['questionId'],
        'data': ipfs_hash,
        'bond': question['bond']
    }

if __name__ == "__main__":
    main()
    # Print result value for debugging
    print(f"Final result value: {result}") 