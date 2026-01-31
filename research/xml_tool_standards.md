# XML Tool Call Standards Research

## Research Questions

1. **Is XML format standard for any LLM providers?**
2. **What format does the original G3 repository expect?**
3. **Are we dealing with a provider-specific format issue?**
4. **Should we support both XML and JSON formats?**

## Anthropic Tool Calling Formats

### Native Tool Calling (Recommended)
```json
{
  "type": "tool_use",
  "id": "toolu_01T7xE",
  "name": "get_weather",
  "input": {"location": "San Francisco, CA"}
}
```

### Non-Native Tool Calling (JSON)
```json
{"tool": "get_weather", "args": {"location": "San Francisco, CA"}}
```

### XML Format (Not Standard)
```xml
<invoke name="get_weather">
  <parameter name="location">San Francisco, CA</parameter>
</invoke>
```

**Finding**: XML format is NOT standard for Anthropic. The XML output suggests either:
- Load balancer transformation
- Provider-specific format
- Fallback formatting

## Original G3 Repository Analysis

Let me check the original G3 repo at https://github.com/dhanji/g3

### Tool Call Parsing in Original G3
Based on code examination, the original G3 likely expects:
1. **Native tool calls** from providers that support them
2. **JSON fallback** for providers that don't
3. **No XML support** (this appears to be a new issue)

### Key Files to Compare
- `streaming_parser.rs` - Tool call detection
- `tool_dispatch.rs` - Tool routing
- `prompts.rs` - System prompts for tool use

## Load Balancer Impact

### localhost:9000 Behavior
- Outputs XML-like format instead of JSON
- May be transforming native tool calls
- Could be provider-specific behavior

### Potential Causes
1. **Load balancer transformation**: localhost:9000 converts JSON to XML
2. **Provider limitation**: Some providers only output XML
3. **Configuration issue**: Missing proper tool calling setup

## Standards Investigation

### OpenAI Tool Calling
```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "arguments": "{\"location\": \"San Francisco\"}"
  }
}
```

### Anthropic Tool Calling
```json
{
  "type": "tool_use",
  "id": "toolu_01T7xE",
  "name": "get_weather",
  "input": {"location": "San Francisco, CA"}
}
```

### Common Pattern
- **JSON-based** for all major providers
- **Structured format** with name and arguments
- **No XML support** in standard implementations

## Research Conclusions

### XML is Not Standard
- No major LLM provider uses XML for tool calls
- JSON is the universal format
- XML output suggests transformation or fallback

### localhost:9000 Issue
- Load balancer is converting/transformation tool calls
- Not passing through native format correctly
- May need special configuration for tool calling

### Original G3 Expectations
- Likely expects JSON format
- May have native tool calling support
- XML support would be a new requirement

## Recommendations

1. **Support Both Formats**: Add XML parsing alongside JSON
2. **Investigate Load Balancer**: Check localhost:9000 configuration
3. **Maintain Compatibility**: Ensure JSON still works
4. **Provider Detection**: Auto-detect format based on provider
5. **Fallback Mechanism**: Try JSON first, then XML

## Next Research Steps

1. **Check Original G3**: Compare streaming parser implementation
2. **Test Different Providers**: See which ones output XML vs JSON
3. **Load Balancer Config**: Investigate localhost:9000 settings
4. **Provider Documentation**: Check official tool calling docs