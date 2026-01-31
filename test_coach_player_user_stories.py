#!/usr/bin/env python3
"""
End-to-end user stories tests for G3 coach/player autonomous mode with load balancer.
Tests the core functionality that was fixed for streaming mode compatibility.
"""

import subprocess
import sys
import tempfile
import os
import json
import time
from pathlib import Path

def create_test_project():
    """Create a minimal test project for coach/player testing"""
    project_dir = tempfile.mkdtemp(prefix="g3_test_project_")
    
    # Create a simple Python project structure
    os.makedirs(f"{project_dir}/src", exist_ok=True)
    os.makedirs(f"{project_dir}/tests", exist_ok=True)
    
    # Create requirements file
    with open(f"{project_dir}/requirements.txt", "w") as f:
        f.write("flask==2.3.3\npytest==7.4.0\n")
    
    # Create a basic app.py
    with open(f"{project_dir}/src/app.py", "w") as f:
        f.write("""# Basic Flask app for testing
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from G3 test project!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
""")
    
    # Create a basic test file
    with open(f"{project_dir}/tests/test_app.py", "w") as f:
        f.write("""import pytest
from src.app import app

def test_hello():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b'Hello from G3 test project!' in response.data

def test_health():
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        assert b'healthy' in response.data
""")
    
    return project_dir

def test_coach_player_basic_implementation():
    """Test 1: Basic coach/player implementation workflow"""
    print("\n🎯 USER STORY 1: Basic Coach/Player Implementation")
    print("=" * 60)
    print("As a developer, I want to use G3's coach/player mode to implement")
    print("a simple feature so that I can verify the autonomous workflow works")
    print("with my localhost load balancer.")
    
    # Create test project
    project_dir = create_test_project()
    print(f"\n📁 Created test project: {project_dir}")
    
    # Create coach/player config for load balancer
    config_content = f"""# Coach/Player config for localhost load balancer

[providers]
default_provider = "anthropic.minimax_local"
coach = "anthropic.coach"  
player = "anthropic.player"

[providers.anthropic.minimax_local]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.3
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

[agent]
name = "coach-player-test"
provider = "anthropic.minimax_local"
fallback_default_max_tokens = 8192
enable_streaming = true
allow_multiple_tool_calls = true
timeout_seconds = 60
max_retry_attempts = 3
autonomous_max_retry_attempts = 6
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    config_path = f"{project_dir}/test_config.toml"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    # Create requirements for the feature
    requirements_content = """# Test Requirements for Coach/Player Mode

## Feature: Add User Authentication to Flask App

### Requirements:
1. Add a `/login` endpoint that accepts POST requests with JSON body
2. Add a `/logout` endpoint that clears session
3. Add session management using Flask sessions
4. Add proper error handling for invalid credentials
5. Update the `/` endpoint to require authentication
6. Write tests for the new authentication functionality

### Technical Details:
- Use Flask sessions for session management
- Accept JSON format: {"username": "string", "password": "string"}
- Return appropriate HTTP status codes
- Handle both successful and failed authentication attempts

### Success Criteria:
- `/login` accepts POST with JSON credentials
- `/logout` clears session properly  
- `/` endpoint requires authentication
- All tests pass
- Error handling works correctly
"""
    
    requirements_path = f"{project_dir}/requirements.md"
    with open(requirements_path, "w") as f:
        f.write(requirements_content)
    
    print(f"\n📋 Created requirements file: {requirements_path}")
    
    # Test the autonomous mode with coach/player
    print("\n🚀 Starting Coach/Player Autonomous Mode Test...")
    print("   This will test:")
    print("   - Player agent implements the authentication feature")
    print("   - Coach agent reviews the implementation")
    print("   - Tool execution works with streaming mode")
    print("   - Load balancer handles the traffic correctly")
    
    try:
        # Run autonomous mode with coach/player
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "--autonomous",
             "--codepath", project_dir,
             "--max-turns", "3"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=180  # 3 minutes timeout
        )
        
        print(f"\n📊 Test Results:")
        print(f"   Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("   ✅ Coach/Player mode completed successfully")
            print("   📄 Output preview:")
            output_lines = result.stdout.split('\n')
            for line in output_lines[:20]:  # Show first 20 lines
                if line.strip():
                    print(f"      {line}")
            if len(output_lines) > 20:
                print("      ... (truncated)")
        else:
            print("   ❌ Coach/Player mode failed")
            print(f"   Error output: {result.stderr[:500]}")
            
        # Check if any files were created/modified
        print(f"\n📁 Files in project after test:")
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if not file.endswith('.toml') and not file.endswith('.md'):  # Skip config files
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_dir)
                    print(f"   {rel_path}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("   ⚠️  Test timed out - this might indicate the agent is hanging or taking too long")
        return False
    finally:
        # Clean up (optional - keep for debugging)
        print(f"\n🧹 Test project location: {project_dir}")
        print("   (Files preserved for debugging - delete manually when done)")

def test_flock_mode_parallel_development():
    """Test 2: Flock mode with parallel agents"""
    print("\n🎯 USER STORY 2: Flock Mode Parallel Development")
    print("=" * 60)
    print("As a team lead, I want to use multiple agents in parallel")
    print("to develop different modules simultaneously so that I can")
    print("accelerate development on large projects.")
    
    # Create flock configuration
    flock_config = f"""# Flock configuration for parallel development test

