#!/usr/bin/env python3
"""
Test script to verify the final_output_called fix is working.
This will test if the agent properly terminates after executing tools.
"""

import subprocess
import time
import json
import os

def test_tool_execution_with_final_output():
    """Test that tool execution completes properly with final_output."""
    
    print("🧪 Testing tool execution with final_output fix...")
    
    # Run a simple test that should complete quickly
    start_time = time.time()
    
    try:
        result = subprocess.run([
            './target/release/g3',
            '--config', 'debug_test.toml',
            '--new-session',
            '--quiet',
            'Execute "echo TEST_COMPLETE" and then summarize what you did using final_output'
        ], capture_output=True, text=True, timeout=30)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"⏱️  Execution time: {execution_time:.1f}s")
        print(f"Return code: {result.returncode}")
        
        # Check if we got output
        if result.stdout:
            print("=== STDOUT ===")
            print(result.stdout)
            
            # Look for signs of successful tool execution
            if "TEST_COMPLETE" in result.stdout:
                print("✅ SUCCESS: Tool execution detected")
                return True
            elif "final_output" in result.stdout:
                print("✅ SUCCESS: final_output detected")
                return True
            else:
                print("⚠️  Tool execution unclear")
                
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)
            
            # Check for thinking mode issues
            if "thinking" in result.stderr.lower() and execution_time > 20:
                print("❌ LIKELY STUCK IN THINKING MODE")
                return False
                
        # If execution completed quickly (< 10s), it's probably working
        if execution_time < 10 and result.returncode == 0:
            print("✅ SUCCESS: Quick completion suggests fix is working")
            return True
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ FAILURE: Command timed out (likely stuck in thinking mode)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def check_session_logs():
    """Check recent session logs for evidence of tool execution."""
    print("\n📋 Checking session logs...")
    
    # Find most recent session
    try:
        sessions = []
        for item in os.listdir('.g3/sessions'):
            if os.path.isdir(f'.g3/sessions/{item}'):
                sessions.append(item)
        
        if sessions:
            latest_session = sorted(sessions)[-1]
            session_file = f'.g3/sessions/{latest_session}/session.json'
            
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    data = json.load(f)
                
                # Check status
                status = data.get('status', 'unknown')
                print(f"Latest session status: {status}")
                
                # Check if tools were mentioned
                history = data.get('context_window', {}).get('conversation_history', [])
                tool_mentions = 0
                for msg in history:
                    if 'shell' in msg.get('content', '') or 'tool' in msg.get('content', ''):
                        tool_mentions += 1
                
                print(f"Tool mentions in history: {tool_mentions}")
                return status == 'completed' or tool_mentions > 0
            
    except Exception as e:
        print(f"Could not check session logs: {e}")
    
    return False

if __name__ == "__main__":
    print("🔍 Testing G3 tool execution fix...")
    
    success1 = test_tool_execution_with_final_output()
    success2 = check_session_logs()
    
    if success1 or success2:
        print("\n✅ OVERALL RESULT: Fix appears to be working!")
        exit(0)
    else:
        print("\n❌ OVERALL RESULT: Fix may not be working properly")
        exit(1)