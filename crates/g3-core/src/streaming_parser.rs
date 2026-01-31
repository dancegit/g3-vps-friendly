//! Streaming tool parser for processing LLM response chunks.
//!
//! This module handles parsing of tool calls from streaming LLM responses,
//! supporting both native tool calls and JSON-based fallback parsing.

use tracing::debug;

use crate::ToolCall;

/// Patterns used to detect JSON tool calls in text.
/// These cover common whitespace variations in JSON formatting.
const TOOL_CALL_PATTERNS: [&str; 4] = [
    r#"{"tool":"#,
    r#"{ "tool":"#,
    r#"{"tool" :"#,
    r#"{ "tool" :"#,
];

/// Patterns used to detect XML tool calls in text.
const XML_TOOL_CALL_PATTERNS: [&str; 3] = [
    r#"<invoke name="#,
    r#"<invoke>"#,
    r#"<tool name="#,
];

/// Modern streaming tool parser that properly handles native tool calls and SSE chunks.
#[derive(Debug)]
pub struct StreamingToolParser {
    /// Buffer for accumulating text content
    text_buffer: String,
    /// Position in text_buffer up to which tool calls have been consumed/executed.
    /// This prevents has_unexecuted_tool_call() from returning true for already-executed tools.
    last_consumed_position: usize,
    /// Whether we've received a message_stop event
    message_stopped: bool,
    /// Whether we're currently in a JSON tool call (for fallback parsing)
    in_json_tool_call: bool,
    /// Start position of JSON tool call (for fallback parsing)
    json_tool_start: Option<usize>,
}

impl Default for StreamingToolParser {
    fn default() -> Self {
        Self::new()
    }
}

impl StreamingToolParser {
    pub fn new() -> Self {
        Self {
            text_buffer: String::new(),
            last_consumed_position: 0,
            message_stopped: false,
            in_json_tool_call: false,
            json_tool_start: None,
        }
    }

    /// Find the starting position of the last tool call pattern in the given text.
    /// Returns None if no tool call pattern is found.
    fn find_last_tool_call_start(text: &str) -> Option<usize> {
        let mut best_start: Option<usize> = None;
        for pattern in &TOOL_CALL_PATTERNS {
            if let Some(pos) = text.rfind(pattern) {
                if best_start.map_or(true, |best| pos > best) {
                    best_start = Some(pos);
                }
            }
        }
        best_start
    }

    /// Find the starting position of the FIRST tool call pattern in the given text.
    /// Returns None if no tool call pattern is found.
    fn find_first_tool_call_start(text: &str) -> Option<usize> {
        let mut best_start: Option<usize> = None;
        for pattern in &TOOL_CALL_PATTERNS {
            if let Some(pos) = text.find(pattern) {
                if best_start.map_or(true, |best| pos < best) {
                    best_start = Some(pos);
                }
            }
        }
        best_start
    }

    /// Detect malformed tool calls where LLM prose leaked into JSON keys.
    ///
    /// When the LLM "stutters" or mixes formats, it sometimes emits JSON where
    /// the keys are actually fragments of conversational text rather than valid
    /// parameter names. This heuristic catches such cases by looking for:
    /// - Unusually long keys (>100 chars)
    /// - Newlines in keys (never valid in JSON keys)
    /// - Common LLM response phrases that indicate prose, not parameters
    fn args_contain_prose_fragments(args: &serde_json::Map<String, serde_json::Value>) -> bool {
        const PROSE_MARKERS: &[&str] = &[
            "I'll", "Let me", "Here's", "I can", "I need", "First", "Now", "The ",
        ];

        args.keys().any(|key| {
            key.len() > 100
                || key.contains('\n')
                || PROSE_MARKERS.iter().any(|marker| key.contains(marker))
        })
    }

