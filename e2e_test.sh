#!/bin/bash

# Comprehensive E2E test for G3 tool execution fix
# This test runs in nohup to avoid timeout issues

echo "🚀 Starting comprehensive E2E test for G3 tool execution..."

# Create test results directory
mkdir -p test_results

# Test 1: Simple tool execution
echo "Test 1: Simple shell command execution"
echo "Testing basic tool execution with localhost:9000..."

nohup ./target/release/g3 \
  --config test_localhost_config.toml \
  --new-session \
  --quiet \
  "execute 'ls -la' and verify tool execution is working" > test_results/test1_simple.log 2>&1 &

TEST1_PID=$!
sleep 30
kill $TEST1_PID 2>/dev/null || true

# Test 2: Multiple tool calls
echo "Test 2: Multiple tool calls in sequence"
nohup ./target/release/g3 \
  --config test_localhost_config.toml \
  --new-session \
  --quiet \
  "list files in current directory, then check if README.md exists, then show its first 10 lines" > test_results/test2_multiple.log 2>&1 &

TEST2_PID=$!
sleep 45
kill $TEST2_PID 2>/dev/null || true

# Test 3: Complex request (similar to user's Dokploy issue)
echo "Test 3: Complex deployment debugging scenario"
nohup ./target/release/g3 \
  --config test_localhost_config.toml \
  --new-session \
  --quiet \
  "I need to debug WebSocket connection issues in a deployment. Please explore the current directory structure, look for any configuration files related to WebSockets, Docker deployments, or environment variables. Check for .env files, docker-compose files, and any web-related configuration." > test_results/test3_complex.log 2>&1 &

TEST3_PID=$!
sleep 60
kill $TEST3_PID 2>/dev/null || true

# Wait a bit for all processes to complete
sleep 5

echo "📊 Analyzing test results..."

# Check results
for test_file in test_results/test*.log; do
  if [[ -f "$test_file" ]]; then
    echo "=== $test_file ==="
    
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
    
    # Show relevant lines
    echo "--- Relevant output ---"
    grep -E "(shell|find|read|write|thinking|final_output)" "$test_file" | head -10
    echo ""
  fi
done

# Create summary
echo "📋 TEST SUMMARY" > test_results/summary.txt
echo "==================" >> test_results/summary.txt
echo "Tests run: 3" >> test_results/summary.txt
echo "Config used: test_localhost_config.toml" >> test_results/summary.txt
echo "Provider: localhost:9000 (minimax via load balancer)" >> test_results/summary.txt
echo "" >> test_results/summary.txt

# Count results
TOOL_EXECUTION_COUNT=$(grep -l "shell\|find\|read\|write" test_results/test*.log | wc -l)
THINKING_MODE_COUNT=$(grep -l "thinking\|think" test_results/test*.log | wc -l)

echo "Tool execution detected in: $TOOL_EXECUTION_COUNT/3 tests" >> test_results/summary.txt
echo "Thinking mode detected in: $THINKING_MODE_COUNT/3 tests" >> test_results/summary.txt

if [[ $TOOL_EXECUTION_COUNT -gt 0 ]]; then
  echo "✅ OVERALL RESULT: TOOL EXECUTION IS WORKING" >> test_results/summary.txt
else
  echo "❌ OVERALL RESULT: NO TOOL EXECUTION DETECTED" >> test_results/summary.txt
fi

cat test_results/summary.txt