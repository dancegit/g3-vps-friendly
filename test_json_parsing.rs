#[cfg(test)]
mod tests {
    use crate::ToolCall;
    use serde_json;

    #[test]
    fn test_json_tool_call_parsing() {
        // Test different JSON formats that the LLM might generate
        let test_cases = vec![
            (r#"{"tool":"shell","args":{"command":"ls -la"}}"#, true),
            (r#"{ "tool":"shell","args":{"command":"ls -la"}}"#, true),
            (r#"{"tool" :"shell","args":{"command":"ls -la"}}"#, true),
            (r#"{ "tool" :"shell","args":{"command":"ls -la"}}"#, true),
            (r#"<invoke name="shell"><parameter name="command">ls -la</parameter></invoke>"#, false),
            (r#"<tool name="shell" command="ls -la"/>"#, false),
        ];

        for (i, (test_case, should_parse)) in test_cases.iter().enumerate() {
            println!("Test case {}: {}", i + 1, test_case);
            match serde_json::from_str::<ToolCall>(test_case) {
                Ok(tool_call) => {
                    if *should_parse {
                        println!("  ✅ Parsed successfully: {:?}", tool_call);
                    } else {
                        println!("  ⚠️  Unexpectedly parsed: {:?}", tool_call);
                    }
                },
                Err(e) => {
                    if *should_parse {
                        println!("  ❌ Failed to parse: {}", e);
                    } else {
                        println!("  ✅ Correctly failed to parse: {}", e);
                    }
                }
            }
            println!();
        }
    }

    #[test]
    fn test_find_tool_call_patterns() {
        use super::super::streaming_parser::StreamingToolParser;
        
        let test_text = r#"I need to list files. {"tool":"shell","args":{"command":"ls -la"}} Let me check the directory."#;
        
        // Test finding tool call start
        if let Some(pos) = StreamingToolParser::find_first_tool_call_start(test_text) {
            println!("Found tool call pattern at position: {}", pos);
            let remaining = &test_text[pos..];
            println!("Remaining text: {}", remaining);
            
            // Test finding complete JSON
            if let Some(end_pos) = StreamingToolParser::find_complete_json_object_end(remaining) {
                let json_str = &remaining[..=end_pos];
                println!("Complete JSON: {}", json_str);
                
                match serde_json::from_str::<ToolCall>(json_str) {
                    Ok(tool_call) => println!("Parsed tool call: {:?}", tool_call),
                    Err(e) => println!("Failed to parse: {}", e),
                }
            } else {
                println!("No complete JSON object found");
            }
        } else {
            println!("No tool call pattern found");
        }
    }
}