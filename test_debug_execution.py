#!/usr/bin/env python3
"""
Test to verify if tool execution debug logs are being generated.
This will show us exactly what path the code is taking.
"""

import subprocess
import time
import re

def test_execution_debug():
    """Test with debug logging to trace the execution path."""
    
    print("🔍 Testing tool execution with debug logging")
    print("=" * 50)
    
    # Test with comprehensive debug logging
    env = os.environ.copy()
    env['RUST_LOG'] = 'g3_core=debug,g3_core::tools=debug,g3_core::tool_dispatch=debug,g3_execution=debug'
    
    try:
        result = subprocess.run([
            '/home/clauderun/.local/bin/g3',
            '--config', 'test_localhost_config.toml',
            '--new-session',
            '--quiet',
            'execute "echo TEST_DEBUG_EXECUTION"'
        ], capture_output=True, text=True, timeout=15, env=env)
        
        print(f"Return code: {result.returncode}")
        print(f"Execution time: {len(result.stderr.split('\n'))} lines of debug output")
        
        # Look for specific execution markers
        debug_output = result.stderr
        
        # Key execution markers we're looking for
        markers = {
            'dispatch_tool': 'Tool dispatch function called',
            'execute_shell': 'Shell execution function called',
            'execute_bash_streaming': 'Bash streaming execution called',
            'EXECUTING TOOL': 'Tool execution started',
            'ABOUT TO CALL': 'About to call actual execution',
            'tool_result': 'Tool execution completed',
            'Command executed': 'Command success message',
            'Command failed': 'Command failure message',
            'TEST_DEBUG_EXECUTION': 'Our actual command output'
        }
        
        print("\n=== EXECUTION MARKERS FOUND ===")
        found_markers = {}
        
        for marker, description in markers.items():
            if marker in debug_output:
                found_markers[marker] = True
                print(f"✅ {description}")
                # Show context around the marker
                lines = debug_output.split('\n')
                for i, line in enumerate(lines):
                    if marker in line:
                        print(f"   Context: {line.strip()}")
                        # Show next few lines for context
                        for j in range(1, 3):
                            if i + j < len(lines):
                                print(f"   Next: {lines[i+j].strip()}")
                        break
            else:
                found_markers[marker] = False
                print(f"❌ {description}")
        
        # Check if we got actual command output
        command_output = 'TEST_DEBUG_EXECUTION' in result.stdout
        
        print(f"\n=== FINAL ASSESSMENT ===")
        print(f"Command output detected: {'✅' if command_output else '❌'}")
        
        # Key indicators
        execution_started = found_markers.get('EXECUTING TOOL', False)
        execution_called = found_markers.get('ABOUT TO CALL', False)
        dispatch_called = found_markers.get('dispatch_tool', False)
        
        if execution_started and execution_called and dispatch_called:
            print("✅ Tool execution path is being followed correctly")
            if command_output:
                print("✅ Tools are executing AND producing output")
            else:
                print("⚠️ Tools are executing but output may not be displayed")
        elif dispatch_called and not execution_started:
            print("❌ Tool dispatch is called but execution is not starting")
        elif not dispatch_called:
            print("❌ Tool dispatch is not being called at all")
        else:
            print("⚠️ Partial execution path - need to investigate further")
        
        # Show some key debug lines
        print(f"\n=== KEY DEBUG LINES ===")
        debug_lines = debug_output.split('\n')
        key_lines = [line for line in debug_lines if any(marker in line for marker in markers.keys())]
        for line in key_lines[:10]:  # Show first 10 relevant lines
            print(f"{line.strip()}")
        
        return execution_started and execution_called and dispatch_called and command_output
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import os
    success = test_execution_debug()
    
    if success:
        print("\n🎉 Tool execution appears to be working correctly!")
    else:
        print("\n❌ Tool execution has issues - need to investigate the execution path")