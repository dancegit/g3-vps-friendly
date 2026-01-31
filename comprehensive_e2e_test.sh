#!/bin/bash

# Comprehensive E2E Test Suite for G3 Tool Execution Fix
# This test runs in nohup to avoid timeout issues

echo "🚀 Starting comprehensive E2E test suite for G3 tool execution fix..."
echo "Using binary: ~/.local/bin/g3"
echo "Config: test_localhost_config.toml"
echo "Provider: localhost:9000 (minimax via load balancer)"
echo ""

# Create test results directory
mkdir -p e2e_test_results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Test 1: Simple tool execution (should complete quickly)
echo "Test 1: Simple shell command execution"
nohup bash -c '
  echo "=== Test 1: Simple shell command ===" > e2e_test_results/test1_${TIMESTAMP}.log
  echo "Command: echo E2E_TEST_SUCCESS" >> e2e_test_results/test1_${TIMESTAMP}.log
  echo "Start time: $(date)" >> e2e_test_results/test1_${TIMESTAMP}.log
  
  timeout 60 /home/clauderun/.local/bin/g3 \
    --config test_localhost_config.toml \
    --new-session \
    --quiet \
    "execute echo E2E_TEST_SUCCESS" >> e2e_test_results/test1_${TIMESTAMP}.log 2>&1
  
  echo "End time: $(date)" >> e2e_test_results/test1_${TIMESTAMP}.log
  echo "Return code: $?" >> e2e_test_results/test1_${TIMESTAMP}.log
' > e2e_test_results/test1_nohup.log 2>&1 &

TEST1_PID=$!

# Test 2: Multiple tool calls in sequence
echo "Test 2: Multiple tool calls"
sleep 10
nohup bash -c '
  echo "=== Test 2: Multiple tool calls ===" > e2e_test_results/test2_${TIMESTAMP}.log
  echo "Commands: pwd, ls, date" >> e2e_test_results/test2_${TIMESTAMP}.log
  echo "Start time: $(date)" >> e2e_test_results/test2_${TIMESTAMP}.log
  
  timeout 90 /home/clauderun/.local/bin/g3 \
    --config test_localhost_config.toml \
    --new-session \
    --quiet \
    "execute pwd && ls -la && date" >> e2e_test_results/test2_${TIMESTAMP}.log 2>&1
  
  echo "End time: $(date)" >> e2e_test_results/test2_${TIMESTAMP}.log
  echo "Return code: $?" >> e2e_test_results/test2_${TIMESTAMP}.log
' > e2e_test_results/test2_nohup.log 2>&1 &

TEST2_PID=$!

# Test 3: Complex scenario similar to user's Dokploy issue
echo "Test 3: Complex deployment debugging scenario"
sleep 10
nohup bash -c '
  echo "=== Test 3: Complex scenario ===" > e2e_test_results/test3_${TIMESTAMP}.log
  echo "Scenario: Debug WebSocket deployment issues" >> e2e_test_results/test3_${TIMESTAMP}.log
  echo "Start time: $(date)" >> e2e_test_results/test3_${TIMESTAMP}.log
  
  timeout 120 /home/clauderun/.local/bin/g3 \
    --config test_localhost_config.toml \
    --new-session \
    --quiet \
    "I need to debug WebSocket connection issues in a deployment. Please explore the current directory structure, look for any configuration files related to WebSockets, Docker deployments, or environment variables. Check for .env files, docker-compose files, and any web-related configuration. Provide a summary of what you found." >> e2e_test_results/test3_${TIMESTAMP}.log 2>&1
  
  echo "End time: $(date)" >> e2e_test_results/test3_${TIMESTAMP}.log
  echo "Return code: $?" >> e2e_test_results/test3_${TIMESTAMP}.log
' > e2e_test_results/test3_nohup.log 2>&1 &

TEST3_PID=$!

