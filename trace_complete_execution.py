#!/usr/bin/env python3
"""
Comprehensive execution flow tracing to understand how commands are actually being executed.
"""

import subprocess
import time
import json

def trace_execution_flow():
    """Trace the complete execution flow to understand the mystery."""
    
    print("🔍 Tracing Complete Execution Flow")
    print("=" * 60)
    
    # Test 1: Check if tool dispatch logs appear
    print("\n1. Testing Tool Dispatch Logs...")
    
    result = subprocess.run([
        '/home/clauderun/.local/bin/g3',
        '--config', 'test_localhost_config.toml',
        '--new-session',
        '--quiet',
        'execute "echo TRACE_TEST_1"'
    ], capture_output=True, text=True, timeout=15, 
    env={**subprocess.os.environ, 'RUST_LOG': 'g3_core=debug,g3_core::tools=debug,g3_core::tool_dispatch=debug'})
    
    has_tool_dispatch = "TOOL_DISPATCH" in result.stderr
    has_shell_tool = "SHELL_TOOL" in result.stderr
    has_agent = "AGENT" in result.stderr
    
    print(f"TOOL_DISPATCH logs found: {'✅' if has_tool_dispatch else '❌'}")
    print(f"SHELL_TOOL logs found: {'✅' if has_shell_tool else '❌'}")
    print(f"AGENT logs found: {'✅' if has_agent else '❌'}")
    
    # Test 2: Check if streaming parser finds tool calls
    print("\n2. Testing Streaming Parser Results...")
    
    has_json_found = "Found.*JSON tool calls" in result.stderr
    has_xml_found = "Found.*XML tool calls" in result.stderr
    has_any_found = "Found.*tool calls" in result.stderr
    
    print(f"JSON tool calls found: {'✅' if has_json_found else '❌'}")
    print(f"XML tool calls found: {'✅' if has_xml_found else '❌'}")
    print(f"ANY tool calls found: {'✅' if has_any_found else '❌'}")
    
    # Test 3: Check execution evidence
    print("\n3. Testing Execution Evidence...")
    
    command_output = "TRACE_TEST_1" in result.stdout
    timing_info = "⚡️" in result.stdout
    tool_formatting = "shell" in result.stdout and "command" in result.stdout
    
    print(f"Command output appears: {'✅' if command_output else '❌'}")
    print(f"Timing info appears: {'✅' if timing_info else '❌'}")
    print(f"Tool formatting appears: {'✅' if tool_formatting else '❌'}")
    
    # Test 4: Check the mystery - what execution path is actually being used?
    print("\n4. The Mystery Analysis...")
    
    if command_output and not has_tool_dispatch:
        print("🚨 MYSTERY CONFIRMED: Commands execute WITHOUT normal tool dispatch!")
        print("   - Commands produce output")
        print("   - Tool formatting appears in UI")
        print("   - But NO tool dispatch logs")
        print("   - This means there's a SEPARATE execution path")
    elif has_tool_dispatch and command_output:
        print("✅ NORMAL EXECUTION: Commands execute through tool dispatch")
        print("   - Both execution and dispatch logs present")
    else:
        print("❓ UNCLEAR: Inconsistent execution pattern")
    
    # Test 5: Look for alternative execution evidence
    print("\n5. Alternative Execution Evidence...")
    
    # Check for g3-execution related logs
    has_g3_execution = "g3_execution" in result.stderr or "execute_bash" in result.stderr
    has_direct_command = "Command::new" in result.stderr or "std::process::Command" in result.stderr
    has_tokio_command = "TokioCommand" in result.stderr
    
    print(f"g3-execution logs found: {'✅' if has_g3_execution else '❌'}")
    print(f"Direct Command logs found: {'✅' if has_direct_command else '❌'}")
    print(f"Tokio Command logs found: {'✅' if has_tokio_command else '❌'}")
    
    # Test 6: Check UI vs execution separation
    print("\n6. UI vs Execution Separation...")
    
    # The key insight: UI shows tool calls but execution happens elsewhere
    ui_shows_tools = "<invoke" in result.stdout or "TOOL_CALL" in result.stdout
    execution_happens = command_output
    
    if ui_shows_tools and execution_happens and not has_tool_dispatch:
        print("🎯 KEY INSIGHT: UI displays tool calls but execution bypasses dispatch!")
        print("   - This suggests the XML is displayed for user visibility")
        print("   - But actual execution happens through a separate mechanism")
        print("   - The displayed XML is NOT the same as the executed tool call")
    
    # Summary
    print("\n" + "="*60)
    print("EXECUTION FLOW ANALYSIS SUMMARY:")
    print("="*60)
    
    if command_output and not has_tool_dispatch and not has_any_found:
        print("🚨 CONFIRMED: Dual execution path issue!")
        print("   1. XML tool calls are DISPLAYED in UI")
        print("   2. Commands are EXECUTED through separate mechanism") 
        print("   3. Normal tool dispatch is COMPLETELY BYPASSED")
        print("   4. This creates inconsistent and confusing behavior")
        
        print("\n🎯 ROOT CAUSE IDENTIFIED:")
        print("   The localhost:9000 load balancer uses a SEPARATE execution mechanism")
        print("   that bypasses G3's normal tool dispatch system entirely.")
        print("   The XML format is displayed for user visibility but executed elsewhere.")
        
        print("\n🔧 SOLUTION REQUIRED:")
        print("   1. Ensure XML parsing captures ALL tool calls from stream")
        print("   2. Force all execution through the normal tool dispatch path")
        print("   3. Add comprehensive logging throughout the execution pipeline")
        print("   4. Standardize execution behavior across all providers")
    else:
        print("❓ Analysis inconclusive - need more investigation")

if __name__ == "__main__":
    trace_execution_flow()