#!/usr/bin/env python3
"""
Quick tool functionality test for G3 with localhost load balancer.
Focuses on core tool execution to verify the fixes work.
"""

import subprocess
import sys
import tempfile
import os

def test_quick_tools():
    """Quick test of core G3 tools"""
    print("⚡ QUICK G3 TOOLS TEST")
    print("=" * 40)
    print("Testing core tool functionality with localhost:9000")
    
    test_dir = tempfile.mkdtemp(prefix="g3_quick_test_")
    config_path = f"{test_dir}/config.toml"
    
    # Quick config for load balancer
    config_content = """# Quick config for tool testing

[providers]
default_provider = "anthropic.minimax_local"

[providers.anthropic.minimax_local]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.3
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[agent]
name = "quick-test"
provider = "anthropic.minimax_local"
fallback_default_max_tokens = 8192
enable_streaming = true
allow_multiple_tool_calls = true
timeout_seconds = 30
max_retry_attempts = 2
autonomous_max_retry_attempts = 3
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print(f"\n📁 Test directory: {test_dir}")
    
    # Quick tests with shorter timeouts
    tests = [
        {
            "name": "Shell: pwd",
            "command": "shell:pwd",
            "timeout": 5
        },
        {
            "name": "Shell: echo test",
            "command": "shell:echo 'test'",
            "timeout": 5
        },
        {
            "name": "File: list files",
            "command": "list_workspace_files",
            "timeout": 5
        },
        {
            "name": "File: read config",
            "command": f"read_file {config_path}",
            "timeout": 5
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n⚡ Testing: {test['name']}")
        try:
            result = subprocess.run(
                ["/home/clauderun/g3-vps-friendly/target/release/g3", 
                 "--config", config_path,
                 test['command']],
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=test['timeout']
            )
            
            if result.returncode == 0:
                print(f"   ✅ {test['name']}: SUCCESS")
                # Show a bit of output
                output = result.stdout.strip()
                if output and len(output) < 200:
                    print(f"      Output: {output}")
                elif output:
                    print(f"      Output: {output[:100]}...")
                results.append(True)
            else:
                print(f"   ❌ {test['name']}: FAILED")
                print(f"      Error: {result.stderr[:100]}")
                results.append(False)
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {test['name']}: TIMEOUT")
            results.append(False)
        except Exception as e:
            print(f"   💥 {test['name']}: ERROR - {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Quick Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 QUICK TESTS PASSED!")
        print("✅ Core G3 tools work with your load balancer")
        print("✅ Tool execution is functional")
        print("✅ Ready for more complex testing")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("   Check if your localhost:9000 service is running")
    
    print(f"\n🧹 Test files: {test_dir}")
    return passed == total

if __name__ == "__main__":
    success = test_quick_tools()
    sys.exit(0 if success else 1)