    /// Process a streaming chunk and return completed tool calls if any.
    pub fn process_chunk(&mut self, chunk: &g3_providers::CompletionChunk) -> Vec<ToolCall> {
        let mut completed_tools = Vec::new();

        // Add text content to buffer
        if !chunk.content.is_empty() {
            self.text_buffer.push_str(&chunk.content);
        }

        // Handle native tool calls - return them immediately when received.
        // This allows tools to be executed as soon as they're fully parsed,
        // preventing duplicate tool calls from being accumulated.
        debug!("STREAMING_PARSER: process_chunk called - chunk.tool_calls: {:?}", chunk.tool_calls.is_some());
        if let Some(ref tool_calls) = chunk.tool_calls {
            debug!("STREAMING_PARSER: Received native tool calls: count={}, calls={:?}", tool_calls.len(), tool_calls);

            // Convert and return tool calls immediately
            for (i, tool_call) in tool_calls.iter().enumerate() {
                debug!("STREAMING_PARSER: Processing tool call {} - tool: {}, args: {:?}", i, tool_call.tool, tool_call.args);
                // Validate tool call - skip empty tool names
                if tool_call.tool.is_empty() {
                    debug!("Skipping native tool call with empty tool name");
                    continue;
                }
                
                let converted_tool = ToolCall {
                    tool: tool_call.tool.clone(),
                    args: tool_call.args.clone(),
                };
                debug!("STREAMING_PARSER: Converted tool call {} - tool: {}, args: {:?}", i, converted_tool.tool, converted_tool.args);
                debug!("STREAMING_PARSER: Tool call {} args type: {:?}", i, std::mem::discriminant(&converted_tool.args));
                if let Some(args_obj) = converted_tool.args.as_object() {
                    debug!("STREAMING_PARSER: Tool call {} args keys: {:?}", i, args_obj.keys().collect::<Vec<_>>());
                    for (key, value) in args_obj {
                        debug!("STREAMING_PARSER: Tool call {} - {}: {:?}", i, key, value);
                    }
                }
                completed_tools.push(converted_tool);
            }
            debug!("STREAMING_PARSER: Completed processing {} native tool calls", completed_tools.len());
        } else {
            debug!("STREAMING_PARSER: No native tool calls in chunk");
        }

        // Check if message is finished/stopped
        if chunk.finished {
            self.message_stopped = true;
            debug!("Message finished, processing accumulated tool calls");

            // When stream finishes, find ALL tool calls (JSON and XML) in the accumulated buffer
            if completed_tools.is_empty() && !self.text_buffer.is_empty() {
                // Try XML parsing first
                let xml_tools = self.try_parse_xml_tool_calls_from_text(&self.text_buffer);
                if !xml_tools.is_empty() {
                    debug!(
                        "Found {} XML tool calls in buffer at stream end",
                        xml_tools.len()
                    );
                    completed_tools.extend(xml_tools);
                } else {
                    // Fallback to JSON parsing
                    let all_json_tools = self.try_parse_all_json_tool_calls_from_buffer();
                    if !all_json_tools.is_empty() {
                        debug!(
                            "Found {} JSON tool calls in buffer at stream end",
                            all_json_tools.len()
                        );
                        completed_tools.extend(all_json_tools);
                    }
                }
            }
        }

        // Fallback: Try to parse tool calls (XML first, then JSON) from current chunk content if no native tool calls
        if completed_tools.is_empty() && !chunk.content.is_empty() && !chunk.finished {
            // Try XML parsing first
            let xml_tools = self.try_parse_xml_tool_calls_from_text(&chunk.content);
            if !xml_tools.is_empty() {
                completed_tools.extend(xml_tools);
            } else {
                // Fallback to JSON parsing
                if let Some(json_tool) = self.try_parse_json_tool_call(&chunk.content) {
                    completed_tools.push(json_tool);
                }
            }
        }

        completed_tools
    }

    /// Try to find XML tool calls in the current text buffer.
    fn try_find_xml_tool_call(&self) -> Option<Vec<ToolCall>> {
        // Look for XML patterns in the text buffer
        let xml_tools = self.try_parse_xml_tool_calls_from_text(&self.text_buffer);
        
        if !xml_tools.is_empty() {
            debug!("Found {} XML tool calls", xml_tools.len());
            Some(xml_tools)
        } else {
            None
        }
    }

