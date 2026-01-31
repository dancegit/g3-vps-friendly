#!/usr/bin/env python3
"""
Test interactive mode vs command-line mode to see the difference.
"""

import subprocess
import time
import select
import sys
import os

def test_interactive_mode():
    """Test interactive mode by simulating user input."""
    
    print("🔍 Testing INTERACTIVE MODE")
    print("=" * 40)
    
    try:
        # Start G3 in interactive mode
        process = subprocess.Popen([
            '/home/clauderun/.local/bin/g3',
            '--config', 'test_localhost_config.toml',
            '--new-session'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for it to start up
        time.sleep(3)
        
        # Send a simple command
        print("Sending: list files")
        process.stdin.write("list files\n")
        process.stdin.flush()
        
        # Wait for response
        time.sleep(8)
        
        # Read output
        try:
            # Try to get output without blocking
            stdout_lines = []
            stderr_lines = []
            
            # Read what we can
            import fcntl
            fcntl.fcntl(process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
            fcntl.fcntl(process.stderr.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
            
            try:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    stdout_lines.append(line.strip())
            except:
                pass
                
            try:
                while True:
                    line = process.stderr.readline()
                    if not line:
                        break
                    stderr_lines.append(line.strip())
            except:
                pass
            
        except Exception as e:
            print(f"Error reading output: {e}")
            stdout_lines = []
            stderr_lines = []
        
        # Terminate the process
        process.terminate()
        process.wait(timeout=5)
        
        print("\n=== INTERACTIVE MODE OUTPUT ===")
        print("STDOUT:")
        for i, line in enumerate(stdout_lines):
            print(f"{i+1:2d}: {line}")
        
        print("\nSTDERR:")
        for i, line in enumerate(stderr_lines):
            if line.strip():
                print(f"{i+1:2d}: {line}")
        
        # Analyze the output
        tool_call_detected = any('TOOL_CALL' in line or 'tool_call' in line.lower() for line in stdout_lines)
        command_output = any('ls -la' in line for line in stdout_lines)
        thinking_detected = any('thinking' in line.lower() for line in stdout_lines)
        
        print(f"\n=== ANALYSIS ===")
        print(f"Tool call detected: {tool_call_detected}")
        print(f"Command output detected: {command_output}")
        print(f"Thinking detected: {thinking_detected}")
        
        return command_output  # The key indicator
        
    except Exception as e:
        print(f"❌ Error in interactive test: {e}")
        return False

def test_command_line_mode():
    """Test command-line mode for comparison."""
    
    print("\n🔍 Testing COMMAND-LINE MODE")
    print("=" * 40)
    
    try:
        result = subprocess.run([
            '/home/clauderun/.local/bin/g3',
            '--config', 'test_localhost_config.toml',
            '--new-session',
            '--quiet',
            'list files'
        ], capture_output=True, text=True, timeout=15)
        
        print(f"Return code: {result.returncode}")
        
        stdout_lines = result.stdout.split('\n')
        stderr_lines = result.stderr.split('\n')
        
        print("\n=== COMMAND-LINE MODE OUTPUT ===")
        print("STDOUT:")
        for i, line in enumerate(stdout_lines):
            if line.strip():
                print(f"{i+1:2d}: {line}")
        
        print("\nSTDERR:")
        for i, line in enumerate(stderr_lines):
            if line.strip():
                print(f"{i+1:2d}: {line}")
        
        # Analyze the output
        tool_call_detected = any('TOOL_CALL' in line or 'tool_call' in line.lower() for line in stdout_lines)
        command_output = any('ls -la' in line for line in stdout_lines)
        thinking_detected = any('thinking' in line.lower() for line in stdout_lines)
        
        print(f"\n=== ANALYSIS ===")
        print(f"Tool call detected: {tool_call_detected}")
        print(f"Command output detected: {command_output}")
        print(f"Thinking detected: {thinking_detected}")
        
        return command_output  # The key indicator
        
    except Exception as e:
        print(f"❌ Error in command-line test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Comparing Interactive vs Command-line modes")
    print("=" * 50)
    
    interactive_result = test_interactive_mode()
    command_line_result = test_command_line_mode()
    
    print("\n" + "=" * 50)
    print("📊 COMPARISON RESULTS")
    print("=" * 50)
    print(f"Interactive mode: {'✅ WORKING' if interactive_result else '❌ BROKEN'}")
    print(f"Command-line mode: {'✅ WORKING' if command_line_result else '❌ BROKEN'}")
    
    if interactive_result and not command_line_result:
        print("\n🚨 ISSUE: Interactive mode works but command-line doesn't")
    elif not interactive_result and command_line_result:
        print("\n🚨 ISSUE: Command-line mode works but interactive doesn't")
    elif not interactive_result and not command_line_result:
        print("\n❌ BOTH MODES BROKEN")
    else:
        print("\n✅ BOTH MODES WORKING")