#!/usr/bin/env python3
"""
Debug Kimi endpoint specifically.
"""

import requests

def test_kimi_endpoints():
    auth_token = "sk-kimi-cWDcxzAMBNUdM9T99OjCVNAInNvJmfYkyUbFx6wA9L5HhkN2ajha7RT7sSYlHmIZ"
    model = "kimi-for-coding"
    
    # Different base URLs to try
    base_urls = [
        "https://api.kimi.com/coding/",
        "https://api.kimi.com/coding",
        "https://api.kimi.com/v1/",
        "https://api.kimi.com/"
    ]
    
    endpoints = ["/messages", "/chat/completions", "/v1/messages", "/v1/chat/completions"]
    
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
    
    for base_url in base_urls:
        print(f"\n=== Testing base URL: {base_url} ===")
        
        for endpoint in endpoints:
            url = f"{base_url.rstrip('/')}{endpoint}"
            print(f"  Testing: {url}")
            
            try:
                response = requests.post(url, headers=headers, json=test_payload, timeout=10)
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    ✅ SUCCESS!")
                    return url
                elif response.status_code == 401:
                    print(f"    ⚠️  Auth error: {response.text[:100]}")
                    if "invalid" in response.text.lower() or "unauthorized" in response.text.lower():
                        print(f"    🔑 Invalid token")
                    else:
                        print(f"    🚪 Might be correct endpoint, wrong auth")
                elif response.status_code == 404:
                    print(f"    ❌ Not found")
                elif response.status_code == 405:
                    print(f"    ⚠️  Method not allowed: {response.text[:100]}")
                else:
                    print(f"    ❌ Other: {response.text[:100]}")
                    
            except requests.exceptions.Timeout:
                print(f"    ⏰ Timeout")
            except requests.exceptions.ConnectionError:
                print(f"    🔌 Connection error")
            except Exception as e:
                print(f"    💥 Error: {e}")
    
    return None

if __name__ == "__main__":
    print("Debugging Kimi endpoint...")
    result = test_kimi_endpoints()
    if result:
        print(f"\n🎉 Found working Kimi endpoint: {result}")
    else:
        print(f"\n❌ No working Kimi endpoint found")