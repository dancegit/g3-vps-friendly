#!/usr/bin/env python3
"""
Test the Dokploy WebSocket debugging scenario to ensure the agent can handle complex requests.
"""

import subprocess
import sys
import os

def test_dokploy_scenario():
    """Test the Dokploy WebSocket debugging scenario."""
    
    config_file = 'test_localhost_config.toml'
    
    # The original user's request
    user_request = """im trying to deploy correctly the vibe-kanban-expert-manager on the dokploy using the dokploy mcp and so on , the agents know about those tools and can use the mcp servers to try to configure the project on dokploy correctly setting up the correct subdomains that points to the correct docker image in the local dokploy, the login credentials are defined in .env and we tried to run playwright mcp web tests and so on for the users stories but we have some websocket errors after logging in, can you fix that?"""
    
    print("🧪 Testing Dokploy WebSocket debugging scenario...")
    print(f"User request length: {len(user_request)} characters")
    
    test_command = [
        './target/release/g3',
        '--config', config_file,
        '--new-session',
        '--quiet',
        user_request
    ]
    
    try:
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout for complex request
        )
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            # Check if the agent started taking action (executing tools)
            if "shell" in result.stdout or "find" in result.stdout or "read" in result.stdout:
                print("✅ SUCCESS: Agent started executing tools (not stuck in thinking mode)")
                print("📋 Output snippet:")
                print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
                return True
            elif "think" in result.stdout.lower() and len(result.stdout.strip()) < 200:
                print("❌ FAILURE: Agent stuck in thinking mode")
                print(f"Output: {result.stdout}")
                return False
            else:
                print("⚠️  AGENT RESPONDED: Let me check if it's making progress...")
                # If it's a long response, it might be working properly
                if len(result.stdout) > 500:
                    print("✅ SUCCESS: Agent produced substantial output (likely working)")
                    return True
                else:
                    print(f"❓ UNCLEAR: Short response - {result.stdout}")
                    return False
        else:
            print("❌ FAILURE: No output captured")
            return False
            
        if result.stderr:
            print(f"Stderr: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ FAILURE: Command timed out (likely stuck)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_dokploy_scenario()
    sys.exit(0 if success else 1)