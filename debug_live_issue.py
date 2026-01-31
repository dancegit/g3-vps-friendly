#!/usr/bin/env python3
"""
Debug script to investigate why tool execution isn't working with the actual binary.
"""

import subprocess
import time
import json
import os
import signal

def debug_tool_execution():
    """Debug tool execution with the actual binary."""
    
    print("🔍 Debugging tool execution with ~/.local/bin/g3")
    print("Testing simple command that should definitely execute a tool...")
    
    # Test with a simple command that should execute quickly
    start_time = time.time()
    
    try:
        # Use a simple command that should trigger tool execution
        process = subprocess.Popen([
            '/home/clauderun/.local/bin/g3',
            '--config', 'test_localhost_config.toml',
            '--new-session',
            '--quiet',
            'execute "echo DEBUG_TEST"'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Let it run for a short time to see what happens
        time.sleep(8)  # Wait 8 seconds to see initial output
        
        # Check what's been output so far
        stdout_lines = []
        stderr_lines = []
        
        try:
            # Try to read some output
            stdout, stderr = process.communicate(timeout=1)
            stdout_lines = stdout.split('\n')
            stderr_lines = stderr.split('\n')
        except subprocess.TimeoutExpired:
            # Process is still running, get what we can
            process.kill()
            stdout, stderr = process.communicate()
            stdout_lines = stdout.split('\n')
            stderr_lines = stderr.split('\n')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"⏱️  Execution time: {execution_time:.1f}s")
        print(f"Process return code: {process.returncode}")
        
        print("\n=== STDOUT ===")
        for i, line in enumerate(stdout_lines):
            print(f"{i+1:2d}: {line}")
        
        print("\n=== STDERR ===")
        for i, line in enumerate(stderr_lines):
            print(f"{i+1:2d}: {line}")
        
        # Analyze what happened
        print("\n=== ANALYSIS ===")
        
        # Check if tool execution was attempted
        tool_execution_detected = False
        for line in stdout_lines:
            if 'shell' in line and 'command' in line:
                tool_execution_detected = True
                break
            if 'TOOL_CALL' in line or 'tool_call' in line:
                tool_execution_detected = True
                break
            if 'invoke' in line.lower():
                tool_execution_detected = True
                break
        
        if tool_execution_detected:
            print("✅ Tool call detected in output")
        else:
            print("❌ No tool call detected in output")
        
        # Check if it's stuck in thinking
        thinking_detected = False
        for line in stdout_lines:
            if 'thinking' in line.lower():
                thinking_detected = True
                break
        
        if thinking_detected:
            print("⚠️  Thinking mode detected")
        else:
            print("✅ No excessive thinking detected")
        
        # Check for actual command output
        command_output = False
        for line in stdout_lines:
            if 'DEBUG_TEST' in line:
                command_output = True
                break
        
        if command_output:
            print("✅ Command output detected - tool execution worked!")
        else:
            print("❌ No command output detected - tool execution may have failed")
        
        return tool_execution_detected and command_output
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def check_current_session():
    """Check if there's a current session running."""
    print("\n📋 Checking current session status...")
    
    try:
        # Check for current session
        if os.path.exists('.g3/sessions/current_context_window.txt'):
            with open('.g3/sessions/current_context_window.txt', 'r') as f:
                current_session = f.read().strip()
            print(f"Current session: {current_session}")
            
            # Try to read the session file
            session_file = f".g3/sessions/{current_session}"
            if os.path.exists(session_file):
                print(f"Session file exists: {session_file}")
                # Check if it's being updated
                stat_info = os.stat(session_file)
                print(f"Last modified: {time.ctime(stat_info.st_mtime)}")
            else:
                print("Session file not found")
        else:
            print("No current session found")
            
    except Exception as e:
        print(f"Error checking session: {e}")

if __name__ == "__main__":
    print("🔍 Live debugging of G3 tool execution issue")
    print("=" * 50)
    
    success = debug_tool_execution()
    check_current_session()
    
    if success:
        print("\n🎉 Tool execution appears to be working!")
    else:
        print("\n❌ Tool execution is not working as expected")
        print("The issue needs further investigation")