# Test 4: File operations and exploration
echo "Test 4: File operations and directory exploration"
sleep 10
nohup bash -c '
  echo "=== Test 4: File operations ===" > e2e_test_results/test4_${TIMESTAMP}.log
  echo "Tasks: List files, check for README, read first 10 lines" >> e2e_test_results/test4_${TIMESTAMP}.log
  echo "Start time: $(date)" >> e2e_test_results/test4_${TIMESTAMP}.log
  
  timeout 90 /home/clauderun/.local/bin/g3 \
    --config test_localhost_config.toml \
    --new-session \
    --quiet \
    "Please list all files in the current directory, check if README.md exists, and if it does, show me the first 10 lines. Then provide a summary of what you found." >> e2e_test_results/test4_${TIMESTAMP}.log 2>&1
  
  echo "End time: $(date)" >> e2e_test_results/test4_${TIMESTAMP}.log
  echo "Return code: $?" >> e2e_test_results/test4_${TIMESTAMP}.log
' > e2e_test_results/test4_nohup.log 2>&1 &

TEST4_PID=$!

# Test 5: Original user scenario - Dokploy WebSocket debugging
echo "Test 5: Original Dokploy WebSocket debugging scenario"
sleep 10
nohup bash -c '
  echo "=== Test 5: Dokploy WebSocket debugging ===" > e2e_test_results/test5_${TIMESTAMP}.log
  echo "Original user request about Dokploy deployment" >> e2e_test_results/test5_${TIMESTAMP}.log
  echo "Start time: $(date)" >> e2e_test_results/test5_${TIMESTAMP}.log
  
  timeout 180 /home/clauderun/.local/bin/g3 \
    --config test_localhost_config.toml \
    --new-session \
    --quiet \
    "im trying to deploy correctly the vibe-kanban-expert-manager on the dokploy using the dokploy mcp and so on , the agents know about those tools and can use the mcp servers to try to configure the project on dokploy correctly setting up the correct subdomains that points to the correct docker image in the local dokploy, the login credentials are defined in .env and we tried to run playwright mcp web tests and so on for the users stories but we have some websocket errors after logging in, can you fix that?" >> e2e_test_results/test5_${TIMESTAMP}.log 2>&1
  
  echo "End time: $(date)" >> e2e_test_results/test5_${TIMESTAMP}.log
  echo "Return code: $?" >> e2e_test_results/test5_${TIMESTAMP}.log
' > e2e_test_results/test5_nohup.log 2>&1 &

TEST5_PID=$!

echo ""
echo "🧪 All tests started!"
echo "Test PIDs: $TEST1_PID, $TEST2_PID, $TEST3_PID, $TEST4_PID, $TEST5_PID"
echo "Waiting for tests to complete..."
echo ""

# Wait for all tests to complete
wait $TEST1_PID $TEST2_PID $TEST3_PID $TEST4_PID $TEST5_PID

echo "✅ All tests completed!"
echo "Analyzing results..."

# Analysis function
analyze_test() {
  local test_file=$1
  local test_name=$2
  
  echo "=== $test_name ==="
  
  if [[ -f "$test_file" ]]; then
    # Check if tools were executed
    if grep -q "shell\|find\|read\|write" "$test_file"; then
      echo "✅ TOOL EXECUTION DETECTED"
    else
      echo "❌ NO TOOL EXECUTION FOUND"
    fi
    
    # Check if stuck in thinking mode
    if grep -q "thinking\|think" "$test_file"; then
      echo "⚠️  THINKING MODE DETECTED"
    fi
    
    # Check for final_output
    if grep -q "final_output" "$test_file"; then
      echo "✅ FINAL OUTPUT DETECTED"
    fi
    
    # Check for success indicators
    if grep -q "E2E_TEST_SUCCESS\|TEST_COMPLETE" "$test_file"; then
      echo "✅ SUCCESS INDICATORS FOUND"
    fi
    
    # Check execution time
    if grep -q "Start time\|End time" "$test_file"; then
      start_time=$(grep "Start time" "$test_file" | cut -d' ' -f3-)
      end_time=$(grep "End time" "$test_file" | cut -d' ' -f3-)
      echo "⏱️  Execution: $start_time -> $end_time"
    fi
    
    # Check return code
    return_code=$(grep "Return code:" "$test_file" | tail -1 | cut -d' ' -f3)
    if [[ "$return_code" == "0" ]]; then
      echo "✅ SUCCESSFUL RETURN CODE"
    else
      echo "❌ RETURN CODE: $return_code"
    fi
    
    echo ""
  else
    echo "❌ Test file not found: $test_file"
    echo ""
  fi
}