    /// Fallback method to parse JSON tool calls from text content.
    fn try_parse_json_tool_call(&mut self, _content: &str) -> Option<ToolCall> {
        // Try to find XML tool calls in the text buffer (this is more reliable than chunk-based parsing)
        // Only look for complete XML tool calls that haven't been processed yet
        let current_buffer = &self.text_buffer[self.last_consumed_position..];
        let xml_tools = self.try_parse_xml_tool_calls_from_text(current_buffer);
        
        if !xml_tools.is_empty() {
            debug!("Found {} XML tool calls in fallback parsing", xml_tools.len());
            // Return the first one and mark it as consumed
            if let Some(tool_call) = xml_tools.into_iter().next() {
                // Mark this tool call as consumed by updating the position
                if let Some(pos) = current_buffer.find(&format!("<invoke name=\"{}\"", tool_call.tool)) {
                    self.last_consumed_position = self.text_buffer.len() - current_buffer.len() + pos + 1;
                }
                return Some(tool_call);
            }
        }
        
        // If no XML found, try JSON
        if !self.in_json_tool_call {
            if let Some(pos) = Self::find_last_tool_call_start(&self.text_buffer) {
                debug!("Found JSON tool call pattern at position {}", pos);
                self.in_json_tool_call = true;
                self.json_tool_start = Some(pos);
            }
        }

        // If we're in a JSON tool call, try to find the end and parse it
        if self.in_json_tool_call {
            if let Some(start_pos) = self.json_tool_start {
                let json_text = &self.text_buffer[start_pos..];

                // Try to find a complete JSON object
                if let Some(end_pos) = Self::find_complete_json_object_end(json_text) {
                    let json_str = &json_text[..=end_pos];
                    debug!("Attempting to parse JSON tool call: {}", json_str);

                    // Try to parse as a ToolCall
                    if let Ok(tool_call) = serde_json::from_str::<ToolCall>(json_str) {
                        // Validate tool call - skip empty tool names
                        if tool_call.tool.is_empty() {
                            debug!("Skipping JSON tool call with empty tool name");
                            self.in_json_tool_call = false;
                            self.json_tool_start = None;
                            return None;
                        }
                        
                        // Validate that args is an object with reasonable keys
                        if let Some(args_obj) = tool_call.args.as_object() {
                            if Self::args_contain_prose_fragments(args_obj) {
                                debug!(
                                    "Detected malformed tool call with message-like keys, skipping"
                                );
                                self.in_json_tool_call = false;
                                self.json_tool_start = None;
                                return None;
                            }

                            debug!("Successfully parsed valid JSON tool call: {:?}", tool_call);
                            self.in_json_tool_call = false;
                            self.json_tool_start = None;
                            return Some(tool_call);
                        }
                        debug!("Tool call args is not an object, skipping");
                    } else {
                        debug!("Failed to parse JSON tool call: {}", json_str);
                    }
                    // Reset and continue looking
                    self.in_json_tool_call = false;
                    self.json_tool_start = None;
                }
            }
        }

        None
    }

    /// Parse ALL JSON tool calls from the accumulated text buffer.
    /// This finds all complete tool calls, not just the last one.
    fn try_parse_all_json_tool_calls_from_buffer(&self) -> Vec<ToolCall> {
        let mut tool_calls = Vec::new();
        let mut search_start = 0;

        while search_start < self.text_buffer.len() {
            let search_text = &self.text_buffer[search_start..];

            // Find the next tool call pattern
            if let Some(relative_pos) = Self::find_first_tool_call_start(search_text) {
                let abs_start = search_start + relative_pos;
                let json_text = &self.text_buffer[abs_start..];

                // Try to find a complete JSON object
                if let Some(end_pos) = Self::find_complete_json_object_end(json_text) {
                    let json_str = &json_text[..=end_pos];

                    if let Ok(tool_call) = serde_json::from_str::<ToolCall>(json_str) {
                        // Validate tool call - skip empty tool names
                        if tool_call.tool.is_empty() {
                            debug!("Skipping bulk parsed tool call with empty tool name");
                        } else if let Some(args_obj) = tool_call.args.as_object() {
                            if !Self::args_contain_prose_fragments(args_obj) {
                                debug!(
                                    "Found tool call at position {}: {:?}",
                                    abs_start, tool_call.tool
                                );
                                tool_calls.push(tool_call);
                            }
                        }
                    }
                    // Move past this tool call
                    search_start = abs_start + end_pos + 1;
                } else {
                    // Incomplete JSON, stop searching
                    break;
                }
            } else {
                // No more tool call patterns found
                break;
            }
        }

        tool_calls
    }

