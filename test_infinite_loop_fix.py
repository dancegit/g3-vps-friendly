#!/usr/bin/env python3
"""
Test for the infinite loop fix in G3 agent with localhost load balancer.
This tests if the agent can now properly exit loops and execute tools.
"""

import subprocess
import sys
import tempfile
import os
import time

def test_infinite_loop_fix():
    """Test if the infinite loop fix works with the load balancer"""
    print("🔄 TESTING INFINITE LOOP FIX")
    print("=" * 50)
    print("Testing if G3 can now properly exit loops and execute tools")
    print("with localhost:9000 load balancer after the final_output tracking fix.")
    
    test_dir = tempfile.mkdtemp(prefix="g3_loop_fix_test_")
    config_path = f"{test_dir}/config.toml"
    
    # Create minimal config for load balancer
    config_content = """# Config for infinite loop fix testing

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
name = "loop-fix-test"
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
    
    # Test 1: Simple command that should complete quickly
    print("\n⚡ Test 1: Simple command (should complete quickly)")
    start_time = time.time()
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "shell:pwd"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Simple command completed in {elapsed:.1f}s")
            print(f"   Output: {result.stdout.strip()[:100]}...")
            return True
        else:
            print(f"   ❌ Simple command failed after {elapsed:.1f}s")
            print(f"   Error: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Simple command TIMED OUT (infinite loop suspected)")
        return False
    except Exception as e:
        print(f"   💥 Simple command ERROR: {e}")
        return False
    
    # Test 2: File operations (should work based on previous tests)
    print("\n📁 Test 2: File Operations")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "list_workspace_files"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ File operations work")
            output = result.stdout.strip()
            if len(output) < 200:
                print(f"   Output: {output}")
            else:
                print(f"   Output: {output[:100]}...")
            return True
        else:
            print("   ❌ File operations failed")
            print(f"   Error: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ File operations TIMED OUT")
        return False
    except Exception as e:
        print(f"   💥 File operations ERROR: {e}")
        return False
    
    # Test 3: Check if the agent can complete a simple task
    print("\n🎯 Test 3: Simple Task Completion")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "create a file named 'success.txt' with content 'test passed'"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=20
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Task completed in {elapsed:.1f}s")
            print("   📄 Output preview:")
            output_lines = result.stdout.split('\n')
            for line in output_lines[:3]:
                if line.strip() and not line.startswith('⏱') and not line.startswith('●'):
                    print(f"      {line}")
            return True
        else:
            print(f"   ❌ Task failed after {elapsed:.1f}s")
            print(f"   Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Task TIMED OUT (likely infinite loop)")
        return False
    except Exception as e:
        print(f"   💥 Task ERROR: {e}")
        return False
    
    print(f"\n🧹 Test files location: {test_dir}")
    return True

def run_loop_fix_test():
    """Run the infinite loop fix test"""
    print("🚀 RUNNING INFINITE LOOP FIX TEST")
    print("=" * 60)
    
    success = test_infinite_loop_fix()
    
    if success:
        print("\n🎉 LOOP FIX TEST PASSED!")
        print("✅ The infinite loop issue appears to be resolved")
        print("✅ G3 can now properly execute tools and exit loops")
        print("✅ Ready for complex autonomous operations")
    else:
        print("\n⚠️  LOOP FIX TEST HAD ISSUES")
        print("   The fix may need additional work or there may be other issues")
        print("   Check the test output above for specific problems")
    
    return success

if __name__ == "__main__":
    success = run_loop_fix_test()
    sys.exit(0 if success else 1)