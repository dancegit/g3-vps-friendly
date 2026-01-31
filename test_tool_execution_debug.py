#!/usr/bin/env python3
"""
Debug tool execution by capturing everything and checking for signs of execution.
"""

import subprocess
import time
import re

def test_tool_execution_comprehensive():
    """Comprehensive test to see exactly what happens during tool execution."""
    
    print("🔍 Comprehensive tool execution debug")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Run the command and capture everything
        process = subprocess.Popen([
            '/home/clauderun/.local/bin/g3',
            '--config', 'test_localhost_config.toml',
            '--new-session',
            '--quiet',
            'execute "echo TEST_TOOL_EXECUTION"'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Let it run for a bit to see the full execution
        time.sleep(12)  # Wait longer to see complete execution
        
        # Terminate and get output
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"⏱️  Total execution time: {execution_time:.1f}s")
        print(f"Return code: {process.returncode}")
        
        # Analyze stdout for signs of execution
        print("\n=== STDOUT ANALYSIS ===")
        stdout_lines = stdout.split('\n')
        
        # Look for specific patterns
        patterns_found = {
            'tool_call_detected': False,
            'shell_command': False,
            'command_output': False,
            'timing_info': False,
            'final_output': False,
            'error_indicators': False
        }
        
        for i, line in enumerate(stdout_lines):
            print(f"{i+1:2d}: {line}")
            
            # Check for tool call patterns
            if 'TOOL_CALL' in line or 'tool_call' in line.lower():
                patterns_found['tool_call_detected'] = True
            if 'shell' in line and 'command' in line:
                patterns_found['shell_command'] = True
            if 'TEST_TOOL_EXECUTION' in line:
                patterns_found['command_output'] = True
            if '⚡️' in line and 'ms' in line:
                patterns_found['timing_info'] = True
            if 'final_output' in line:
                patterns_found['final_output'] = True
            if 'error' in line.lower() or 'failed' in line.lower():
                patterns_found['error_indicators'] = True
        
        print("\n=== PATTERN ANALYSIS ===")
        for pattern, found in patterns_found.items():
            status = "✅" if found else "❌"
            print(f"{status} {pattern.replace('_', ' ').title()}")
        
        # Analyze stderr
        print("\n=== STDERR ANALYSIS ===")
        stderr_lines = stderr.split('\n')
        for i, line in enumerate(stderr_lines):
            if line.strip():  # Only show non-empty lines
                print(f"{i+1:2d}: {line}")
        
        # Check for specific error patterns in stderr
        error_patterns = ['ERROR', 'WARN', 'Failed', 'Error', 'Exception']
        for pattern in error_patterns:
            matches = [line for line in stderr_lines if pattern in line]
            if matches:
                print(f"\n⚠️  Found {pattern} in stderr:")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"  {match}")
        
        # Overall assessment
        print("\n=== OVERALL ASSESSMENT ===")
        
        if patterns_found['command_output']:
            print("🎉 SUCCESS: Tool execution appears to be working!")
            print("   The command output was detected, which means the shell tool executed.")
        elif patterns_found['tool_call_detected'] and patterns_found['timing_info']:
            print("🤔 PARTIAL SUCCESS: Tool call was detected and timing info present")
            print("   But no command output - this suggests execution happened but output wasn't captured")
        elif patterns_found['tool_call_detected']:
            print("❌ TOOL CALL ONLY: Tool call was detected but no execution evidence")
            print("   This suggests the tool call is being printed but not executed")
        else:
            print("❌ NO TOOL ACTIVITY: No tool calls or execution detected")
        
        # Check if it's the display vs execution issue
        if patterns_found['tool_call_detected'] and not patterns_found['command_output']:
            print("\n🚨 LIKELY ISSUE: Tool calls are being DISPLAYED but not EXECUTED")
            print("   The UI shows [TOOL_CALL] but the actual dispatch mechanism isn't working")
        
        return patterns_found['command_output'] or (patterns_found['tool_call_detected'] and patterns_found['timing_info'])
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_tool_execution_comprehensive()
    
    if success:
        print("\n✅ Tool execution is working (or appears to be working)")
    else:
        print("\n❌ Tool execution is definitely broken")
        print("The issue is that tool calls are displayed but not executed")