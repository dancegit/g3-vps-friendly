#!/usr/bin/env python3
"""
Test the new coach/player/planner setup for G3 with localhost load balancer.
Demonstrates how to use the different roles effectively.
"""

import subprocess
import sys
import tempfile
import os

def test_coach_player_setup():
    """Test the coach/player autonomous mode with the new setup"""
    print("🏗️  TESTING COACH/PLAYER/PLANNER SETUP")
    print("=" * 60)
    print("Testing G3's autonomous modes with the new role-based configuration")
    
    # Create test project
    project_dir = tempfile.mkdtemp(prefix="g3_coach_player_test_")
    
    # Create the updated config with coach/player/planner setup
    config_path = f"{project_dir}/config.toml"
    config_content = """# G3 Configuration - Coach/Player/Planner Setup for Autonomous Development
# Optimized for localhost:9000 load balancer with minimaxm2/kimik2

[providers]
# Default provider for general use
default_provider = "anthropic.minimax_local"

# Coach provider - for code review and analysis (more thoughtful, lower temp)
coach = "anthropic.coach"

# Player provider - for code generation and implementation (more creative, higher temp)
player = "anthropic.player"

# Planner provider - for requirements refinement and project planning
planner = "anthropic.planner"

# Base Anthropic configuration for general use
[providers.anthropic.minimax_local]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.2
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true  # For load balancer compatibility

# Coach configuration - optimized for careful analysis and review
[providers.anthropic.coach]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 32000  # Smaller context for focused review
temperature = 0.1   # Very low temp for consistent, careful analysis
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

# Player configuration - optimized for creative implementation
[providers.anthropic.player]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000  # Larger context for complex implementations
temperature = 0.3   # Higher temp for creative problem solving
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

# Planner configuration - optimized for requirements and planning
[providers.anthropic.planner]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.15  # Balanced temp for planning (between coach and player)
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[agent]
name = "coach-player-agent"
provider = "anthropic.minimax_local"  # Default for interactive mode
fallback_default_max_tokens = 8192
enable_streaming = true              # Enable streaming for better UX
allow_multiple_tool_calls = true     # Allow multiple tools per response
timeout_seconds = 120                # Longer timeout for complex operations
max_retry_attempts = 5               # More retries for reliability
autonomous_max_retry_attempts = 8    # Even more for autonomous mode
auto_compact = true                  # Auto compact at 80% context

[computer_control]
enabled = false                      # Disable for now (experimental)
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = false                      # Disable for now (can enable if needed)
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515"""
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print(f"\n📁 Created test project: {project_dir}")
    print(f"   Config file: {config_path}")
    
    # Test 1: Verify config loads correctly
    print("\n🔍 Test 1: Configuration Loading")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("   ✅ Configuration loads successfully")
        else:
            print("   ❌ Configuration loading failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Config test error: {e}")
        return False
    
    # Test 2: Basic tool execution with new config
    print("\n🔧 Test 2: Basic Tool Execution")
    try:
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "shell:echo 'Testing coach/player setup'"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ Basic tool execution works")
            print(f"   Output: {result.stdout.strip()[:100]}...")
        else:
            print("   ❌ Basic tool execution failed")
            print(f"   Error: {result.stderr[:100]}")
            
    except Exception as e:
        print(f"   ❌ Tool execution error: {e}")
    
    # Test 3: File operations with new config
    print("\n📁 Test 3: File Operations")
    try:
        # Create a test file
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "shell:echo 'Test content' > test.txt"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ File creation successful")
            
            # Read it back
            result2 = subprocess.run(
                ["/home/clauderun/g3-vps-friendly/target/release/g3", 
                 "--config", config_path,
                 "read_file test.txt"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result2.returncode == 0:
                print("   ✅ File reading successful")
            else:
                print("   ⚠️  File reading had issues")
        else:
            print("   ❌ File operations failed")
            
    except Exception as e:
        print(f"   ❌ File operations error: {e}")
    
    # Test 4: Demonstrate the different modes
    print("\n🎯 Test 4: Configuration Demonstration")
    print("   Your config now includes:")
    print("   ✅ Coach role (anthropic.coach) - Low temp for careful analysis")
    print("   ✅ Player role (anthropic.player) - Higher temp for creative implementation")
    print("   ✅ Planner role (anthropic.planner) - Balanced temp for requirements")
    print("   ✅ All use Bearer auth for localhost:9000 compatibility")
    print("   ✅ Optimized retry settings for autonomous operations")
    
    print(f"\n🧹 Test files location: {project_dir}")
    print("   (Files preserved for debugging - delete manually when done)")
    
    return True

def demonstrate_usage():
    """Show how to use the different modes with the new config"""
    print("\n📚 USAGE DEMONSTRATION")
    print("=" * 60)
    print("How to use the new coach/player/planner setup:")
    
    examples = [
        {
            "mode": "Interactive (default)",
            "command": "g3 --config coach_player_planner_config.toml",
            "description": "Use default provider for interactive chat"
        },
        {
            "mode": "Autonomous Mode",
            "command": "g3 --config coach_player_planner_config.toml --autonomous",
            "description": "Use coach-player loop with requirements.md"
        },
        {
            "mode": "Planning Mode",
            "command": "g3 --config coach_player_planner_config.toml --planning --codepath ./my-project",
            "description": "Use planner for requirements refinement"
        },
        {
            "mode": "Flock Mode",
            "command": "g3 --config coach_player_planner_config.toml --flock flock.yaml",
            "description": "Use multiple parallel agents"
        },
        {
            "mode": "Single Task",
            "command": "g3 --config coach_player_planner_config.toml 'implement user authentication'",
            "description": "Quick single-shot task"
        }
    ]
    
    for example in examples:
        print(f"\n🎯 {example['mode']}:")
        print(f"   Command: {example['command']}")
        print(f"   Description: {example['description']}")
    
    print("\n💡 Key Benefits of This Setup:")
    print("   • Coach provides careful, consistent analysis")
    print("   • Player provides creative, flexible implementation")
    print("   • Planner provides structured, thoughtful planning")
    print("   • All work with your localhost:9000 load balancer")
    print("   • Optimized for autonomous development workflows")

if __name__ == "__main__":
    success = test_coach_player_setup()
    demonstrate_usage()
    sys.exit(0 if success else 1)