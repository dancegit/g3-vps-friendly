#!/usr/bin/env python3
"""
Comprehensive test to verify G3 tool execution is working reliably.
"""

import subprocess
import sys
import os

def test_multiple_scenarios():
    """Test multiple scenarios to ensure tool execution is reliable."""
    
    config_file = 'test_localhost_config.toml'
    
    tests = [
        {
            'name': 'Simple shell command',
            'command': 'ls -la',
            'expected_tool': 'shell'
        },
        {
            'name': 'File listing',
            'command': 'find . -name "*.toml" | head -5',
            'expected_tool': 'shell'
        },
        {
            'name': 'Directory info',
            'command': 'pwd && echo "Current directory contents:" && ls',
            'expected_tool': 'shell'
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n🧪 Testing: {test['name']}")
        print(f"Command: {test['command']}")
        
        test_command = [
            './target/release/g3',
            '--config', config_file,
            '--new-session',
            '--quiet',
            f'execute "{test["command"]}"'
        ]
        
        try:
            result = subprocess.run(
                test_command,
                capture_output=True,
                text=True,
                timeout=45  # 45 second timeout
            )
            
            print(f"Return code: {result.returncode}")
            
            if result.stdout:
                # Check if tool execution happened
                if test['expected_tool'] in result.stdout:
                    print(f"✅ SUCCESS: {test['expected_tool']} tool executed")
                    passed += 1
                elif "think" in result.stdout.lower():
                    print(f"❌ FAILURE: Still stuck in thinking mode")
                else:
                    print(f"⚠️  UNCLEAR: Unexpected output")
                    print(f"Stdout snippet: {result.stdout[:200]}...")
            else:
                print(f"❌ FAILURE: No output captured")
                
            if result.stderr:
                print(f"Stderr: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ FAILURE: Command timed out")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    success = test_multiple_scenarios()
    sys.exit(0 if success else 1)