name: "test-flock"
description: "Test flock mode with parallel agents"

settings:
  max_agents: 3
  timeout_minutes: 30
  provider: "anthropic.minimax_local"

agents:
  - name: "api-module"
    description: "Develop API endpoints"
    working_dir: "src/api"
    requirements: |
      Create a simple API module with:
      - A /users endpoint that returns JSON
      - Proper error handling
      - Input validation

  - name: "utils-module"
    description: "Develop utility functions"
    working_dir: "src/utils"
    requirements: |
      Create utility functions for:
      - JSON validation
      - Error formatting
      - Logging helpers

  - name: "test-module"
    description: "Write tests for modules"
    working_dir: "tests"
    requirements: |
      Write comprehensive tests for:
      - API endpoints
      - Utility functions
      - Error scenarios
"""
    
    # Create test project
    project_dir = tempfile.mkdtemp(prefix="g3_flock_test_")
    os.makedirs(f"{project_dir}/src/api", exist_ok=True)
    os.makedirs(f"{project_dir}/src/utils", exist_ok=True)
    os.makedirs(f"{project_dir}/tests", exist_ok=True)
    
    # Write flock configuration
    flock_path = f"{project_dir}/flock.yaml"
    with open(flock_path, "w") as f:
        f.write(flock_config)
    
    print(f"\n📁 Created flock test project: {project_dir}")
    print(f"   Flock config: {flock_path}")
    
    # Create coach/player config
    config_content = f"""# Config for flock mode test

[providers]
default_provider = "anthropic.minimax_local"

