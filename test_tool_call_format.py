#!/usr/bin/env python3
"""
Test to capture the exact format of tool calls and see what's being parsed.
"""

import subprocess
import time
import json

def test_tool_call_format():
    """Test to see what format tool calls are actually in."""
    
    print("🔍 Testing tool call format and parsing")
    print("=" * 50)
    
    # Test with debug logging to see the raw content
    env = os.environ.copy()
    env['RUST_LOG'] = 'g3_core::streaming_parser=debug,g3_core=debug'
    
    try:
        result = subprocess.run([
            '/home/clauderun/.local/bin/g3',
            '--config', 'test_localhost_config.toml',
            '--new-session',
            '--quiet',
            'execute "echo TEST_FORMAT"'
        ], capture_output=True, text=True, timeout=15, env=env)
        
        print(f"Return code: {result.returncode}")
        
        # Separate stdout and stderr
        stdout = result.stdout
        stderr = result.stderr
        
        print("\n=== STDOUT (What user sees) ===")
        stdout_lines = stdout.split('\n')
        for i, line in enumerate(stdout_lines):
            print(f"{i+1:2d}: {line}")
        
        print("\n=== STDERR (Debug logs) ===")
        stderr_lines = stderr.split('\n')
        debug_lines = [line for line in stderr_lines if any(keyword in line for keyword in 
                      ['tool_call', 'JSON', 'chunk', 'content', 'Received', 'Found', 'parsing'])]
        
        for i, line in enumerate(debug_lines[:20]):  # Show first 20 relevant debug lines
            print(f"{i+1:2d}: {line}")
        
        # Look for specific patterns in the output format
        print("\n=== TOOL CALL FORMAT ANALYSIS ===")
        
        # Check what format the tool call is in
        if '<invoke name="shell">' in stdout:
            print("🚨 Found XML-like tool call format in stdout")
            print("   This suggests the tool call is being DISPLAYED but not PARSED")
        
        if '{tool => "shell"' in stdout or '{"tool":' in stdout:
            print("✅ Found JSON tool call format in stdout")
            print("   This suggests JSON parsing might be working")
        
        # Check for parsing debug messages
        json_parsed = any('JSON tool calls' in line for line in stderr_lines)
        native_received = any('Received native tool calls' in line for line in stderr_lines)
        
        print(f"\nJSON tool calls parsed: {'✅' if json_parsed else '❌'}")
        print(f"Native tool calls received: {'✅' if native_received else '❌'}")
        
        # Check if we got actual command output
        command_output = 'TEST_FORMAT' in stdout
        print(f"\nActual command output: {'✅' if command_output else '❌'}")
        
        # Key insight: If we see XML format but no JSON parsing debug, 
        # then the tool call is being displayed but not executed
        xml_format_found = '<invoke name="shell">' in stdout
        json_parsing_found = json_parsed
        
        if xml_format_found and not json_parsing_found:
            print("\n🚨 LIKELY ISSUE: Tool calls are in XML format but not being parsed to JSON")
            print("   The model outputs XML-like tool calls, but the parser expects JSON")
        elif json_parsing_found and command_output:
            print("\n✅ Tool calls are being parsed and executed correctly")
        elif json_parsing_found and not command_output:
            print("\n⚠️ Tool calls are parsed but execution may have issues")
        else:
            print("\n❓ Unclear what's happening - need more investigation")
        
        return xml_format_found and not json_parsing_found
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import os
    issue_found = test_tool_call_format()
    
    if issue_found:
        print("\n🚨 FOUND THE ISSUE: XML tool calls not being parsed to JSON")
        print("The model outputs XML format but the parser expects JSON format")
    else:
        print("\n✅ Tool call format appears to be working correctly")