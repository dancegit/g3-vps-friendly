#!/usr/bin/env python3
"""
Test the final corrected configuration.
"""

import requests

def test_final_config():
    """Test the final configuration with correct endpoints."""
    
    providers = [
        {
            "name": "MiniMax Gmail",
            "url": "https://api.minimax.io/v1/chat/completions",
            "auth_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJwZXIgc3VuZGJlcmciLCJVc2VyTmFtZSI6InBlciBzdW5kYmVyZyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTUxOTM5MjI0NTkyNzE2MTU3IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTk1MTkzOTIyNDU4ODUyMTg1MyIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6InBlci5tYXJ0aW4uc3VuZGJlcmdAZ21haWwuY29tIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTEtMTIgMTI6MDk6MzYiLCJUb2tlblR5cGUiOjQsImlzcyI6Im1pbmltYXgifQ.EzTj3ItbOoAdiOyqV85UA3eH_lx1-NlQyHEI_BSvzi0umVxJbfLpwhAtXNpWxifZ5rjw_VYKxHb09z53k-MIzLzts6ODdC6FPw-eDp-B2V5sSArHHxz1DJf_EDKWNqYPea3ydUVpn3wHaOBQeVqqN-0-6CxU1IZ9O4HYnsAriiDzGbH6SkpYJFMr2PSPUHMy3t7THOEr_qMzpkX5dE-loh4SWeNRn72jJoaIMHAMFsE59B7q2iX7LZvmBeQpV7pzk-5QKGJIQrjrYZyAdCWC-f2Jrs6DjtjN4TfT2ZvLX_9vxgUntGNCnxFCdZ3wseIQiKcsv3NqrOt4rKg4-Nh1Hw",
            "model": "minimax-m2"
        },
        {
            "name": "MiniMax GitHub",
            "url": "https://api.minimax.io/v1/chat/completions",
            "auth_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJQZXIgTWFydGluIFN1bmRiZXJnIiwiVXNlck5hbWUiOiJwZXJzb25hbCBhcHAgZGV2IiwiQWNjb3VudCI6IiIsIlN1YmplY3RJRCI6IjE5ODk3NDI3NzkwNDI4OTQ1NTMiLCJQaG9uZSI6IiIsIkdyb3VwSUQiOiIxOTg5NzQyNzc5MDM0NTEwMDQxIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoid2ViaW52ZW50aW9uc0Bwcm90b25tYWlsLmNvbSIsIkNyZWF0ZVRpbWUiOiIyMDI1LTExLTE2IDAyOjA0OjI4IiwiVG9rZW5UeXBlIjo0LCJpc3MiOiJtaW5pbWF4In0.J_Aeico2d8AFhDHpLXqkJrStbZsu-dmQvtpBqzbmOmBVqKPttSNRB0Nk4mUlcnJCZL6oIeeVpcynf1Gby_NjpJ2AlbZ-DJ_LhcfFpCkBNzJEpSaYBGex7mhklTUn_XOFKPAh5fkJ9Gu6yTxgbbaOUCeXE9mVBNnTUkntAJK-U3JjLpIeWZC7G3IRBgk4FqTjrM_AIUnSjVFZwYQRlD8LxNYF8AAcaMl7jQ6P0UOaI2T5w-e-nBUTSrRPRhDTMygfB0JFJsmzjpApr5912Cp3M7nfU2vtQ08c3N7wxcX5bdX2RhCYAfOkbU6eqxympu5W7XO45YZQ4kJ6EJW2UItFPA",
            "model": "minimax-m2"
        },
        {
            "name": "Kimi Thinking",
            "url": "https://api.kimi.com/coding/v1/messages",
            "auth_token": "sk-kimi-cWDcxzAMBNUdM9T99OjCVNAInNvJmfYkyUbFx6wA9L5HhkN2ajha7RT7sSYlHmIZ",
            "model": "kimi-for-coding"
        }
    ]
    
    print("Testing final corrected configuration...")
    print("=" * 60)
    
    results = []
    
    for provider in providers:
        print(f"\n=== Testing {provider['name']} ===")
        
        headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {provider['auth_token']}",
            "anthropic-version": "2023-06-01"
        }
        
        test_payload = {
            "model": provider["model"],
            "max_tokens": 10,
            "messages": [
                {"role": "user", "content": "Hello, this is a test."}
            ]
        }
        
        try:
            response = requests.post(provider["url"], headers=headers, json=test_payload, timeout=15)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS: Provider is working!")
                results.append((provider["name"], True))
            elif response.status_code == 401:
                print(f"  ⚠️  Auth error: {response.text[:100]}")
                results.append((provider["name"], False))
            else:
                print(f"  ❌ Error: {response.text[:100]}")
                results.append((provider["name"], False))
                
        except Exception as e:
            print(f"  💥 Exception: {e}")
            results.append((provider["name"], False))
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    success_count = 0
    for name, success in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{name}: {status}")
        if success:
            success_count += 1
    
    print(f"\nOverall: {success_count}/{len(results)} providers working")
    
    if success_count == len(results):
        print("🎉 All providers are now configured correctly!")
        print("\nThe issue was incorrect base URLs. The corrected configuration uses:")
        print("- MiniMax: https://api.minimax.io/v1/chat/completions")
        print("- Kimi: https://api.kimi.com/coding/v1/messages")
        return True
    else:
        print("⚠️  Some providers still have issues.")
        return False

if __name__ == "__main__":
    test_final_config()