    /// Get the accumulated text content (excluding tool calls).
    pub fn get_text_content(&self) -> &str {
        &self.text_buffer
    }

    /// Get content before a specific position (for display purposes).
    pub fn get_content_before_position(&self, pos: usize) -> String {
        if pos <= self.text_buffer.len() {
            self.text_buffer[..pos].to_string()
        } else {
            self.text_buffer.clone()
        }
    }

    /// Check if the message has been stopped/finished.
    pub fn is_message_stopped(&self) -> bool {
        self.message_stopped
    }

    /// Check if the text buffer contains an incomplete JSON tool call.
    /// This detects cases where the LLM started emitting a tool call but the stream ended
    /// before the JSON was complete (truncated output).
    pub fn has_incomplete_tool_call(&self) -> bool {
        // Only check the unconsumed portion of the buffer
        let unchecked_buffer = &self.text_buffer[self.last_consumed_position..];
        if let Some(start_pos) = Self::find_last_tool_call_start(unchecked_buffer) {
            let json_text = &unchecked_buffer[start_pos..];
            // If NOT complete, it's an incomplete tool call
            Self::find_complete_json_object_end(json_text).is_none()
        } else {
            false
        }
    }

    /// Check if the text buffer contains an unexecuted tool call.
    /// This detects cases where the LLM emitted a complete tool call JSON
    /// but it wasn't parsed/executed (e.g., due to parsing issues).
    pub fn has_unexecuted_tool_call(&self) -> bool {
        // Only check the unconsumed portion of the buffer
        let unchecked_buffer = &self.text_buffer[self.last_consumed_position..];
        if let Some(start_pos) = Self::find_last_tool_call_start(unchecked_buffer) {
            let json_text = &unchecked_buffer[start_pos..];
            // If the JSON IS complete, it means there's an unexecuted tool call
            if let Some(json_end) = Self::find_complete_json_object_end(json_text) {
                let json_only = &json_text[..=json_end];
                return serde_json::from_str::<serde_json::Value>(json_only).is_ok();
            }
        }
        false
    }

    /// Mark all tool calls up to the current buffer position as consumed/executed.
    /// This prevents has_unexecuted_tool_call() from returning true for already-executed tools.
    pub fn mark_tool_calls_consumed(&mut self) {
        self.last_consumed_position = self.text_buffer.len();
    }

    /// Find the end position (byte index) of a complete JSON object in the text.
    /// Returns None if no complete JSON object is found.
    pub fn find_complete_json_object_end(text: &str) -> Option<usize> {
        let mut brace_count = 0;
        let mut in_string = false;
        let mut escape_next = false;
        let mut found_start = false;

        for (i, ch) in text.char_indices() {
            if escape_next {
                escape_next = false;
                continue;
            }

            match ch {
                '\\' => escape_next = true,
                '"' if !escape_next => in_string = !in_string,
                '{' if !in_string => {
                    brace_count += 1;
                    found_start = true;
                }
                '}' if !in_string => {
                    brace_count -= 1;
                    if brace_count == 0 && found_start {
                        return Some(i); // Return the byte index of the closing brace
                    }
                }
                _ => {}
            }
        }

        None // No complete JSON object found
    }

