# XML Tool Support Implementation Plan

## Problem Statement

G3 currently has a **dual execution path issue**:

1. **Expected Path**: JSON tool calls → Streaming Parser → Tool Dispatch → Execution
2. **Actual Path**: XML tool calls → ??? → Direct g3-execution → Output

The localhost:9000 load balancer outputs XML format, but G3's streaming parser only looks for JSON. This causes:
- Tool dispatch system to be bypassed
- Inconsistent execution behavior
- Debugging difficulties
- Unclear execution flow

## Root Cause

**Format Mismatch**: localhost:9000 outputs XML-like tool calls:
```xml
<invoke_tool_call>
<tool name="shell" args="{\"command\": \"echo test\"}"/>
</invoke_tool_call>
```

**But streaming parser expects JSON:**
```json
{"tool": "shell", "args": {"command": "echo test"}}
```

## Solution Strategy

### Phase 1: Add XML Tool Call Support
1. **Extend Streaming Parser**: Add XML parsing alongside JSON
2. **Format Detection**: Auto-detect XML vs JSON
3. **Unified Output**: Convert both formats to internal ToolCall structure
4. **Backward Compatibility**: Ensure JSON continues to work

### Phase 2: Standardize Execution Path
1. **Single Execution Flow**: Ensure all tool calls go through dispatch system
2. **Comprehensive Logging**: Add debug logs throughout pipeline
3. **Provider Consistency**: Same behavior for all providers
4. **Debug Visibility**: Clear execution path tracing

### Phase 3: Testing & Validation
1. **Format Testing**: Test both XML and JSON formats
2. **Provider Testing**: Test with different providers
3. **Debug Verification**: Ensure logs show complete flow
4. **Performance Testing**: No performance regression

## Implementation Details

### 1. Extend Streaming Parser

**File**: `crates/g3-core/src/streaming_parser.rs`

```rust
// Add XML pattern detection
const XML_TOOL_PATTERNS: [&str; 3] = [
    r#"<invoke_tool_call>"#,
    r#"<tool name="#,
    r#"<parameter name="#,
];

// Add XML parsing function
fn try_parse_xml_tool_calls_from_text(&self, text: &str) -> Vec<ToolCall> {
    // Parse XML format and convert to ToolCall
}

// Modify process_chunk to check both formats
pub fn process_chunk(&mut self, chunk: &g3_providers::CompletionChunk) -> Vec<ToolCall> {
    // ... existing JSON logic ...
    
    // Add XML parsing
    if !chunk.content.is_empty() {
        let xml_tools = self.try_parse_xml_tool_calls_from_text(&chunk.content);
        if !xml_tools.is_empty() {
            debug!("Found {} XML tool calls in chunk content", xml_tools.len());
            completed_tools.extend(xml_tools);
        }
    }
}
```

### 2. XML Parser Implementation

```rust
impl StreamingToolParser {
    /// Parse XML-style tool calls and convert to internal format
    fn try_parse_xml_tool_calls_from_text(&self, text: &str) -> Vec<ToolCall> {
        let mut tools = Vec::new();
        
        // Look for XML tool call patterns
        if let Some(start) = text.find("<invoke_tool_call>") {
            if let Some(end) = text.find("</invoke_tool_call>") {
                let xml_content = &text[start..end + "</invoke_tool_call>".len()];
                
                // Parse individual tool calls within the XML
                if let Some(tool_start) = xml_content.find("<tool name=") {
                    if let Ok(tool_call) = self.parse_xml_tool_call(xml_content) {
                        tools.push(tool_call);
                    }
                }
            }
        }
        
        tools
    }
    
    /// Parse individual XML tool call
    fn parse_xml_tool_call(&self, xml_content: &str) -> Result<ToolCall, Box<dyn std::error::Error>> {
        // Extract tool name
        let name_regex = regex::Regex::new(r#"name="([^"]+)""#)?;
        let tool_name = name_regex.captures(xml_content)
            .and_then(|cap| cap.get(1))
            .map(|m| m.as_str().to_string())
            .ok_or("No tool name found")?;
        
        // Extract arguments (usually in JSON format within XML)
        let args_regex = regex::Regex::new(r#"args="([^"]+)""#)?;
        let args_json = args_regex.captures(xml_content)
            .and_then(|cap| cap.get(1))
            .map(|m| m.as_str())
            .ok_or("No args found")?;
        
        // Parse JSON arguments
        let args: serde_json::Value = serde_json::from_str(args_json)?;
        
        Ok(ToolCall {
            tool: tool_name,
            args,
        })
    }
}
```

