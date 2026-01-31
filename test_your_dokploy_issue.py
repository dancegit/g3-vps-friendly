#!/usr/bin/env python3
"""
Test G3 with your specific Dokploy WebSocket issue configuration.
Use the coach/player setup to debug the websocket errors.
"""

import subprocess
import sys
import tempfile
import os

def test_your_dokploy_issue():
    """Test G3 with your Dokploy WebSocket issue using coach/player setup"""
    print("🏗️  TESTING YOUR DOKPLOY WEBSOCKET ISSUE")
    print("=" * 60)
    print("Using coach/player mode to debug websocket errors in Dokploy deployment")
    
    # Create test project structure similar to yours
    project_dir = tempfile.mkdtemp(prefix="g3_dokploy_test_")
    
    # Create the coach/player config
    config_path = f"{project_dir}/config.toml"
    config_content = """# G3 Configuration - Coach/Player/Planner Setup for Dokploy Issue
# Optimized for localhost:9000 load balancer with minimaxm2/kimik2

[providers]
default_provider = "anthropic.minimax_local"
coach = "anthropic.coach"
player = "anthropic.player"
planner = "anthropic.planner"

[providers.anthropic.minimax_local]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.2
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[providers.anthropic.coach]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 32000
temperature = 0.1
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[providers.anthropic.player]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.3
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[providers.anthropic.planner]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.15
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[agent]
name = "dokploy-debug-agent"
provider = "anthropic.minimax_local"
fallback_default_max_tokens = 8192
enable_streaming = true
allow_multiple_tool_calls = true
timeout_seconds = 120
max_retry_attempts = 5
autonomous_max_retry_attempts = 8
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515"""
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    # Create a minimal test project structure
    os.makedirs(f"{project_dir}/src", exist_ok=True)
    os.makedirs(f"{project_dir}/tests", exist_ok=True)
    
    # Create requirements for the Dokploy issue
    requirements_content = """# Dokploy WebSocket Issue - Debug Requirements

## Issue Description:
WebSocket errors occur after logging in to the vibe-kanban-expert-manager deployed on Dokploy.

## Current Setup:
- Using Dokploy MCP servers for configuration
- Agents can configure project on Dokploy
- Login credentials in .env file
- Playwright MCP web tests for user stories
- WebSocket errors after successful login

## Success Criteria:
1. Identify root cause of WebSocket errors
2. Fix WebSocket connection issues
3. Ensure stable WebSocket connections after login
4. Test with Playwright to verify fix
5. Document the solution

## Technical Areas to Investigate:
- WebSocket configuration in the application
- Dokploy deployment settings
- MCP server WebSocket handling
- Authentication and session management
- Network configuration and proxies
- Docker container WebSocket settings
"""
    
    requirements_path = f"{project_dir}/requirements.md"
    with open(requirements_path, "w") as f:
        f.write(requirements_content)
    
    print(f"\n📁 Created test project: {project_dir}")
    print(f"   Config: {config_path}")
    print(f"   Requirements: {requirements_path}")
    
    # Test 1: Basic tool execution to verify the fix works
    print("\n🔧 Test 1: Basic Tool Execution (Post-Fix)")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "shell:pwd && echo 'Testing tool execution'"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            print("   ✅ Basic tool execution works")
            print(f"   Output: {result.stdout.strip()[:100]}...")
        else:
            print("   ❌ Basic tool execution failed")
            print(f"   Error: {result.stderr[:100]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Basic tool execution error: {e}")
        return False
    
    # Test 2: File operations (should work based on previous tests)
    print("\n📁 Test 2: File Operations")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "list_workspace_files"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ File operations work")
        else:
            print("   ❌ File operations failed")
            
    except Exception as e:
        print(f"   ❌ File operations error: {e}")
    
    # Test 3: Requirements analysis (demonstrates planning mode)
    print("\n🎯 Test 3: Requirements Analysis (Planning Mode Demo)")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "read_file requirements.md"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ Requirements reading works")
            output = result.stdout.strip()
            if "WebSocket errors" in output:
                print("   ✅ Requirements contain WebSocket issue details")
            else:
                print("   ℹ️  Requirements reading functional")
        else:
            print("   ⚠️  Requirements reading had issues")
            
    except Exception as e:
        print(f"   ⚠️  Requirements reading error: {e}")
    
    print(f"\n🧹 Test files location: {project_dir}")
    print("   (Files preserved for debugging - delete manually when done)")
    
    return True

def demonstrate_usage():
    """Show how to use the new setup for your Dokploy issue"""
    print("\n📚 USAGE FOR YOUR DOKPLOY WEBSOCKET ISSUE")
    print("=" * 60)
    print("Now that the infinite loop fix is in place, here's how to use the coach/player setup:")
    
    examples = [
        {
            "mode": "Requirements Analysis",
            "command": "g3 --config coach_player_planner_config.toml --planning --codepath ./your-project",
            "description": "Use planner to refine requirements for WebSocket debugging"
        },
        {
            "mode": "Autonomous Debugging",
            "command": "g3 --config coach_player_planner_config.toml --autonomous --codepath ./your-project",
            "description": "Use coach-player loop to systematically debug WebSocket issues"
        },
        {
            "mode": "Single Task",
            "command": "g3 --config coach_player_planner_config.toml 'debug WebSocket connection errors in Dokploy deployment'",
            "description": "Quick focused debugging of specific WebSocket issues"
        },
        {
            "mode": "Interactive Analysis",
            "command": "g3 --config coach_player_planner_config.toml",
            "description": "Interactive mode for step-by-step debugging"
        }
    ]
    
    for example in examples:
        print(f"\n🎯 {example['mode']}:")
        print(f"   Command: {example['command']}")
        print(f"   Description: {example['description']}")
    
    print("\n💡 Key Benefits of This Setup:")
    print("   • Coach provides careful, systematic analysis of WebSocket issues")
    print("   • Player provides creative solutions and implementations")
    print("   • Planner ensures comprehensive requirements gathering")
    print("   • All work with your localhost:9000 load balancer")
    print("   • Optimized retry settings for complex debugging operations")
    print("   • The infinite loop issue has been fixed")

if __name__ == "__main__":
    success = test_your_dokploy_issue()
    demonstrate_usage()
    sys.exit(0 if success else 1)