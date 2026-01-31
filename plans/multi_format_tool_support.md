# Multi-Format Tool Support Implementation Plan

## Problem Scope

The current implementation only handles one specific XML format, but we need to support:
1. **JSON format** (existing): `{"tool": "shell", "args": {"command": "echo test"}}`
2. **XML Format 1** (current): `<invoke name="shell"><parameter name="args">{"command": "echo test"}</parameter></invoke>`
3. **XML Format 2** (Anthropic-style): `<tool_use><name>shell</name><input>{"command": "echo test"}</input></tool_use>`
4. **XML Format 3** (OpenAI-style): `<function_call><name>shell</name><arguments>{"command": "echo test"}</arguments></function_call>`
5. **Mixed formats**: Providers that switch between formats
6. **Nested XML**: Complex XML structures with multiple tool calls

## Multi-Format Architecture

### 1. Format Detection System
```rust
enum ToolCallFormat {
    Json,
    XmlInvoke,      // <invoke name="...">
    XmlToolUse,     // <tool_use><name>...</name>
    XmlFunctionCall,// <function_call><name>...</name>
    XmlGeneric,     // <tool name="..." args="...">
    Unknown,
}

impl StreamingToolParser {
    fn detect_format(&self, text: &str) -> ToolCallFormat {
        // Priority order: Check most specific formats first
        if self.contains_xml_tool_use(text) {
            ToolCallFormat::XmlToolUse
        } else if self.contains_xml_function_call(text) {
            ToolCallFormat::XmlFunctionCall
        } else if self.contains_xml_invoke(text) {
            ToolCallFormat::XmlInvoke
        } else if self.contains_json_tool_call(text) {
            ToolCallFormat::Json
        } else {
            ToolCallFormat::Unknown
        }
    }
}
```

### 2. Multi-Format Parser
```rust
impl StreamingToolParser {
    pub fn parse_tool_calls(&self, text: &str) -> Vec<ToolCall> {
        let format = self.detect_format(text);
        
        match format {
            ToolCallFormat::Json => self.parse_json_tool_calls(text),
            ToolCallFormat::XmlInvoke => self.parse_xml_invoke_calls(text),
            ToolCallFormat::XmlToolUse => self.parse_xml_tool_use_calls(text),
            ToolCallFormat::XmlFunctionCall => self.parse_xml_function_calls(text),
            _ => self.parse_generic_tool_calls(text),
        }
    }
}
```

### 3. Robust XML Parsing
```rust
// Support multiple XML formats
fn parse_xml_invoke_calls(&self, text: &str) -> Vec<ToolCall> {
    // Pattern 1: <invoke name="shell"><parameter name="args">{...}</parameter></invoke>
    // Pattern 2: <invoke><tool name="shell">...</tool></invoke>
    // Pattern 3: <invoke name="shell" args="{...}"/>
}

fn parse_xml_tool_use_calls(&self, text: &str) -> Vec<ToolCall> {
    // Pattern: <tool_use><name>shell</name><input>{"command": "echo test"}</input></tool_use>
}

fn parse_xml_function_calls(&self, text: &str) -> Vec<ToolCall> {
    // Pattern: <function_call><name>shell</name><arguments>{"command": "echo test"}</arguments></function_call>
}
```

## Implementation Strategy

### Phase 1: Format Detection
1. **Pattern Recognition**: Multiple regex patterns for different formats
2. **Confidence Scoring**: Rate confidence for each format detection
3. **Fallback Chain**: Try formats in order of confidence
4. **Format Caching**: Remember format for consistent parsing

### Phase 2: Robust Parsing
1. **Error Recovery**: Continue parsing even if one format fails
2. **Partial Parsing**: Handle incomplete tool calls gracefully
3. **Multiple Tools**: Parse multiple tool calls in single response
4. **Nested Structures**: Handle complex nested XML

### Phase 3: Validation & Testing
1. **Format Validation**: Ensure parsed tool calls are valid
2. **Argument Validation**: Validate JSON arguments structure
3. **Tool Name Validation**: Ensure tool names are recognized
4. **Comprehensive Testing**: Test all format combinations

## Enhanced XML Support

### 1. Multiple XML Patterns
```rust
// Support various XML formats
const XML_PATTERNS: &[&str] = &[
    r#"<invoke[^>]*name="([^"]+)"[^>]*>"#,           // <invoke name="shell">
    r#"<tool[^>]*name="([^"]+)"[^>]*>"#,             // <tool name="shell">
    r#"<tool_use>"#,                                  // <tool_use>
    r#"<function_call>"#,                             // <function_call>
    r#"<invoke_tool_call>"#,                           // <invoke_tool_call>
];
```