### 3. Enhanced Debug Logging

**Add comprehensive logging throughout the pipeline:**

```rust
// In streaming_parser.rs
eprintln!("🔍 STREAMING_PARSER: Found {} XML tool calls", xml_tools.len());

// In tool_dispatch.rs  
eprintln!("🔍 TOOL_DISPATCH: Dispatching tool '{}'", tool_call.tool);

// In shell.rs
eprintln!("🔍 SHELL_TOOL: Executing command '{}'", command);
eprintln!("🔍 SHELL_TOOL: Command completed with success={}", result.success);
```

### 4. Format Detection and Auto-Selection

```rust
/// Detect whether content contains JSON or XML tool calls
fn detect_tool_call_format(text: &str) -> ToolCallFormat {
    if text.contains("{\"tool\":") || text.contains("{ \"tool\":") {
        ToolCallFormat::Json
    } else if text.contains("<invoke_tool_call>") || text.contains("<tool name=") {
        ToolCallFormat::Xml
    } else {
        ToolCallFormat::None
    }
}
```

## Testing Strategy

### 1. Unit Tests
```rust
#[test]
fn test_xml_tool_call_parsing() {
    let xml = r#"<invoke_tool_call><tool name="shell" args="{\"command\": \"echo test\"}"/></invoke_tool_call>"#;
    let tools = parser.try_parse_xml_tool_calls_from_text(xml);
    assert_eq!(tools.len(), 1);
    assert_eq!(tools[0].tool, "shell");
}

#[test]
fn test_json_tool_call_parsing() {
    let json = r#"{"tool": "shell", "args": {"command": "echo test"}}"#;
    let tools = parser.try_parse_json_tool_calls_from_text(json);
    assert_eq!(tools.len(), 1);
    assert_eq!(tools[0].tool, "shell");
}
```

### 2. Integration Tests
```bash
# Test XML format
RUST_LOG=debug g3 --config test.toml --quiet 'execute "echo XML_TEST"' 2>&1 | grep -E "(XML|JSON|TOOL_DISPATCH|SHELL_TOOL)"

# Test JSON format  
RUST_LOG=debug g3 --config test.toml --quiet 'execute "echo JSON_TEST"' 2>&1 | grep -E "(XML|JSON|TOOL_DISPATCH|SHELL_TOOL)"
```

### 3. Provider Testing
- Test with localhost:9000 (current issue)
- Test with direct Anthropic API
- Test with other providers
- Ensure consistent behavior

## Success Criteria

1. **XML Parsing Works**: XML tool calls are correctly parsed
2. **JSON Still Works**: Existing JSON parsing continues to work
3. **Debug Logs Visible**: Complete execution path is traceable
4. **Single Execution Path**: All tool calls go through dispatch system
5. **Provider Consistency**: Same behavior across providers

## Timeline

### Week 1: Research & Design
- [ ] Complete XML format research
- [ ] Design parsing implementation
- [ ] Plan testing strategy

### Week 2: Implementation  
- [ ] Implement XML parsing in streaming parser
- [ ] Add comprehensive debug logging
- [ ] Write unit tests

### Week 3: Testing & Refinement
- [ ] Integration testing
- [ ] Provider testing
- [ ] Debug and fix issues

### Week 4: Validation & Documentation
- [ ] Final testing
- [ ] Documentation updates
- [ ] Performance validation

## Risk Mitigation

1. **Backward Compatibility**: Ensure JSON parsing still works
2. **Performance**: XML parsing shouldn't slow down execution
3. **Accuracy**: XML parsing should be as reliable as JSON
4. **Debugging**: Comprehensive logging for troubleshooting
5. **Testing**: Thorough testing across formats and providers