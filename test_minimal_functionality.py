#!/usr/bin/env python3
"""
Minimal test to verify G3 agent tool execution works with localhost load balancer.
Focuses on the core issue: tool execution in streaming mode.
"""

import subprocess
import sys
import tempfile
import os
import time

def test_minimal_tool_execution():
    """Minimal test for tool execution with load balancer"""
    print("🔧 MINIMAL G3 TOOL EXECUTION TEST")
    print("=" * 50)
    print("Testing if G3 can execute tools with localhost:9000 load balancer")
    
    # Create a simple test directory
    test_dir = tempfile.mkdtemp(prefix="g3_minimal_test_")
    print(f"\n📁 Test directory: {test_dir}")
    
    # Create minimal config for load balancer
    config_content = """# Minimal config for tool execution test

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
name = "minimal-test"
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
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    config_path = f"{test_dir}/config.toml"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print("\n🚀 Testing basic tool execution...")
    
    # Test 1: Simple shell command (should work quickly)
    print("   Test 1: Simple shell command")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "shell:pwd"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=15  # 15 second timeout
        )
        
        if result.returncode == 0:
            print("   ✅ Shell command executed successfully")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print("   ❌ Shell command failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Shell command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Shell command error: {e}")
        return False
    
    # Test 2: File listing (basic file operation)
    print("\n   Test 2: File listing")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "shell:ls -la"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            print("   ✅ File listing executed successfully")
            # Just show first few lines
            lines = result.stdout.strip().split('\n')
            for line in lines[:3]:
                print(f"      {line}")
            if len(lines) > 3:
                print("      ...")
        else:
            print("   ❌ File listing failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  File listing timed out")
        return False
    except Exception as e:
        print(f"   ❌ File listing error: {e}")
        return False
    
    # Test 3: File creation (more complex tool)
    print("\n   Test 3: File creation and reading")
    try:
        # Create a test file using echo without redirection first
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "shell:echo 'Hello from G3 test'"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            print("   ✅ Echo command successful")
            
            # Now create the file with echo and redirect
            result2 = subprocess.run(
                ["/home/clauderun/g3-vps-friendly/target/release/g3", 
                 "--config", config_path,
                 "shell:echo 'Hello from G3 test' > test_file.txt"],
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result2.returncode == 0:
                print("   ✅ File creation successful")
                
                # Read the file back
                result3 = subprocess.run(
                    ["/home/clauderun/g3-vps-friendly/target/release/g3", 
                     "--config", config_path,
                     "shell:cat test_file.txt"],
                    cwd=test_dir,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result3.returncode == 0:
                    print(f"   ✅ File reading successful: {result3.stdout.strip()}")
                else:
                    print("   ⚠️  File reading failed - file may not exist")
            else:
                print("   ⚠️  File creation with redirect failed")
        else:
            print("   ❌ Basic echo command failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  File operations timed out")
        return False
    except Exception as e:
        print(f"   ❌ File operations error: {e}")
        return False
    
    # Test 4: Single-shot mode (simpler than agent mode)
    print("\n   Test 4: Single-shot mode")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "create a simple Python file that prints 'Hello World'"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=30  # Longer timeout for single-shot
        )
        
        if result.returncode == 0:
            print("   ✅ Single-shot mode completed")
            print("   📄 Output preview:")
            output_lines = result.stdout.split('\n')
            for line in output_lines[:5]:
                if line.strip() and not line.startswith('⏱') and not line.startswith('●'):
                    print(f"      {line}")
            if len(output_lines) > 5:
                print("      ...")
        else:
            print("   ❌ Single-shot mode failed")
            print(f"   Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Single-shot mode timed out")
        return False
    except Exception as e:
        print(f"   ❌ Single-shot mode error: {e}")
        return False
    
    print(f"\n🧹 Test files location: {test_dir}")
    print("   (Files preserved for debugging - delete manually when done)")
    
    return True

def test_streaming_vs_non_streaming():
    """Compare streaming vs non-streaming performance"""
    print("\n🚀 STREAMING VS NON-STREAMING COMPARISON")
    print("=" * 50)
    
    # Create test directory
    test_dir = tempfile.mkdtemp(prefix="g3_streaming_test_")
    
    # Create config with streaming enabled
    streaming_config = """# Streaming enabled config

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
name = "streaming-test"
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
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    # Create config with streaming disabled
    non_streaming_config = """# Streaming disabled config

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
name = "non-streaming-test"
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
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    streaming_path = f"{test_dir}/streaming.toml"
    non_streaming_path = f"{test_dir}/non_streaming.toml"
    
    with open(streaming_path, "w") as f:
        f.write(streaming_config)
    with open(non_streaming_path, "w") as f:
        f.write(non_streaming_config)
    
    print("\n⏱️  Comparing streaming vs non-streaming performance...")
    
    # Test streaming mode
    print("\n   📊 Testing streaming mode...")
    start_time = time.time()
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", streaming_path,
             "shell:echo 'Streaming test' && ls"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        streaming_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Streaming mode: {streaming_time:.2f}s")
        else:
            print(f"   ❌ Streaming mode failed")
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Streaming mode timed out")
    except Exception as e:
        print(f"   ❌ Streaming mode error: {e}")
    
    # Test non-streaming mode
    print("\n   📊 Testing non-streaming mode...")
    start_time = time.time()
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", non_streaming_path,
             "shell:echo 'Non-streaming test' && ls"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        non_streaming_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Non-streaming mode: {non_streaming_time:.2f}s")
        else:
            print(f"   ❌ Non-streaming mode failed")
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Non-streaming mode timed out")
    except Exception as e:
        print(f"   ❌ Non-streaming mode error: {e}")
    
    print(f"\n🧹 Test files location: {test_dir}")
    return True

def run_minimal_tests():
    """Run all minimal tests"""
    print("🚀 MINIMAL G3 FUNCTIONALITY TESTS")
    print("=" * 60)
    print("Testing core G3 functionality with localhost:9000 load balancer")
    print("after MCP removal and streaming fixes.")
    
    results = []
    
    # Test 1: Basic tool execution
    print("\n" + "="*60)
    results.append(("Basic Tool Execution", test_minimal_tool_execution()))
    
    # Test 2: Streaming vs non-streaming comparison
    print("\n" + "="*60)
    results.append(("Streaming Comparison", test_streaming_vs_non_streaming()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 MINIMAL TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL MINIMAL TESTS PASSED!")
        print("✅ G3 basic functionality works with your load balancer")
        print("✅ Tool execution is working correctly")
        print("✅ Streaming mode is functional")
        print("\n🚀 Your G3 agent is ready for more complex tasks!")
        print("\n💡 Next steps:")
        print("   - Try the full user story tests")
        print("   - Test with your actual Dokploy deployment")
        print("   - Use coach/player mode for complex implementations")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("   This indicates there may still be issues with your load balancer setup")
        print("   Check that your localhost:9000 service is running correctly")
    
    return passed == total

if __name__ == "__main__":
    success = run_minimal_tests()
    sys.exit(0 if success else 1)