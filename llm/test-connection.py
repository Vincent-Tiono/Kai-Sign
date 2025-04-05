import os
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables from the current directory
load_dotenv()

# Get RPC URL from environment
ETH_RPC_URL = os.getenv('SEPOLIA_RPC_URL')
print(f"RPC URL: {ETH_RPC_URL}")

# Create Web3 connection
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# Print connection status
print(f"Connected to Ethereum: {w3.is_connected()}")

if w3.is_connected():
    print(f"Current block number: {w3.eth.block_number}")
else:
    print("Failed to connect. Trying with requests transport...")
    
    # Try with requests transport
    from web3.providers.rpc import HTTPProvider
    
    w3 = Web3(HTTPProvider(ETH_RPC_URL))
    
    print(f"Connected with requests transport: {w3.is_connected()}")
    if w3.is_connected():
        print(f"Current block number: {w3.eth.block_number}")
    else:
        print("Still failed to connect. Trying with explicit HTTP headers...")
        
        # Try with explicit headers
        custom_http_provider = HTTPProvider(
            ETH_RPC_URL,
            request_kwargs={
                'headers': {
                    'Content-Type': 'application/json',
                    'User-Agent': 'python-web3/6.0.0'
                }
            }
        )
        
        w3 = Web3(custom_http_provider)
        print(f"Connected with custom headers: {w3.is_connected()}")
        if w3.is_connected():
            print(f"Current block number: {w3.eth.block_number}")
        else:
            print("Connection failed with all methods.")
            print("Check the following:")
            print("1. Is your Infura API key valid?")
            print("2. Is there a network issue?")
            print("3. Is the RPC endpoint correct?")
            print("\nTrying a different public endpoint:")
            
            # Try an alternative RPC endpoint
            ALT_RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/demo"
            print(f"Alternative RPC URL: {ALT_RPC_URL}")
            w3 = Web3(Web3.HTTPProvider(ALT_RPC_URL))
            print(f"Connected to alternative endpoint: {w3.is_connected()}")
            if w3.is_connected():
                print(f"Current block number: {w3.eth.block_number}") 