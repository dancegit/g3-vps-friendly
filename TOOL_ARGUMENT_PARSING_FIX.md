# G3 Tool Argument Parsing Fix Summary

## Issue Analysis

The G3 tool was experiencing issues with tool argument parsing where:

1. **Tool calls were missing arguments**: Commands like `shell` were being called without the required `command` parameter
2. **Wrong arguments were being passed**: Instead of `ls`, the tool was receiving filenames like `Cargo.toml` or `test_tool_parsing.rs` as commands
3. **Intermittent behavior**: Sometimes tool calls worked correctly, sometimes they didn't

## Root Cause Investigation

Through analysis of the logs and codebase, I discovered that:

1. **XML Tool Call Format**: The LLM was generating tool calls in XML format like:
   ```xml
   <invoke name="shell">
     <parameter name="args">{"command": "ls -la"}</parameter>
   </invoke>
   ```

2. **JSON-Only Parser**: The streaming parser only supported JSON format:
   ```json
   {"tool":"shell","args":{"command":"ls -la"}}
   ```

3. **Missing XML Support**: The `StreamingToolParser` had no XML parsing capabilities, so XML tool calls were being ignored.

## Solution Implemented

### 1. Added XML Tool Call Patterns
```rust
const XML_TOOL_CALL_PATTERNS: [&str; 3] = [
    r#"<invoke name="#,
    r#"<invoke>"#,
    r#"<tool name="#,
];
```

### 2. Added XML Parsing Functions
- `try_parse_xml_tool_calls_from_text()` - Main XML parsing function
- `find_complete_xml_element_end()` - Finds complete XML elements
- `parse_xml_tool_call()` - Converts XML to ToolCall struct

### 3. Updated Processing Logic
- Modified `process_chunk()` to try XML parsing first, then JSON fallback
- Updated `try_parse_json_tool_call()` to check for XML before JSON
- Modified message completion handling to parse both XML and JSON

### 4. Enhanced Error Handling
- Added validation for empty tool names across all parsing paths
- Added proper debug logging for troubleshooting

## Key Changes Made

### File: `/home/clauderun/g3-vps-friendly/crates/g3-core/src/streaming_parser.rs`

1. **Added XML patterns and parsing logic**
2. **Integrated XML parsing into main processing flow**
3. **Enhanced debug logging for troubleshooting**

## Technical Details

The XML parser handles two main formats:

1. **Invoke format**: `<invoke name="shell"><parameter name="args">{"command": "ls"}</parameter></invoke>`
2. **Tool format**: `<tool name="shell" command="ls -la"/>`

The parser:
- Extracts tool names from XML attributes
- Parses arguments from JSON content within XML
- Falls back to simple text extraction if JSON parsing fails
- Validates tool calls before returning them

## Testing

The fix was tested with:
- ✅ E2E tests pass showing tool execution is working
- ✅ Build succeeds without errors
- ✅ XML parsing test cases added to verify functionality

## Result

The tool argument parsing issue should now be resolved. The G3 agent can properly handle:
- JSON format tool calls (existing functionality)
- XML format tool calls (new functionality)
- Proper argument extraction and validation

## Monitoring

To verify the fix is working, users can:
1. Run simple tool commands and verify arguments are parsed correctly
2. Check debug logs for XML parsing activity
3. Monitor for "Missing command argument" errors (should be reduced/eliminated)

## Files Modified

- `/home/clauderun/g3-vps-friendly/crates/g3-core/src/streaming_parser.rs` - Main XML parsing implementation
- `/home/clauderun/g3-vps-friendly/crates/g3-core/src/tool_dispatch.rs` - Enhanced validation
- `/home/clauderun/g3-vps-friendly/crates/g3-core/src/lib.rs` - Improved debug logging

The fix ensures that tool calls are properly parsed regardless of whether they're generated in JSON or XML format, resolving the argument parsing issues that were causing tool execution failures.