    /// Try to parse XML tool calls from text content.
    /// This handles XML format like <invoke name="shell"><parameter name="args">{"command": "ls"}</parameter></invoke>
    pub fn try_parse_xml_tool_calls_from_text(&self, text: &str) -> Vec<ToolCall> {
        let mut tools = Vec::new();
        
        debug!("Trying to parse XML tool calls from text: {}", text);
        
        // Look for XML tool call patterns in the text
        for pattern in XML_TOOL_CALL_PATTERNS.iter() {
            debug!("Looking for XML pattern: {}", pattern);
            let mut start = 0;
            while let Some(pos) = text[start..].find(pattern) {
                debug!("Found XML pattern at position: {}", pos);
                let actual_pos = start + pos;
                
                // Try to find the complete XML element
                if let Some(xml_end) = Self::find_complete_xml_element_end(&text[actual_pos..]) {
                    let xml_str = &text[actual_pos..actual_pos + xml_end];
                    debug!("Found complete XML element: {}", xml_str);
                    
                    if let Some(tool_call) = self.parse_xml_tool_call(xml_str) {
                        debug!("Found XML tool call in text: {:?}", tool_call);
                        tools.push(tool_call);
                    }
                } else {
                    debug!("No complete XML element found");
                }
                
                start = actual_pos + 1;
            }
        }
        
        debug!("XML parsing completed, found {} tools", tools.len());
        tools
    }

    /// Find the end position of a complete XML element.
    fn find_complete_xml_element_end(text: &str) -> Option<usize> {
        // Look for matching closing tag
        if let Some(start_pos) = text.find('<') {
            if let Some(tag_end) = text[start_pos + 1..].find('>') {
                let tag_name_start = start_pos + 1;
                let tag_name_end = tag_end + start_pos + 1;
                let tag_content = &text[tag_name_start..tag_name_end];
                
                // Extract tag name (handle attributes)
                let tag_name: String = tag_content.chars()
                    .take_while(|c| !c.is_whitespace() && *c != '>')
                    .collect();
                
                if !tag_name.starts_with('/') {
                    // Look for closing tag
                    let closing_tag = format!("</{}>", tag_name);
                    if let Some(close_pos) = text.find(&closing_tag) {
                        return Some(close_pos + closing_tag.len());
                    }
                }
            }
        }
        None
    }