### 2. Flexible Argument Extraction
```rust
fn extract_xml_arguments(&self, xml_content: &str) -> Result<serde_json::Value, Box<dyn Error>> {
    // Try multiple argument extraction patterns
    
    // Pattern 1: <parameter name="args">{json}</parameter>
    if let Some(json) = self.extract_parameter_args(xml_content) {
        return serde_json::from_str(json);
    }
    
    // Pattern 2: <input>{json}</input>
    if let Some(json) = self.extract_input_content(xml_content) {
        return serde_json::from_str(json);
    }
    
    // Pattern 3: <arguments>{json}</arguments>
    if let Some(json) = self.extract_arguments_content(xml_content) {
        return serde_json::from_str(json);
    }
    
    // Pattern 4: args="{json}" attribute
    if let Some(json) = self.extract_args_attribute(xml_content) {
        return serde_json::from_str(json);
    }
    
    Err("Could not extract arguments from XML".into())
}
```

### 3. Robust Error Handling
```rust
fn parse_xml_tool_calls(&self, text: &str) -> Vec<ToolCall> {
    let mut tools = Vec::new();
    let mut remaining_text = text;
    
    while !remaining_text.is_empty() {
        match self.try_parse_next_xml_tool(remaining_text) {
            Ok((tool, next_pos)) => {
                tools.push(tool);
                remaining_text = &remaining_text[next_pos..];
            }
            Err(e) => {
                debug!("XML parsing error: {}", e);
                // Try to skip to next potential tool call
                if let Some(next_pos) = self.find_next_xml_pattern(remaining_text) {
                    remaining_text = &remaining_text[next_pos..];
                } else {
                    break;
                }
            }
        }
    }
    
    tools
}
```

## Testing Strategy

### 1. Unit Tests for Each Format
```rust
#[test]
fn test_json_tool_parsing() {
    let json = r#"{"tool": "shell", "args": {"command": "echo test"}}"#;
    let tools = parser.parse_json_tool_calls(json);
    assert_eq!(tools.len(), 1);
    assert_eq!(tools[0].tool, "shell");
}

#[test]
fn test_xml_invoke_parsing() {
    let xml = r#"<invoke name="shell"><parameter name="args">{"command": "echo test"}</parameter></invoke>"#;
    let tools = parser.parse_xml_invoke_calls(xml);
    assert_eq!(tools.len(), 1);
    assert_eq!(tools[0].tool, "shell");
}

#[test]
fn test_xml_tool_use_parsing() {
    let xml = r#"<tool_use><name>shell</name><input>{"command": "echo test"}</input></tool_use>"#;
    let tools = parser.parse_xml_tool_use_calls(xml);
    assert_eq!(tools.len(), 1);
    assert_eq!(tools[0].tool, "shell");
}
```

### 2. Integration Tests
```bash
# Test various formats
./test_format.sh json "{\"tool\": \"shell\", \"args\": {\"command\": \"echo test\"}}"
./test_format.sh xml_invoke '<invoke name="shell"><parameter name="args">{"command": "echo test"}</parameter></invoke>'
./test_format.sh xml_tool_use '<tool_use><name>shell</name><input>{"command": "echo test"}</input></tool_use>'
```

### 3. Real-world Testing
- Test with localhost:9000 (current issue)
- Test with direct Anthropic API
- Test with OpenAI API
- Test with various load balancers

## Implementation Plan

### Week 1: Foundation
- [ ] Implement format detection system
- [ ] Add comprehensive XML pattern support
- [ ] Create flexible argument extraction
- [ ] Write unit tests for each format

### Week 2: Integration
- [ ] Integrate multi-format parsing into streaming parser
- [ ] Add format detection to process_chunk
- [ ] Implement buffer-level XML parsing
- [ ] Add fallback chain logic

### Week 3: Testing & Debugging
- [ ] Test with current localhost:9000 issue
- [ ] Test with different providers
- [ ] Add comprehensive debug logging
- [ ] Fix edge cases and errors

### Week 4: Validation & Optimization
- [ ] Performance testing
- [ ] Memory usage optimization
- [ ] Final integration testing
- [ ] Documentation updates

## Success Metrics

1. **Format Coverage**: Support 5+ different tool call formats
2. **Parsing Accuracy**: 99%+ success rate for valid tool calls
3. **Performance**: No significant performance degradation
4. **Provider Compatibility**: Works with all major providers
5. **Debug Visibility**: Clear execution path for all formats

## Risk Mitigation

1. **Backward Compatibility**: JSON format continues to work
2. **Performance**: Efficient parsing algorithms
3. **Memory**: Proper cleanup and no memory leaks
4. **Error Handling**: Graceful degradation on parsing failures
5. **Testing**: Comprehensive test coverage

## Expected Outcome

After implementation:
- **localhost:9000 will work properly** with XML parsing
- **All providers will have consistent behavior**
- **Debug logs will show complete execution path**
- **Tool dispatch system will be properly triggered**
- **Single, clear execution path for all formats**