# Generate comprehensive report
echo "📊 COMPREHENSIVE E2E TEST RESULTS"
echo "=================================="
echo "Timestamp: $TIMESTAMP"
echo "Binary: /home/clauderun/.local/bin/g3"
echo "Config: test_localhost_config.toml"
echo "Provider: localhost:9000 (minimax via load balancer)"
echo ""

# Analyze each test
analyze_test "e2e_test_results/test1_${TIMESTAMP}.log" "Test 1: Simple Shell Command"
analyze_test "e2e_test_results/test2_${TIMESTAMP}.log" "Test 2: Multiple Tool Calls"
analyze_test "e2e_test_results/test3_${TIMESTAMP}.log" "Test 3: Complex Scenario"
analyze_test "e2e_test_results/test4_${TIMESTAMP}.log" "Test 4: File Operations"
analyze_test "e2e_test_results/test5_${TIMESTAMP}.log" "Test 5: Dokploy WebSocket Debugging"

# Overall summary
echo "📋 OVERALL SUMMARY"
echo "=================="

# Count successful tests
total_tests=5
successful_tests=0
tool_execution_count=0
final_output_count=0

for i in {1..5}; do
  test_file="e2e_test_results/test${i}_${TIMESTAMP}.log"
  if [[ -f "$test_file" ]]; then
    if grep -q "shell\|find\|read\|write" "$test_file" 2>/dev/null; then
      tool_execution_count=$((tool_execution_count + 1))
    fi
    if grep -q "final_output" "$test_file" 2>/dev/null; then
      final_output_count=$((final_output_count + 1))
    fi
    return_code=$(grep "Return code:" "$test_file" 2>/dev/null | tail -1 | cut -d' ' -f3)
    if [[ "$return_code" == "0" ]]; then
      successful_tests=$((successful_tests + 1))
    fi
  fi
done

echo "Total tests: $total_tests"
echo "Tests with tool execution: $tool_execution_count/$total_tests"
echo "Tests with final_output: $final_output_count/$total_tests"
echo "Tests with return code 0: $successful_tests/$total_tests"

if [[ $tool_execution_count -gt 0 ]]; then
  echo ""
  echo "✅ OVERALL RESULT: TOOL EXECUTION FIX IS WORKING!"
  echo "The agent is now properly executing tools instead of getting stuck in thinking mode."
else
  echo ""
  echo "❌ OVERALL RESULT: NO TOOL EXECUTION DETECTED"
  echo "The fix may not be working as expected."
fi

# Save summary
echo "Test completed at: $(date)" >> e2e_test_results/summary_${TIMESTAMP}.txt
echo "Tool execution: $tool_execution_count/$total_tests" >> e2e_test_results/summary_${TIMESTAMP}.txt
echo "Final output: $final_output_count/$total_tests" >> e2e_test_results/summary_${TIMESTAMP}.txt
echo "Return code 0: $successful_tests/$total_tests" >> e2e_test_results/summary_${TIMESTAMP}.txt

echo ""
echo "📁 Test results saved to: e2e_test_results/"
echo "📄 Summary saved to: e2e_test_results/summary_${TIMESTAMP}.txt"