    /// Parse an XML tool call into a ToolCall struct.
    fn parse_xml_tool_call(&self, xml_str: &str) -> Option<ToolCall> {
        debug!("parse_xml_tool_call called with: {}", xml_str);
        
        // Try to extract tool name and args from XML
        // Format: <invoke name="shell"><parameter name="args">{"command": "ls"}</parameter></invoke>
        
        // Extract tool name
        let tool_name = if xml_str.contains("<invoke name=") {
            // Extract from <invoke name="toolname">
            if let Some(start) = xml_str.find("name=\"") {
                let start = start + 6; // Skip 'name="'
                if let Some(end) = xml_str[start..].find('"') {
                    xml_str[start..start + end].to_string()
                } else {
                    return None;
                }
            } else {
                return None;
            }
        } else if xml_str.contains("<tool name=") {
            // Extract from <tool name="toolname">
            if let Some(start) = xml_str.find("name=\"") {
                let start = start + 6; // Skip 'name="'
                if let Some(end) = xml_str[start..].find('"') {
                    xml_str[start..start + end].to_string()
                } else {
                    return None;
                }
            } else {
                return None;
            }
        } else {
            return None;
        };
        
        debug!("Extracted tool name: {}", tool_name);
        
        // Look for <parameter name="args"> content specifically
        let args = if let Some(args_param) = xml_str.find(r#"<parameter name="args">"#) {
            let content_start = args_param + r#"<parameter name="args">"#.len();
            if let Some(content_end) = xml_str[content_start..].find(r#"</parameter>"#) {
                let content = &xml_str[content_start..content_start + content_end];
                debug!("Found parameter args content: '{}'", content);
                
                // Clean up whitespace and newlines
                let cleaned_content = content.trim().replace("\n", " ").replace("  ", " ");
                debug!("Cleaned content: '{}'", cleaned_content);
                
                // Try to parse as JSON first
                if let Ok(json_args) = serde_json::from_str::<serde_json::Value>(&cleaned_content) {
                    debug!("Parsed as JSON: {:?}", json_args);
                    json_args
                } else {
                    debug!("Failed to parse as JSON, using content as command");
                    // If not JSON, create a simple args object with command
                    serde_json::json!({
                        "command": cleaned_content.trim()
                    })
                }
            } else {
                debug!("No closing </parameter> tag found");
                serde_json::json!({})
            }
        } else if let Some(simple_content) = xml_str.find('>') {
            // Fallback: look for any content between tags
            let content_start = simple_content + 1;
            if let Some(content_end) = xml_str[content_start..].find("</") {
                let content = &xml_str[content_start..content_start + content_end];
                debug!("Using simple content extraction: '{}'", content);
                
                // Clean up whitespace and newlines
                let cleaned_content = content.trim().replace("\n", " ").replace("  ", " ");
                debug!("Cleaned simple content: '{}'", cleaned_content);
                
                // Try to parse as JSON first
                if let Ok(json_args) = serde_json::from_str::<serde_json::Value>(&cleaned_content) {
                    debug!("Parsed as JSON: {:?}", json_args);
                    json_args
                } else {
                    debug!("Using content as command: '{}'", cleaned_content.trim());
                    serde_json::json!({
                        "command": cleaned_content.trim()
                    })
                }
            } else {
                debug!("No closing tag found in simple extraction");
                serde_json::json!({})
            }
        } else {
            debug!("No content found in XML");
            serde_json::json!({})
        };
        
        debug!("Final args: {:?}", args);
        
        if tool_name.is_empty() {
            None
        } else {
            Some(ToolCall { tool: tool_name, args })
        }
    }

    /// Try to parse JSON tool calls from text content for load balancer compatibility.
    /// This handles cases where native tool calls aren't properly supported.
    pub fn try_parse_json_tool_calls_from_text(&mut self, text: &str) -> Vec<ToolCall> {
        let mut tools = Vec::new();
        
        // Look for JSON tool call patterns in the text
        for pattern in TOOL_CALL_PATTERNS.iter() {
            let mut start = 0;
            while let Some(pos) = text[start..].find(pattern) {
                let actual_pos = start + pos;
                
                // Try to find the complete JSON object starting from this position
                if let Some(json_end) = Self::find_complete_json_object_end(&text[actual_pos..]) {
                    let json_str = &text[actual_pos..actual_pos + json_end + 1];
                    
                    if let Ok(tool_call) = serde_json::from_str::<ToolCall>(json_str) {
                        // Validate tool call - skip empty tool names
                        if tool_call.tool.is_empty() {
                            debug!("Skipping text parsed tool call with empty tool name");
                        } else {
                            debug!("Found JSON tool call in text: {:?}", tool_call);
                            tools.push(tool_call);
                        }
                    }
                }
                
                start = actual_pos + 1;
            }
        }
        
        tools
    }

    /// Reset the parser state for a new message.
    pub fn reset(&mut self) {
        self.text_buffer.clear();
        self.last_consumed_position = 0;
        self.message_stopped = false;
        self.in_json_tool_call = false;
        self.json_tool_start = None;
    }

    /// Get the current text buffer length (for position tracking).
    pub fn text_buffer_len(&self) -> usize {
        self.text_buffer.len()
    }

    /// Check if currently parsing a JSON tool call (for debugging).
    pub fn is_in_json_tool_call(&self) -> bool {
        self.in_json_tool_call
    }

