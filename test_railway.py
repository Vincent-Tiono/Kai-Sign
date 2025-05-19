import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def test_api_health():
    """Test the API health endpoint"""
    try:
        # For local testing
        url = "http://localhost:8001"
        response = requests.get(f"{url}/")
        print(f"Health check response: {response.status_code}")
        print(response.json())
        assert response.status_code == 200
        assert response.json()["message"] == "API is running"
        return True
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

def test_erc7730_generation():
    """Test the ERC7730 generation endpoint using a sample contract address"""
    try:
        # For local testing
        url = "http://localhost:8001"
        
        # A sample verified contract address on Ethereum mainnet (DAI stablecoin)
        sample_contract = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
        
        # Make the API request
        response = requests.post(
            f"{url}/generateERC7730",
            json={"address": sample_contract}
        )
        
        print(f"ERC7730 generation response: {response.status_code}")
        
        if response.status_code == 200:
            print("ERC7730 descriptor generated successfully")
            return True
        else:
            print(f"Failed to generate ERC7730 descriptor: {response.json()}")
            return False
            
    except Exception as e:
        print(f"ERC7730 generation test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting API tests...")
    
    # Set ETHERSCAN_API_KEY from environment if needed
    if not os.getenv("ETHERSCAN_API_KEY"):
        print("Warning: ETHERSCAN_API_KEY not set in environment")
    
    # Run tests
    health_result = test_api_health()
    erc7730_result = test_erc7730_generation()
    
    print("\nTest Results:")
    print(f"Health Check: {'✅ PASSED' if health_result else '❌ FAILED'}")
    print(f"ERC7730 Generation: {'✅ PASSED' if erc7730_result else '❌ FAILED'}")
    
    if health_result and erc7730_result:
        print("\n🎉 All tests passed! The API is ready for deployment.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        exit(1) 