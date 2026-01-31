#!/usr/bin/env python3
"""
Test to verify if prompt length affects tool execution with localhost:9000
"""

import subprocess
import time

def test_prompt(prompt_text, test_name):
    """Test a specific prompt and check if tool execution works."""
    print(f"\n🧪 {test_name}")
    print(f"Prompt length: {len(prompt_text)} characters")
    print(f"Prompt: {prompt_text[:100]}..." if len(prompt_text) > 100 else f"Prompt: {prompt_text}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            '/home/clauderun/.local/bin/g3',
            '--config', 'test_localhost_config.toml',
            '--new-session',
            '--quiet',
            prompt_text
        ], capture_output=True, text=True, timeout=15)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"⏱️  Execution time: {execution_time:.1f}s")
        print(f"Return code: {result.returncode}")
        
        # Check for tool execution
        tool_executed = 'shell' in result.stdout or 'find' in result.stdout or 'read' in result.stdout
        empty_response = 'content=""' in result.stderr or 'No content or tool calls' in result.stderr
        
        if tool_executed:
            print("✅ TOOL EXECUTION DETECTED")
        elif empty_response:
            print("❌ EMPTY RESPONSE FROM MODEL")
        else:
            print("⚠️  NO TOOL EXECUTION DETECTED")
            
        if 'thinking' in result.stdout.lower():
            print("🤔 Thinking mode detected")
            
        return tool_executed and not empty_response
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT - Likely stuck in thinking mode")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🔍 Testing prompt length vs tool execution with localhost:9000")
    print("=" * 60)
    
    test_cases = [
        ("list files", "Very Short Prompt"),
        ("Please list all files in the current directory", "Short Prompt"),
        ("I need you to explore the current directory and list all files and folders to understand the project structure", "Medium Prompt"),
        ("Please help me understand this project by exploring the directory structure. I need you to list all files and directories in the current folder, then check if there are any configuration files like .env or docker-compose.yml, and finally provide a summary of what you found", "Long Prompt"),
        ("im trying to deploy correctly the vibe-kanban-expert-manager on the dokploy using the dokploy mcp and so on , the agents know about those tools and can use the mcp servers to try to configure the project on dokploy correctly setting up the correct subdomains that points to the correct docker image in the local dokploy, the login credentials are defined in .env and we tried to run playwright mcp web tests and so on for the users stories but we have some websocket errors after logging in, can you fix that?", "Very Long Prompt (User's Original)")
    ]
    
    results = []
    
    for prompt, test_name in test_cases:
        success = test_prompt(prompt, test_name)
        results.append((test_name, len(prompt), success))
        time.sleep(2)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY RESULTS")
    print("=" * 60)
    
    for test_name, length, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name:25} | {length:4d} chars")
    
    # Count results
    successful = sum(1 for _, _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {successful}/{total} tests passed")
    
    if successful < total:
        print("\n🚨 CONCLUSION: Prompt length IS affecting tool execution!")
        print("The localhost:9000 load balancer has issues with long/complex prompts")
        print("This explains why the user's Dokploy scenario fails while simple commands work")
    else:
        print("\n✅ All tests passed - prompt length is not the issue")

if __name__ == "__main__":
    main()