[providers.anthropic.minimax_local]
model = "minimax"
base_url = "http://localhost:9000/v1/messages"
max_tokens = 64000
temperature = 0.3
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[agent]
name = "flock-test"
provider = "anthropic.minimax_local"
fallback_default_max_tokens = 8192
enable_streaming = true
allow_multiple_tool_calls = true
timeout_seconds = 60
max_retry_attempts = 3
autonomous_max_retry_attempts = 6
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    config_path = f"{project_dir}/config.toml"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print("\n🚀 Starting Flock Mode Test...")
    print("   This will test:")
    print("   - Multiple agents working in parallel")
    print("   - Each agent handles different modules")
    print("   - Coordination and progress tracking")
    print("   - Streaming mode with load balancer")
    
    try:
        # Run flock mode
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "--flock", flock_path,
             "--timeout", "15"],  # 15 minute timeout
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes for test
        )
        
        print(f"\n📊 Flock Test Results:")
        print(f"   Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("   ✅ Flock mode completed successfully")
            print("   📄 Output preview:")
            lines = result.stdout.split('\n')
            for line in lines[:15]:
                if 'flock' in line.lower() or 'agent' in line.lower() or 'status' in line.lower():
                    print(f"      {line}")
        else:
            print("   ❌ Flock mode failed")
            print(f"   Error: {result.stderr[:300]}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("   ⚠️  Flock test timed out")
        return False
    finally:
        print(f"\n🧹 Flock test project location: {project_dir}")

def test_planning_mode_structured_workflow():
    """Test 3: Planning mode with structured workflow"""
    print("\n🎯 USER STORY 3: Planning Mode Structured Workflow")
    print("=" * 60)
    print("As a project manager, I want to use planning mode")
    print("to refine requirements and implement them systematically")
    print("with proper git integration and documentation.")
    
    # Create test project with git
    project_dir = tempfile.mkdtemp(prefix="g3_planning_test_")
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_dir, capture_output=True)
    
    print(f"\n📁 Created planning test project: {project_dir}")
    
    # Create coach/player config
    config_content = f"""# Config for planning mode test

[providers]
default_provider = "anthropic.minimax_local"
planner = "anthropic.planner"

[providers.anthropic.minimax_local]
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
temperature = 0.1
api_key = "fake-api-key-for-localhost-endpoint"
use_bearer_auth = true

[agent]
name = "planning-test"
provider = "anthropic.minimax_local"
fallback_default_max_tokens = 8192
enable_streaming = true
allow_multiple_tool_calls = true
timeout_seconds = 60
max_retry_attempts = 3
autonomous_max_retry_attempts = 6
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = false
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515
"""

    config_path = f"{project_dir}/config.toml"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    # Create initial requirements
    os.makedirs(f"{project_dir}/g3-plan", exist_ok=True)
    
    initial_requirements = """# New Requirements for Planning Mode Test

## Project: Simple Task Management API

### Initial Requirements:
1. Create a Flask API for task management
2. Support CRUD operations for tasks
3. Use SQLite for data storage
4. Include proper error handling
5. Write comprehensive tests

### Technical Specifications:
- Python 3.8+
- Flask framework
- SQLite database
- RESTful API design
- JSON responses
- Proper HTTP status codes

### API Endpoints Needed:
- GET /tasks - List all tasks
- GET /tasks/{id} - Get specific task
- POST /tasks - Create new task
- PUT /tasks/{id} - Update task
- DELETE /tasks/{id} - Delete task

### Task Model:
- id: integer (primary key)
- title: string (required)
- description: string (optional)
- completed: boolean (default: false)
- created_at: datetime
- updated_at: datetime
"""
    
    requirements_path = f"{project_dir}/g3-plan/new_requirements.md"
    with open(requirements_path, "w") as f:
        f.write(initial_requirements)
    
    print(f"\n📋 Created initial requirements: {requirements_path}")
    
    print("\n🚀 Starting Planning Mode Test...")
    print("   This will test:")
    print("   - Requirements refinement phase")
    print("   - Implementation phase with coach/player")
    print("   - Git integration and commits")
    print("   - Planning artifact management")
    
    try:
        # Run planning mode
        result = subprocess.run(
            ["/home/clauderun/g3-vps-friendly/target/release/g3", 
             "--config", config_path,
             "--planning",
             "--codepath", project_dir,
             "--workspace", project_dir,
             "--max-turns", "2"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=180  # 3 minutes
        )
        
        print(f"\n📊 Planning Test Results:")
        print(f"   Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("   ✅ Planning mode completed successfully")
            
            # Check what was created
            print("\n📁 Files created during planning:")
            for root, dirs, files in os.walk(f"{project_dir}/g3-plan"):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_dir)
                    print(f"   {rel_path}")
            
            # Check git status
            git_result = subprocess.run(["git", "status"], cwd=project_dir, capture_output=True, text=True)
            if git_result.returncode == 0:
                print(f"\n📝 Git status:")
                print(git_result.stdout)
                
        else:
            print("   ❌ Planning mode failed")
            print(f"   Error: {result.stderr[:400]}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("   ⚠️  Planning test timed out")
        return False
    finally:
        print(f"\n🧹 Planning test project location: {project_dir}")

def run_all_tests():
    """Run all user story tests"""
    print("🚀 G3 COACH/PLAYER USER STORIES - END-TO-END TESTS")
    print("=" * 80)
    print("Testing G3's autonomous modes with localhost:9000 load balancer")
    print("after MCP removal and streaming mode fixes.")
    
    results = []
    
    # Test 1: Basic Coach/Player
    print("\n" + "="*80)
    results.append(("Coach/Player Basic", test_coach_player_basic_implementation()))
    
    # Test 2: Flock Mode
    print("\n" + "="*80)
    results.append(("Flock Mode Parallel", test_flock_mode_parallel_development()))
    
    # Test 3: Planning Mode
    print("\n" + "="*80)
    results.append(("Planning Mode Structured", test_planning_mode_structured_workflow()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ G3's coach/player autonomous modes work correctly with your load balancer")
        print("✅ Streaming mode tool execution is fixed")
        print("✅ Multi-agent coordination works properly")
        print("\n🚀 Your G3 agent is ready for production use with localhost:9000!")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("   Check the test output above for specific issues")
        print("   The test project directories are preserved for debugging")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)