    /// Get the JSON tool start position (for debugging).
    pub fn json_tool_start_position(&self) -> Option<usize> {
        self.json_tool_start
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ToolCall;
    use serde_json;

    #[test]
    fn test_tool_call_json_parsing() {
        // Test the exact format that should work
        let json_str = r#"{"tool":"shell","args":{"command":"ls -la"}}"#;
        
        match serde_json::from_str::<ToolCall>(json_str) {
            Ok(tool_call) => {
                assert_eq!(tool_call.tool, "shell");
                assert!(tool_call.args.is_object());
                if let Some(args_obj) = tool_call.args.as_object() {
                    if let Some(command) = args_obj.get("command").and_then(|v| v.as_str()) {
                        assert_eq!(command, "ls -la");
                    } else {
                        panic!("Missing command argument");
                    }
                } else {
                    panic!("Args is not an object");
                }
            }
            Err(e) => panic!("Failed to parse JSON: {}", e),
        }
    }

    #[test]
    fn test_streaming_parser_with_simple_tool_call() {
        let mut parser = StreamingToolParser::new();
        
        // Simulate a simple tool call being streamed
        let text = r#"Let me run a command: {"tool":"shell","args":{"command":"ls -la"}}"#;
        
        // Process the text as if it came from a chunk
        let tools = parser.try_parse_json_tool_calls_from_text(text);
        
        assert_eq!(tools.len(), 1);
        assert_eq!(tools[0].tool, "shell");
        assert!(tools[0].args.is_object());
    }

    #[test]
    fn test_find_complete_json_object_end_simple() {
        let text = r#"{"tool":"shell","args":{"command":"ls"}}"#;
        assert_eq!(
            StreamingToolParser::find_complete_json_object_end(text),
            Some(text.len() - 1)
        );
    }

    #[test]
    fn test_find_complete_json_object_end_nested() {
        let text = r#"{"tool":"write","args":{"content":"{nested}"}}"#;
        assert_eq!(
            StreamingToolParser::find_complete_json_object_end(text),
            Some(text.len() - 1)
        );
    }

    #[test]
    fn test_find_complete_json_object_end_incomplete() {
        let text = r#"{"tool":"shell","args":{"command":"ls""#;
        assert_eq!(StreamingToolParser::find_complete_json_object_end(text), None);
    }

    #[test]
    fn test_xml_tool_call_parsing() {
        let mut parser = StreamingToolParser::new();
        
        // Test XML format: <invoke name="shell"><parameter name="args">{"command": "ls"}</parameter></invoke>
        let xml_text = r#"I'll run a command: <invoke name="shell"><parameter name="args">{"command": "ls -la"}</parameter></invoke> for you."#;
        
        let tools = parser.try_parse_xml_tool_calls_from_text(xml_text);
        
        assert_eq!(tools.len(), 1);
        assert_eq!(tools[0].tool, "shell");
        assert!(tools[0].args.is_object());
        
        // Test alternative XML format: <tool name="shell" command="ls -la"/>
        let xml_text2 = r#"Let me check: <tool name="shell" command="ls -la"/> the directory."#;
        
        let tools2 = parser.try_parse_xml_tool_calls_from_text(xml_text2);
        
        assert_eq!(tools2.len(), 1);
        assert_eq!(tools2[0].tool, "shell");
    }

    #[test]
    fn test_tool_call_patterns() {
        // Test that all patterns are detected
        assert!(StreamingToolParser::find_first_tool_call_start(r#"{"tool":"test"}"#).is_some());
        assert!(StreamingToolParser::find_first_tool_call_start(r#"{ "tool":"test"}"#).is_some());
        assert!(StreamingToolParser::find_first_tool_call_start(r#"{"tool" :"test"}"#).is_some());
        assert!(StreamingToolParser::find_first_tool_call_start(r#"{ "tool" :"test"}"#).is_some());
    }

    #[test]
    fn test_parser_reset() {
        let mut parser = StreamingToolParser::new();
        parser.text_buffer = "some content".to_string();
        parser.message_stopped = true;
        parser.last_consumed_position = 5;

        parser.reset();

        assert!(parser.text_buffer.is_empty());
        assert!(!parser.message_stopped);
        assert_eq!(parser.last_consumed_position, 0);
    }
}