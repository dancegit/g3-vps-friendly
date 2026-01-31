#!/usr/bin/env python3
"""
Debug script to find the correct API endpoints for each provider.
"""

import requests
import json

def test_endpoints(provider_name, base_url, auth_token, model, endpoints_to_test):
    """Test multiple endpoint variations to find the correct one."""
    print(f"\n=== Testing {provider_name} ===")
    print(f"Base URL: {base_url}")
    
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {auth_token}",
        "anthropic-version": "2023-06-01"
    }
    
    test_payload = {
        "model": model,
        "max_tokens": 10,
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    
    for endpoint in endpoints_to_test:
        url = f"{base_url.rstrip('/')}{endpoint}"
        print(f"\nTesting: {url}")
        
        try:
            response = requests.post(url, headers=headers, json=test_payload, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS! Found working endpoint: {url}")
                return url
            elif response.status_code == 401:
                print(f"  ⚠️  Auth error (might be correct endpoint): {response.text[:100]}")
            elif response.status_code == 404:
                print(f"  ❌ Not found")
            elif response.status_code == 405:
                print(f"  ⚠️  Method not allowed (might be correct base): {response.text[:100]}")
            else:
                print(f"  ❌ Other error: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout")
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection error")
        except Exception as e:
            print(f"  💥 Error: {e}")
    
    return None

def main():
    # Test configurations from providers.json
    providers = [
        {
            "name": "MiniMax",
            "base_url": "https://api.minimax.io/v1",
            "auth_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJwZXIgc3VuZGJlcmciLCJVc2VyTmFtZSI6InBlciBzdW5kYmVyZyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTUxOTM5MjI0NTkyNzE2MTU3IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTk1MTkzOTIyNDU4ODUyMTg1MyIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InBlci5tYXJ0aW4uc3VuZGJlcmdAZ21haWwuY29tIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTEtMTIgMTI6MDk6MzYiLCJUb2tlblR5cGUiOjQsImlzcyI6Im1pbmltYXgifQ.EzTj3ItbOoAdiOyqV85UA3eH_lx1-NlQyHEI_BSvzi0umVxJbfLpwhAtXNpWxifZ5rjw_VYKxHb09z53k-MIzLzts6ODdC6FPw-eDp-B2V5sSArHHxz1DJf_EDKWNqYPea3ydUVpn3wHaOBQeVqqN-0-6CxU1IZ9O4HYnsAriiDzGbH6SkpYJFMr2PSPUHMy3t7THOEr_qMzpkX5dE-loh4SWeNRn72jJoaIMHAMFsE59B7q2iX7LZvmBeQpV7pzk-5QKGJIQrjrYZyAdCWC-f2Jrs6DjtjN4TfT2ZvLX_9vxgUntGNCnxFCdZ3wseIQiKcsv3NqrOt4rKg4-Nh1Hw",
            "model": "minimax-m2",
            "endpoints": ["/messages", "/chat/completions", "/v1/messages", "/v1/chat/completions", ""]
        },
        {
            "name": "Kimi",
            "base_url": "https://api.kimi.com/coding/",
            "auth_token": "sk-kimi-cWDcxzAMBNUdM9T99OjCVNAInNvJmfYkyUbFx6wA9L5HhkN2ajha7RT7sSYlHmIZ",
            "model": "kimi-for-coding",
            "endpoints": ["messages", "v1/messages", "chat/completions", "v1/chat/completions", ""]
        }
    ]
    
    print("Debugging API endpoints for providers...")
    print("=" * 60)
    
    working_endpoints = {}
    
    for provider in providers:
        endpoint = test_endpoints(
            provider["name"],
            provider["base_url"],
            provider["auth_token"],
            provider["model"],
            provider["endpoints"]
        )
        if endpoint:
            working_endpoints[provider["name"]] = endpoint
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    
    for name, endpoint in working_endpoints.items():
        print(f"✅ {name}: {endpoint}")
    
    if working_endpoints:
        print("\n🎉 Found working endpoints!")
    else:
        print("\n❌ No working endpoints found. Check authentication tokens.")

if __name__ == "__main__":
    main()