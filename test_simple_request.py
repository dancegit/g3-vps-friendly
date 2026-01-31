#!/usr/bin/env python3
"""
Test simple API request without tools to verify the endpoint and auth work.
"""

import requests
import json

def test_minimax_simple():
    """Test MiniMax with a simple request without tools."""
    
    url = "https://api.minimax.io/v1/chat/completions"
    auth_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJwZXIgc3VuZGJlcmciLCJVc2VyTmFtZSI6InBlciBzdW5kYmVyZyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTUxOTM5MjI0NTkyNzE2MTU3IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTk1MTkzOTIyNDU4ODUyMTg1MyIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InBlci5tYXJ0aW4uc3VuZGJlcmdAZ21haWwuY29tIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTEtMTIgMTI6MDk6MzYiLCJUb2tlblR5cGUiOjQsImlzcyI6Im1pbmltYXgifQ.EzTj3ItbOoAdiOyqV85UA3eH_lx1-NlQyHEI_BSvzi0umVxJbfLpwhAtXNpWxifZ5rjw_VYKxHb09z53k-MIzLzts6ODdC6FPw-eDp-B2V5sSArHHxz1DJf_EDKWNqYPea3ydUVpn3wHaOBQeVqqN-0-6CxU1IZ9O4HYnsAriiDzGbH6SkpYJFMr2PSPUHMy3t7THOEr_qMzpkX5dE-loh4SWeNRn72jJoaIMHAMFsE59B7q2iX7LZvmBeQpV7pzk-5QKGJIQrjrYZyAdCWC-f2Jrs6DjtjN4TfT2ZvLX_9vxgUntGNCnxFCdZ3wseIQiKcsv3NqrOt4rKg4-Nh1Hw"
    
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    
    # Test with OpenAI-compatible format (what MiniMax expects)
    payload = {
        "model": "minimax-m2",
        "messages": [
            {"role": "user", "content": "What is 2 + 2?"}
        ],
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    print("Testing MiniMax with OpenAI-compatible format...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                print(f"✅ SUCCESS: {content}")
                return True
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_minimax_anthropic_format():
    """Test MiniMax with Anthropic format to see the error."""
    
    url = "https://api.minimax.io/v1/messages"
    auth_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJwZXIgc3VuZGJlcmciLCJVc2VyTmFtZSI6InBlciBzdW5kYmVyZyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTUxOTM5MjI0NTkyNzE2MTU3IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTk1MTkzOTIyNDU4ODUyMTg1MyIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InBlci5tYXJ0aW4uc3VuZGJlcmdAZ21haWwuY29tIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTEtMTIgMTI6MDk6MzYiLCJUb2tlblR5cGUiOjQsImlzcyI6Im1pbmltYXgifQ.EzTj3ItbOoAdiOyqV85UA3eH_lx1-NlQyHEI_BSvzi0umVxJbfLpwhAtXNpWxifZ5rjw_VYKxHb09z53k-MIzLzts6ODdC6FPw-eDp-B2V5sSArHHxz1DJf_EDKWNqYPea3ydUVpn3wHaOBQeVqqN-0-6CxU1IZ9O4HYnsAriiDzGbH6SkpYJFMr2PSPUHMy3t7THOEr_qMzpkX5dE-loh4SWeNRn72jJoaIMHAMFsE59B7q2iX7LZvmBeQpV7pzk-5QKGJIQrjrYZyAdCWC-f2Jrs6DjtjN4TfT2ZvLX_9vxgUntGNCnxFCdZ3wseIQiKcsv3NqrOt4rKg4-Nh1Hw"
    
    headers = {
        "content-type": "application/json",
        "x-api-key": auth_token,
        "anthropic-version": "2023-06-01"
    }
    
    # Test with Anthropic format
    payload = {
        "model": "minimax-m2",
        "messages": [
            {"role": "user", "content": "What is 2 + 2?"}
        ],
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    print("\nTesting MiniMax with Anthropic format...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing MiniMax API formats...")
    
    # Test OpenAI format (what should work)
    success1 = test_minimax_simple()
    
    # Test Anthropic format (what g3 is trying to use)
    success2 = test_minimax_anthropic_format()
    
    print(f"\nResults:")
    print(f"OpenAI format: {'✅' if success1 else '❌'}")
    print(f"Anthropic format: {'✅' if success2 else '❌'}")
    
    if success1 and not success2:
        print("\n💡 Discovery: MiniMax supports OpenAI format but not Anthropic format!")
        print("This explains why g3 is failing - it's using the wrong API format.")
    elif success1:
        print("\n✅ MiniMax works with OpenAI format.")
    else:
        print("\n❌ Both formats failed.")