# G3 Tool Execution Streaming Pipeline Bug

## Issue Summary
G3 successfully connects to the load balancer and receives proper Anthropic-format responses with tool calls, but **tool execution hangs at ~6-7% progress** and never completes.

## Root Cause Analysis

### ✅ What's Working
1. **Load Balancer**: Returns proper Anthropic format with tool calls
2. **g3 Connection**: Successfully connects and receives responses  
3. **Response Parsing**: g3 shows thinking about tool usage
4. **Tool Detection**: Anthropic provider detects and creates ToolCall objects
5. **Streaming Pipeline**: Tool calls are created and sent via `make_tool_chunk()`

### ❌ What's Broken
**Tool calls are not being delivered from the provider to the streaming parser.**

The streaming parser expects `chunk.tool_calls` to contain the tool calls, but it's always `None`.

## Technical Details

### Tool Call Flow Analysis
```
1. Load Balancer → Returns Anthropic format with tool_use blocks
2. Anthropic Provider → Detects tool calls, creates ToolCall objects  
3. Anthropic Provider → Sends via make_tool_chunk(current_tool_calls)
4. Streaming Pipeline → ❌ chunk.tool_calls is None
5. Streaming Parser → ❌ Never processes tool calls
6. Tool Execution → ❌ Never happens
```

### Evidence
- Load balancer returns: `"content": [{"type": "tool_use", "id": "call_123", "name": "shell", "input": {"command": "ls"}}]`
- Anthropic provider debug logs show tool calls are detected and created
- No debug message: `"Received native tool calls: {:?}"` from streaming parser
- Tool execution hangs at 6-7% progress with thinking output only

### Code Analysis
**File**: `/home/clauderun/g3-vps-friendly/crates/g3-providers/src/anthropic.rs`

The Anthropic provider correctly:
- Detects `AnthropicContent::ToolUse` blocks
- Creates `ToolCall` objects with `id`, `tool`, `args`
- Sends them via `make_tool_chunk(current_tool_calls.clone())`

**File**: `/home/clauderun/g3-vps-friendly/crates/g3-providers/src/streaming.rs`
```rust
pub fn make_tool_chunk(tool_calls: Vec<ToolCall>) -> CompletionChunk {
    CompletionChunk {
        content: String::new(),
        finished: false,
        usage: None,
        tool_calls: Some(tool_calls),  // ✅ Should be set
    }
}
```

**File**: `/home/clauderun/g3-vps-friendly/crates/g3-core/src/streaming_parser.rs`
```rust
if let Some(ref tool_calls) = chunk.tool_calls {
    debug!("Received native tool calls: {:?}", tool_calls);
    // Convert and return tool calls immediately
    for tool_call in tool_calls {
        let converted_tool = ToolCall {
            tool: tool_call.tool.clone(),
            args: tool_call.args.clone(),
        };
        completed_tools.push(converted_tool);
    }
}
```

## Potential Causes

1. **Channel Communication Break**: The streaming channel between provider and core may be dropping tool call chunks
2. **Stream Processing Issue**: Tool call chunks may not be properly interleaved with text chunks
3. **Timing Issue**: Tool calls may be sent before the stream receiver is ready
4. **Buffer Management**: Incomplete UTF-8 sequences or buffer management may drop tool call data

## Reproduction Steps
```bash
cd /home/clauderun/g3-vps-friendly
./target/release/g3 --config ~/.config/g3/config.toml "execute echo test"
```

**Expected**: Tool execution with "test" output
**Actual**: Hangs at 6-7% with thinking output only

## Impact
- **Critical**: Tool execution is completely broken
- **Scope**: All g3 functionality requiring tools (shell, file ops, etc.)
- **User Experience**: Agent appears to think but never acts

## Next Steps
1. Add comprehensive debug logging to streaming pipeline
2. Verify tool call chunks are being sent/received
3. Check channel communication between provider and core
4. Test with different response formats (streaming vs non-streaming)
5. Validate UTF-8 decoding and buffer management

## Files to Investigate
- `/home/clauderun/g3-vps-friendly/crates/g3-providers/src/anthropic.rs` (streaming response)
- `/home/clauderun/g3-vps-friendly/crates/g3-providers/src/streaming.rs` (chunk creation)
- `/home/clauderun/g3-vps-friendly/crates/g3-core/src/lib.rs` (stream processing)
- `/home/clauderun/g3-vps-friendly/crates/g3-core/src/streaming_parser.rs` (tool call detection)