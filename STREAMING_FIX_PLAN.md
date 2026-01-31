# Anthropic Load Balancer - Streaming Implementation Fix Plan

## Problem Analysis

The current implementation has a **circular dependency issue** in streaming responses:

1. **API Server** (`_create_streaming_generator`): Returns hardcoded placeholder text instead of actual streaming data
2. **MiniMax Provider** (`_handle_stream_response`): Returns `None` expecting the API server to handle streaming
3. **Result**: Neither layer implements actual streaming, causing placeholder responses

## Current Broken Flow

```
G3 Request → API Server → Provider Manager → MiniMax Provider
                ↓                           ↓
        "Streaming response would be here"    None
```

## Root Cause

- **Line 559-565** in `/home/clauderun/anthropic_loadbalancer/src/loadbalancer/api_server.py`: Hardcoded placeholder response
- **Line 267** in `/home/clauderun/anthropic_loadbalancer/src/loadbalancer/providers/minimax_provider.py`: Returns `None` instead of AsyncGenerator
- **Line 203**: Uses `await` on AsyncGenerator (incorrect)

## Solution Architecture

### Option 1: Fix Provider Streaming (Recommended)
Implement proper streaming in the MiniMax provider and return AsyncGenerator directly to API server.

### Option 2: Fix API Server Streaming  
Implement streaming logic in API server and have providers return raw response data.

### Option 3: Hybrid Approach
Providers handle low-level streaming, API server handles SSE formatting.

## Implementation Plan - Option 1 (Provider Fix)

### Step 1: Fix MiniMax Provider Streaming

**File**: `/home/clauderun/anthropic_loadbalancer/src/loadbalancer/providers/minimax_provider.py`

1. **Fix `_handle_stream_response` function**:
   - Change return type from `Optional[Dict[str, Any]]` to `AsyncGenerator[str, None]`
   - Implement actual streaming response processing
   - Format chunks as Server-Sent Events (SSE)

2. **Fix `create_message` function**:
   - Remove `await` from `self._handle_stream_response(response)` call
   - Return AsyncGenerator directly for streaming requests

### Step 2: Update API Server (Minimal Changes)

**File**: `/home/clauderun/anthropic_loadbalancer/src/loadbalancer/api_server.py`

1. **Fix `_create_streaming_generator` function**:
   - Remove hardcoded placeholder response
   - Properly handle AsyncGenerator from providers
   - Add error handling for streaming failures

### Step 3: Test Implementation

1. **Unit Tests**: Verify streaming works with curl
2. **Integration Tests**: Test with G3 configuration
3. **Load Tests**: Ensure streaming doesn't break under load

## Detailed Implementation

### Code Changes Required

#### 1. MiniMax Provider - `_handle_stream_response`

```python
async def _handle_stream_response(self, response) -> AsyncGenerator[str, None]:
    """Handle streaming response from MiniMax API.
    
    Args:
        response: aiohttp response object
        
    Yields:
        Server-sent events formatted chunks
    """
    try:
        # Process the streaming response
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                # Already properly formatted SSE data
                yield line + '\n'
            elif line == '':
                # Empty line, skip
                continue
            elif line == '[DONE]':
                # End of stream marker
                yield 'data: [DONE]\n\n'
                break
            else:
                # Raw data, wrap in SSE format
                if line != '[DONE]':
                    yield f'data: {line}\n\n'
                else:
                    yield 'data: [DONE]\n\n'
                    break
    except Exception as e:
        logger.error(f"Error processing streaming response: {e}")
        yield f'data: {{"error": "{str(e)}"}}\n\n'
```

#### 2. MiniMax Provider - `create_message` fix

```python
# Change this line:
return await self._handle_stream_response(response)

# To this:
return self._handle_stream_response(response)
```

#### 3. API Server - `_create_streaming_generator`

```python
# Replace placeholder logic with:
if hasattr(response, '__aiter__'):
    # response is an AsyncGenerator - stream the actual content
    async for chunk in response:
        if isinstance(chunk, str):
            yield chunk  # Already formatted SSE data
        else:
            yield f"data: {json.dumps(chunk)}\n\n"
else:
    logger.warning("Provider returned non-streaming response for streaming request")
    yield f"data: {json.dumps(response)}\n\n"
    yield "data: [DONE]\n\n"
```

## Testing Strategy

### 1. Direct API Test
```bash
# Test streaming endpoint
curl -X POST http://localhost:9000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: fake-key" \
  -H "anthropic-version: 2023-06-01" \
  -H "Accept: text/event-stream" \
  -d '{
    "model": "minimax",
    "max_tokens": 100,
    "stream": true,
    "messages": [{"role": "user", "content": "What is 2+2?"}]
  }'
```

### 2. G3 Integration Test
```bash
# Test with G3
echo "What is 2+2?" | g3
```

### 3. Complex Query Test
```bash
# Test with deployment query
echo "Help me deploy a web application using Dokploy" | g3
```

## Success Criteria

✅ **Streaming responses return actual AI content instead of placeholder text**  
✅ **G3 receives proper streaming responses from localhost:9000**  
✅ **No "Streaming response would be here" placeholder responses**  
✅ **All existing functionality remains intact**  
✅ **Error handling works for failed requests**  

## Rollback Plan

If issues arise:
1. **Backup current files** before making changes
2. **Use git to revert changes** if needed
3. **Alternative**: Disable streaming in G3 config as temporary workaround

## Alternative Solution (Quick Fix)

If the provider fix is too complex, disable streaming in G3:

```toml
[agent]
enable_streaming = false  # Use non-streaming mode
```

This will make G3 use regular HTTP requests instead of streaming, which should work with the current load balancer implementation.

## Next Steps

1. **Review this plan** and confirm approach
2. **Implement the code changes** 
3. **Test the fix** with curl and G3
4. **Verify websocket issues** are resolved
5. **Document any additional findings**

---

**Status**: Ready for implementation  
**Priority**: High (blocking G3 functionality)  
**Estimated Time**: 1-2 hours for implementation and testing