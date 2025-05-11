import requests
import json

def test_api_root():
    """Test the root API endpoint"""
    try:
        response = requests.get('http://localhost:8000/')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        assert response.status_code == 200
        print("✅ Root API test passed")
    except Exception as e:
        print(f"❌ Root API test failed: {str(e)}")

def test_api_erc7730_with_address():
    """Test the ERC7730 API endpoint with a contract address"""
    try:
        payload = {
            "address": "0x2d2f90786a365a2044324f6861697e9EF341F858",
            "chain_id": 11155111
        }
        response = requests.post(
            'http://localhost:8000/api/py/generateERC7730', 
            json=payload
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            # Print first part of response to avoid too much output
            response_json = response.json()
            print(f"Response preview: {json.dumps(response_json, indent=2)[:200]}...")
            print("✅ ERC7730 API test passed")
        else:
            print(f"Response: {response.text}")
            print("❌ ERC7730 API test failed")
    except Exception as e:
        print(f"❌ ERC7730 API test failed: {str(e)}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_api_root()
    test_api_erc7730_with_address()
    print("All tests completed.") 