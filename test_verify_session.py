"""
Test script for the verify-session endpoint

This script helps test the /auth/verify-session endpoint
"""

import requests

# Configuration
BASE_URL = "http://localhost:5000"  # Update this to your backend URL

def test_verify_session():
    """Test the verify-session endpoint"""
    
    print("=" * 60)
    print("Testing /auth/verify-session Endpoint")
    print("=" * 60)
    
    # Test 1: Without authentication
    print("\nTest 1: Request without authentication token")
    response = requests.get(f"{BASE_URL}/auth/verify-session")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Expected: 401 (Unauthorized)")
    
    # Test 2: With authentication (you need to sign in first)
    print("\n" + "=" * 60)
    print("Test 2: Request with authentication token")
    print("First, let's sign in...")
    
    # Sign in to get a token
    signin_data = {
        "email": "owner@example.com",  # Update with your test credentials
        "password": "password123"
    }
    
    print(f"\nAttempting to sign in with email: {signin_data['email']}")
    signin_response = requests.post(
        f"{BASE_URL}/auth/signin",
        json=signin_data
    )
    
    if signin_response.status_code == 200:
        print(f"Sign-in successful!")
        cookies = signin_response.cookies
        
        # Now test verify-session with the cookies
        print("\nTesting /auth/verify-session with authentication...")
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify-session",
            cookies=cookies
        )
        
        print(f"Status Code: {verify_response.status_code}")
        print(f"Response: {verify_response.json()}")
        print(f"Expected: 200 (OK) with user information")
        
        if verify_response.status_code == 200:
            data = verify_response.json()
            print("\n✓ Session verification successful!")
            print(f"  Account ID: {data.get('account_id')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Role: {data.get('role')}")
            print(f"  Is Verified: {data.get('is_verified')}")
    else:
        print(f"Sign-in failed!")
        print(f"Status Code: {signin_response.status_code}")
        print(f"Response: {signin_response.json()}")
        print("\nPlease update the credentials in this script and try again.")
    
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_verify_session()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the backend server.")
        print(f"   Please ensure the backend is running at {BASE_URL}")
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
