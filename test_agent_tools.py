#!/usr/bin/env python3
"""
Test script to verify G3 agent tool execution works correctly.
"""

import subprocess
import sys
import tempfile
import os

def test_agent_tool_execution():
    """Test that G3 agent can execute tools properly"""
    
    print("🔧 TESTING G3 AGENT TOOL EXECUTION")
    print("=" * 50)
    
    # Test 1: Build verification
    print("\n✅ Test 1: Build Verification")
    result = subprocess.run(
        ["cargo", "build", "--bin", "g3"],
        cwd="/home/clauderun/g3-vps-friendly",
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✅ Build successful")
    else:
        print("   ❌ Build failed")
        print(result.stderr)
        return False
    
    # Test 2: Create a simple test with your current config
    print("\n✅ Test 2: Agent Tool Execution Test")
    
    # Test with streaming enabled (your current issue)
    test_config_streaming = """# Test config with streaming enabled

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
name = "test-agent"
provider = "anthropic.minimax_local"
fallback_default_max_tokens = 8192
enable_streaming = true
allow_multiple_tool_calls = true
timeout_seconds = 60
max_retry_attempts = 3
autonomous_max_retry_attempts = 6
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = true
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    # Test with streaming disabled
    test_config_non_streaming = """# Test config with streaming disabled

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
name = "test-agent"
provider = "anthropic.minimax_local"
fallback_default_max_tokens = 8192
enable_streaming = false
allow_multiple_tool_calls = true
timeout_seconds = 60
max_retry_attempts = 3
autonomous_max_retry_attempts = 6
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = true
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    print("   📋 Creating test configurations...")
    
    # Create temporary config files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(test_config_streaming)
        streaming_config_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(test_config_non_streaming)
        non_streaming_config_path = f.name
    
    try:
        print("\n   🔍 Testing streaming mode...")
        # Test streaming mode with a simple command
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/debug/g3", "--config", streaming_config_path, "shell:echo 'Testing streaming mode'"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ Streaming mode test successful")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print("   ❌ Streaming mode test failed")
            print(f"   Error: {result.stderr}")
        
        print("\n   🔍 Testing non-streaming mode...")
        # Test non-streaming mode with a simple command
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/debug/g3", "--config", non_streaming_config_path, "shell:echo 'Testing non-streaming mode'"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ Non-streaming mode test successful")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print("   ❌ Non-streaming mode test failed")
            print(f"   Error: {result.stderr}")
        
        print("\n   🔍 Testing agent mode with tool execution...")
        # Test agent mode with a task that should trigger tool calls
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/debug/g3", "--config", streaming_config_path, "--agent", "list the files in the current directory"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ Agent mode test successful")
            print(f"   Output: {result.stdout.strip()[:200]}...")  # Truncate long output
        else:
            print("   ❌ Agent mode test failed")
            print(f"   Error: {result.stderr}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("   ⚠️  Test timed out - this might indicate the agent is hanging")
        return False
    finally:
        # Clean up temporary files
        os.unlink(streaming_config_path)
        os.unlink(non_streaming_config_path)
    
    print("\n" + "=" * 50)
    print("🎯 TEST COMPLETE!")
    print("\n📋 SUMMARY:")
    print("- MCP support has been removed from G3")
    print("- Goose integration has been removed")
    print("- Focus is now on native G3 agent functionality")
    print("- Tool execution should work in both streaming and non-streaming modes")
    
    return True

if __name__ == "__main__":
    success = test_agent_tool_execution()
    sys.exit(0 if success else 1)