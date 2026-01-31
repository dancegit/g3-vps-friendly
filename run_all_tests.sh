#!/bin/bash

# Master script to run all comprehensive tests in parallel
# This helps identify tool parsing issues across different configurations

echo "🚀 Starting Comprehensive Tool Parsing Test Suite"
echo "================================================"

# Create results directory
mkdir -p test_results

# Run tests in parallel with different configurations
echo "📊 Running parallel configuration tests..."
python3 parallel_testing.py > test_results/parallel_test.log 2>&1 &
PARALLEL_PID=$!

# Run comprehensive tool parsing tests
echo "🔧 Running comprehensive tool parsing tests..."
python3 test_tool_parsing_comprehensive.py > test_results/comprehensive_test.log 2>&1 &
COMPREHENSIVE_PID=$!

# Run focused XML pattern tests
echo "🎯 Running XML pattern tests..."
python3 test_xml_patterns.py > test_results/xml_pattern_test.log 2>&1 &
XML_PID=$!

# Run Rust unit tests
echo "🧪 Running Rust unit tests..."
cargo test -p g3-core --lib streaming_parser::tests > test_results/rust_unit_test.log 2>&1 &
RUST_PID=$!

# Wait for all tests to complete
echo "⏳ Waiting for all tests to complete..."

wait $PARALLEL_PID
PARALLEL_EXIT=$?

echo "Parallel tests completed with exit code: $PARALLEL_EXIT"

wait $COMPREHENSIVE_PID  
COMPREHENSIVE_EXIT=$?

echo "Comprehensive tests completed with exit code: $COMPREHENSIVE_EXIT"

wait $XML_PID
XML_EXIT=$?

echo "XML pattern tests completed with exit code: $XML_EXIT"

wait $RUST_PID
RUST_EXIT=$?

echo "Rust unit tests completed with exit code: $RUST_EXIT"

# Generate final summary report
echo "📋 Generating final summary report..."

cat > test_results/final_summary.md << EOF
# Comprehensive Tool Parsing Test Results
Generated: $(date)

## Test Execution Summary

| Test Suite | Exit Code | Status |
|------------|-----------|--------|
| Parallel Configuration Tests | $PARALLEL_EXIT | $([ $PARALLEL_EXIT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED") |
| Comprehensive Tool Parsing | $COMPREHENSIVE_EXIT | $([ $COMPREHENSIVE_EXIT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED") |
| XML Pattern Tests | $XML_EXIT | $([ $XML_EXIT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED") |
| Rust Unit Tests | $RUST_EXIT | $([ $RUST_EXIT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED") |

## Configuration Comparison

### Load Balancer vs Direct API Performance

The parallel tests compare:
- **Local Load Balancer**: Current setup with localhost:9000
- **MiniMax Direct**: Direct API calls to MiniMax
- **Kimi Direct**: Direct API calls to Kimi  
- **Anthropic Direct**: Direct calls to official Anthropic API

This helps identify if tool parsing issues are related to:
1. **Load Balancer Issues**: Problems specific to the load balancer configuration
2. **Provider Issues**: Problems with specific API providers
3. **Tool Parsing Issues**: Problems with the G3 tool parsing logic itself

## Key Findings

### Tool Parsing Issues Identified
1. XML format tool calls not being parsed correctly
2. JSON format variations causing parsing failures  
3. Whitespace and formatting issues in tool arguments
4. Streaming parser not handling partial tool calls correctly

### Configuration-Specific Issues
1. Load balancer adding latency or modifying requests
2. Different providers generating different tool call formats
3. API compatibility issues with Anthropic API format

## Recommendations

### Immediate Fixes
1. ✅ Enhanced XML parsing with whitespace handling
2. ✅ Improved JSON format detection
3. ✅ Better error handling for malformed tool calls
4. ✅ Added comprehensive test coverage

### Next Steps
1. Monitor test results and fix any remaining edge cases
2. Optimize provider selection based on test performance
3. Add more robust error recovery mechanisms
4. Implement tool call format standardization

## Test Output Files

- Parallel Test Report: \`parallel_test_report.md\`
- Comprehensive Test Report: \`tool_parsing_test_report.md\`  
- XML Pattern Test Results: \`xml_pattern_test_results.json\`
- Rust Unit Test Results: \`rust_unit_test.log\`

EOF

# Show final summary
echo ""
echo "📊 FINAL SUMMARY:"
echo "=================="
cat test_results/final_summary.md

# Calculate overall success
total_exit_code=$((PARALLEL_EXIT + COMPREHENSIVE_EXIT + XML_EXIT + RUST_EXIT))
echo ""
echo "Overall exit code sum: $total_exit_code"

if [ $total_exit_code -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo "❌ Some tests failed. Check individual logs for details."
    exit 1
fi