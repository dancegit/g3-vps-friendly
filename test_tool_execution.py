#!/usr/bin/env python3
"""
Test script to verify G3 tool execution is working properly.
This will test if the agent can execute a simple tool call instead of getting stuck in "thinking" mode.
"""

import subprocess
import sys
import time
import os

def test_simple_tool_execution():
    """Test if G3 can execute a simple shell command."""
    
    # Use localhost test config
    config_file = 'test_localhost_config.toml'
    if not os.path.exists(config_file):
        print(f"❌ Config file {config_file} not found")
        return False
    
    # Test command that should execute a simple tool
    test_command = [
        './target/release/g3',
        '--config', config_file,
        '--new-session',
        '--quiet',
        'execute "ls -la"'
    ]
    
    print("Testing G3 tool execution...")
    print(f"Running command: {' '.join(test_command)}")
    
    try:
        # Run with timeout to prevent hanging
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        # Check if we got actual tool execution output
        if "shell" in result.stdout or "command" in result.stdout:
            print("✅ SUCCESS: Tool execution detected!")
            return True
        elif "thinking" in result.stdout.lower() or "think" in result.stdout.lower():
            print("❌ FAILURE: Still stuck in thinking mode")
            return False
        else:
            print("⚠️  UNCLEAR: Unexpected output format")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ FAILURE: Command timed out (likely stuck in thinking mode)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_tool_execution()
    sys.exit(0 if success else 1)