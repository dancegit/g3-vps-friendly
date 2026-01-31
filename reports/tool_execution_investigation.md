# Tool Execution Investigation Report

## Executive Summary

The G3 agent appears to execute tools successfully but the execution path is unclear and inconsistent. Commands execute and produce output, but the normal tool dispatch debug logs are never triggered, suggesting multiple execution paths exist.

## Key Findings

### 1. Dual Execution Paths Discovered

**Path 1: Normal Tool Dispatch (Expected)**
- Streaming parser looks for JSON tool calls: `{"tool": "shell", "args": {...}}`
- Tool dispatch system routes to appropriate handlers
- Debug logs should show: `TOOL_DISPATCH`, `SHELL_TOOL`, `AGENT`
- **Issue**: This path is never triggered in our tests

**Path 2: Direct Execution (Actual)**
- Commands execute successfully without normal dispatch logs
- Output appears to come through g3-execution crate directly
- XML format displayed: `<invoke_tool_call><tool name="shell"...`
- **Evidence**: Commands work but dispatch logs missing

### 2. XML vs JSON Tool Call Format Issue

**Current Output Format (XML-like):**
```xml
<invoke_tool_call>
<tool name="shell" args="{\"command\": \"echo test\"}"/>
</invoke_tool_call>
```

**Expected Format (JSON):**
```json
{"tool": "shell", "args": {"command": "echo test"}}
```

**Problem**: Streaming parser only looks for JSON patterns:
- `{"tool":"`
- `{ "tool":"`
- `{"tool" :`
- `{ "tool" :`

**Evidence**: Debug logs show "Checking chunk content for JSON tool calls" but never find any.

### 3. Evidence of Format Conversion

The XML format gets converted to actual tool execution somewhere in the pipeline:
- XML displayed in output
- But actual command execution occurs
- Suggests post-processing conversion from XML to internal tool calls

## Root Cause Analysis

### Primary Issue: Format Mismatch
The localhost:9000 load balancer (minimax) outputs XML-style tool calls, but G3's streaming parser expects JSON format. This causes:

1. **Streaming parser fails** to find JSON tool calls
2. **Normal dispatch bypassed** due to parsing failure
3. **Alternative execution engaged** (direct g3-execution calls)
4. **Inconsistent behavior** between different providers/models

### Secondary Issues

1. **Debug Logging Gap**: Custom debug logs not appearing, making diagnosis difficult
2. **Multiple Execution Paths**: Unclear which path is actually being used
3. **Provider Inconsistency**: Different providers may use different formats
4. **Load Balancer Compatibility**: localhost:9000 may not support native tool calling

## Evidence Collected

### Debug Log Analysis
```
🔍 STREAMING_PARSER: Checking chunk content for JSON tool calls: '<invoke name="shell"...'
[NO "Found X JSON tool calls" messages]
[NO "TOOL_DISPATCH" messages]
[NO "SHELL_TOOL" messages]
[But command executes successfully]
```

### Code Path Investigation
- **Streaming Parser**: Only searches for JSON patterns
- **Tool Dispatch**: Never triggered (no debug logs)
- **Shell Tool**: Should be called but debug logs missing
- **g3-execution**: Has direct Command::new() calls for bash execution

### Format Detection
- XML format consistently output by localhost:9000
- JSON format never found by streaming parser
- Actual execution occurs despite parsing failure

## Impact Assessment

### Critical Issues
1. **Unreliable Tool Execution**: Behavior varies by provider/model
2. **Debugging Difficulty**: Hard to trace actual execution path
3. **Provider Incompatibility**: localhost:9000 doesn't work optimally
4. **Maintenance Burden**: Multiple execution paths to maintain

### User Impact
- Commands execute but through unclear mechanisms
- Inconsistent behavior across different setups
- Difficult to debug when issues occur
- Unclear whether tools are being called properly

## Next Steps Required

1. **Research XML Tool Call Standards**: Investigate if XML is standard for some providers
2. **Implement XML Parsing**: Add support for XML tool call format
3. **Standardize Execution Path**: Ensure single, clear execution path
4. **Improve Debug Logging**: Add comprehensive logging throughout pipeline
5. **Provider Compatibility**: Ensure consistent behavior across providers

## Questions to Answer

1. Is XML format standard for Anthropic or other providers?
2. Where does XML-to-JSON conversion happen in the pipeline?
3. Why are custom debug logs not appearing?
4. Which execution path should be the canonical one?
5. How to ensure consistent behavior across all providers?