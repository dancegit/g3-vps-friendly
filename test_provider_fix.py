#!/usr/bin/env python3
"""
Test script to verify the corrected provider configuration.
This will test the authentication and endpoints for each provider.
"""

import requests
import json
import sys

def test_provider(name, base_url, auth_token, model, is_bearer=True):
    """Test a provider configuration by making a simple API call."""
    print(f"\n=== Testing {name} ===")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"Auth Type: {'Bearer' if is_bearer else 'API Key'}")
    
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    if is_bearer:
        headers["Authorization"] = f"Bearer {auth_token}"
    else:
        headers["x-api-key"] = auth_token
    
    # Test the messages endpoint
    test_url = f"{base_url.rstrip('/')}/messages"
    print(f"Testing endpoint: {test_url}")
    
    test_payload = {
        "model": model,
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello, this is a test."}
        ]
    }
    
    try:
        response = requests.post(test_url, headers=headers, json=test_payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Provider is working correctly!")
            return True
        elif response.status_code == 401:
            print("❌ AUTH ERROR: Invalid authentication token/key")
            print(f"Response: {response.text}")
            return False
        elif response.status_code == 404:
            print("❌ ENDPOINT ERROR: URL or endpoint not found")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    """Test all providers from the corrected configuration."""
    
    # Test configurations from providers.json
    providers = [
        {
            "name": "MiniMax Gmail (Subscription)",
            "base_url": "https://api.minimax.io/v1",
            "auth_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJwZXIgc3VuZGJlcmciLCJVc2VyTmFtZSI6InBlciBzdW5kYmVyZyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTUxOTM5MjI0NTkyNzE2MTU3IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTk1MTkzOTIyNDU4ODUyMTg1MyIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InBlci5tYXJ0aW4uc3VuZGJlcmdAZ21haWwuY29tIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTEtMTIgMTI6MDk6MzYiLCJUb2tlblR5cGUiOjQsImlzcyI6Im1pbmltYXgifQ.EzTj3ItbOoAdiOyqV85UA3eH_lx1-NlQyHEI_BSvzi0umVxJbfLpwhAtXNpWxifZ5rjw_VYKxHb09z53k-MIzLzts6ODdC6FPw-eDp-B2V5sSArHHxz1DJf_EDKWNqYPea3ydUVpn3wHaOBQeVqqN-0-6CxU1IZ9O4HYnsAriiDzGbH6SkpYJFMr2PSPUHMy3t7THOEr_qMzpkX5dE-loh4SWeNRn72jJoaIMHAMFsE59B7q2iX7LZvmBeQpV7pzk-5QKGJIQrjrYZyAdCWC-f2Jrs6DjtjN4TfT2ZvLX_9vxgUntGNCnxFCdZ3wseIQiKcsv3NqrOt4rKg4-Nh1Hw",
            "model": "minimax-m2",
            "is_bearer": True
        },
        {
            "name": "MiniMax GitHub (Subscription)",
            "base_url": "https://api.minimax.io/v1",
            "auth_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJQZXIgTWFydGluIFN1bmRiZXJnIiwiVXNlck5hbWUiOiJwZXJzb25hbCBhcHAgZGV2IiwiQWNjb3VudCI6IiIsIlN1YmplY3RJRCI6IjE5ODk3NDI3NzkwNDI4OTQ1NTMiLCJQaG9uZSI6IiIsIkdyb3VwSUQiOiIxOTg5NzQyNzc5MDM0NTEwMDQxIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoid2ViaW52ZW50aW9uc0Bwcm90b25tYWlsLmNvbSIsIkNyZWF0ZVRpbWUiOiIyMDI1LTExLTE2IDAyOjA0OjI4IiwiVG9rZW5UeXBlIjo0LCJpc3MiOiJtaW5pbWF4In0.J_Aeico2d8AFhDHpLXqkJrStbZsu-dmQvtpBqzbmOmBVqKPttSNRB0Nk4mUlcnJCZL6oIeeVpcynf1Gby_NjpJ2AlbZ-DJ_LhcfFpCkBNzJEpSaYBGex7mhklTUn_XOFKPAh5fkJ9Gu6yTxgbbaOUCeXE9mVBNnTUkntAJK-U3JjLpIeWZC7G3IRBgk4FqTjrM_AIUnSjVFZwYQRlD8LxNYF8AAcaMl7jQ6P0UOaI2T5w-e-nBUTSrRPRhDTMygfB0JFJsmzjpApr5912Cp3M7nfU2vtQ08c3N7wxcX5bdX2RhCYAfOkbU6eqxympu5W7XO45YZQ4kJ6EJW2UItFPA",
            "model": "minimax-m2",
            "is_bearer": True
        },
        {
            "name": "Kimi Thinking (API Key)",
            "base_url": "https://api.kimi.com/coding/",
            "auth_token": "sk-kimi-cWDcxzAMBNUdM9T99OjCVNAInNvJmfYkyUbFx6wA9L5HhkN2ajha7RT7sSYlHmIZ",
            "model": "kimi-for-coding",
            "is_bearer": True
        }
    ]
    
    print("Testing provider configurations based on providers.json...")
    print("=" * 60)
    
    results = []
    for provider in providers:
        result = test_provider(
            provider["name"],
            provider["base_url"],
            provider["auth_token"],
            provider["model"],
            provider["is_bearer"]
        )
        results.append((provider["name"], result))
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    success_count = 0
    for name, success in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{name}: {status}")
        if success:
            success_count += 1
    
    print(f"\nOverall: {success_count}/{len(results)} providers working")
    
    if success_count == len(results):
        print("🎉 All providers configured correctly!")
        return 0
    else:
        print("⚠️  Some providers have issues. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())