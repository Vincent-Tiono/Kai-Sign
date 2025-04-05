import json
import re
import requests
import sys
from google import genai

# Initialize the Gemini client with your API key
client = genai.Client(api_key="AIzaSyAxI-7_Pcu1xN_NCCyieQokljbH7NEmy5M")

def fetch_ipfs_content(ipfs_hash):
    """Fetch content from IPFS given a hash."""
    url = f"https://ipfs.io/ipfs/{ipfs_hash}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from IPFS: {e}")
        sys.exit(1)

def validate_ethereum_address(address):
    """Validate if a string is a proper Ethereum address."""
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

def evaluate_erc7730_spec(spec_json):
    """Evaluate an ERC7730 JSON specification."""
    # Define the prompt with example and user's spec
    prompt = f"""
    Evaluate the following ERC7730 JSON specification based on these criteria:
    1. It must include a properly formatted Ethereum address (42-character string starting with '0x' followed by 40 hex characters).
    2. Each function or type listed in the 'display.formats' section must have a clear, human-readable 'intent' describing its purpose.

    Here is an example of a good ERC7730 spec for reference:
    {{
      "$schema": "../../specs/erc7730-v1.schema.json",
      "context": {{
        "eip712": {{
          "deployments": [{{"chainId": 137, "address": "0xdb46d1dc155634fbc732f92e853b10b288ad5a1d"}}],
          "domain": {{"name": "Dispatch", "chainId": 137, "verifyingContract": "0xdb46d1dc155634fbc732f92e853b10b288ad5a1d"}},
          "schemas": [
            {{
              "primaryType": "FollowWithSig",
              "types": {{
                "EIP712Domain": [
                  {{"name": "chainId", "type": "uint256"}},
                  {{"name": "name", "type": "string"}},
                  {{"name": "verifyingContract", "type": "address"}},
                  {{"name": "version", "type": "string"}}
                ],
                "FollowWithSig": [
                  {{"name": "datas", "type": "bytes[]"}},
                  {{"name": "deadline", "type": "uint256"}},
                  {{"name": "nonce", "type": "uint256"}},
                  {{"name": "profileIds", "type": "uint256[]"}}
                ]
              }}
            }}
          ]
        }}
      }},
      "metadata": {{"owner": "Dispatch.xyz"}},
      "display": {{
        "formats": {{
          "FollowWithSig": {{
            "intent": "Dispatch.xyz Follow Profile",
            "fields": [
              {{"path": "profileIds.[]", "label": "Profile Ids", "format": "raw"}},
              {{"path": "datas.[]", "label": "Data", "format": "raw"}},
              {{"path": "nonce", "label": "Nonce", "format": "raw"}},
              {{"path": "deadline", "label": "Expiration Date", "format": "raw"}}
            ]
          }}
        }}
      }}
    }}

    Now, evaluate this spec:
    {spec_json}

    Return your evaluation in this exact JSON format: {{"Good": XX%, "Bad": XX%}}, where XX% is your confidence level. Do not include any additional text or explanations.
    """

    # Send the request to Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        result_text = response.text.strip()
        
        # Try multiple approaches to extract valid JSON
        try:
            # First attempt: Direct JSON parsing if response is already JSON
            result_dict = json.loads(result_text)
        except json.JSONDecodeError:
            # Second attempt: Use regex to find JSON-like pattern
            json_match = re.search(r'(\{.*"Good".*"Bad".*\})', result_text, re.DOTALL)
            if json_match:
                try:
                    result_json = json_match.group(1)
                    result_dict = json.loads(result_json)
                except json.JSONDecodeError:
                    # If still failing, create a dictionary from the text
                    good_match = re.search(r'"Good":\s*"?(\d+)%"?', result_text)
                    bad_match = re.search(r'"Bad":\s*"?(\d+)%"?', result_text)
                    
                    if good_match and bad_match:
                        result_dict = {
                            "Good": f"{good_match.group(1)}%",
                            "Bad": f"{bad_match.group(1)}%"
                        }
                    else:
                        result_dict = {"Good": "0%", "Bad": "100%"}
            else:
                result_dict = {"Good": "0%", "Bad": "100%"}
        
        return result_dict
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return {"Good": "0%", "Bad": "100%"}

def main():
    # Check if IPFS hash is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python hash_prob.py <ipfs_hash>")
        sys.exit(1)
    
    ipfs_hash = sys.argv[1]
    
    # Fetch the ERC7730 JSON spec from IPFS
    spec_json = fetch_ipfs_content(ipfs_hash)
    
    # Try to parse the content as JSON
    try:
        # Validate JSON format
        json.loads(spec_json)
    except json.JSONDecodeError:
        print("Invalid JSON format in the IPFS content. Please check the hash and try again.")
        sys.exit(1)
    
    # Evaluate the spec
    result = evaluate_erc7730_spec(spec_json)
    
    # Print the result
    print(result)

if __name__ == "__main__":
    main() 