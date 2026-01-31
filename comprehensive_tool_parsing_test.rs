//! Comprehensive Tool Parsing Test Suite
//! 
//! This test suite covers all possible tool call formats that LLMs might generate,
//! including JSON, XML, and hybrid formats, with various edge cases and malformed inputs.

use g3_core::streaming_parser::StreamingToolParser;
use g3_core::ToolCall;

#[cfg(test)]
mod comprehensive_tests {
    use super::*;

    // Helper function to test XML parsing
    fn test_xml_parsing(xml_content: &str, expected_tool: &str, expected_args_contains: &str) {
        let parser = StreamingToolParser::new();
        let tools = parser.try_parse_xml_tool_calls_from_text(xml_content);
        
        println!("Testing XML: {}", xml_content);
        println!("Found {} tools", tools.len());
        
        if !tools.is_empty() {
            let tool = &tools[0];
            println!("Tool: {}, Args: {:?}", tool.tool, tool.args);
            assert_eq!(tool.tool, expected_tool);
            assert!(tool.args.to_string().contains(expected_args_contains));
        } else {
            panic!("No tools found for XML: {}", xml_content);
        }
    }

    // Helper function to test JSON parsing
    fn test_json_parsing(json_content: &str, expected_tool: &str, expected_args_contains: &str) {
        let mut parser = StreamingToolParser::new();
        let tools = parser.try_parse_json_tool_calls_from_text(json_content);
        
        println!("Testing JSON: {}", json_content);
        println!("Found {} tools", tools.len());
        
        if !tools.is_empty() {
            let tool = &tools[0];
            println!("Tool: {}, Args: {:?}", tool.tool, tool.args);
            assert_eq!(tool.tool, expected_tool);
            assert!(tool.args.to_string().contains(expected_args_contains));
        } else {
            panic!("No tools found for JSON: {}", json_content);
        }
    }

    // Test Case 1: Standard JSON formats
    #[test]
    fn test_standard_json_formats() {
        println!("\n=== Testing Standard JSON Formats ===");
        
        // Basic JSON
        test_json_parsing(
            r#"{"tool":"shell","args":{"command":"ls -la"}}"#,
            "shell",
            "ls -la"
        );
        
        // JSON with spaces
        test_json_parsing(
            r#"{ "tool":"shell","args":{"command":"ls -la"}}"#,
            "shell",
            "ls -la"
        );
        
        // JSON with spaced colon
        test_json_parsing(
            r#"{"tool" :"shell","args":{"command":"ls -la"}}"#,
            "shell",
            "ls -la"
        );
        
        // JSON with both spaces
        test_json_parsing(
            r#"{ "tool" :"shell","args":{"command":"ls -la"}}"#,
            "shell",
            "ls -la"
        );
    }

    // Test Case 2: Standard XML formats
    #[test]
    fn test_standard_xml_formats() {
        println!("\n=== Testing Standard XML Formats ===");
        
        // Basic invoke format
        test_xml_parsing(
            r#"<invoke name="shell"><parameter name="args">{"command": "ls -la"}</parameter></invoke>"#,
            "shell",
            "ls -la"
        );
        
        // Invoke with newlines and spacing
        test_xml_parsing(
            r#"<invoke name="shell">
<parameter name="args">{"command": "ls -la"}</parameter>
</invoke>"#,
            "shell",
            "ls -la"
        );
        
        // Simple tool format
        test_xml_parsing(
            r#"<tool name="shell" command="ls -la"/>"#,
            "shell",
            "ls -la"
        );
        
        // Tool with JSON args
        test_xml_parsing(
            r#"<tool name="read_file" args="{\"file_path\": \"test.txt\"}"/>"#,
            "read_file",
            "test.txt"
        );
    }

    // Test Case 3: XML with whitespace issues (common LLM output)
    #[test]
    fn test_xml_with_whitespace() {
        println!("\n=== Testing XML with Whitespace ===");
        
        // XML with extra spaces in arguments
        test_xml_parsing(
            r#"<invoke name="shell"><parameter name="args"> {"command": "ls -la"} </parameter></invoke>"#,
            "shell",
            "ls -la"
        );
        
        // XML with newlines in arguments
        test_xml_parsing(
            r#"<invoke name="shell">
<parameter name="args">
{"command": "ls -la"}
</parameter>
</invoke>"#,
            "shell",
            "ls -la"
        );
        
        // XML with mixed whitespace
        test_xml_parsing(
            r#"<invoke name="shell">
  <parameter name="args">  {"command": "echo hello"}  </parameter>
</invoke>"#,
            "shell",
            "echo hello"
        );
    }

    // Test Case 4: Non-JSON XML content
    #[test]
    fn test_xml_non_json_content() {
        println!("\n=== Testing XML Non-JSON Content ===");
        
        // Simple command in parameter
        test_xml_parsing(
            r#"<invoke name="shell"><parameter name="args">ls -la</parameter></invoke>"#,
            "shell",
            "ls -la"
        );
        
        // Command with spaces
        test_xml_parsing(
            r#"<invoke name="shell"><parameter name="args">ls -la /home/user</parameter></invoke>"#,
            "shell",
            "ls -la /home/user"
        );
        
        // Multi-line command
        test_xml_parsing(
            r#"<invoke name="shell">
<parameter name="args">ls -la
/home/user</parameter>
</invoke>"#,
            "shell",
            "ls -la /home/user"
        );
    }

    // Test Case 5: Mixed formats in same text
    #[test]
    fn test_mixed_formats() {
        println!("\n=== Testing Mixed Formats ===");
        
        let mut parser = StreamingToolParser::new();
        
        // JSON and XML in same text
        let mixed_text = r#"I'll run a command: {"tool":"shell","args":{"command":"ls"}} and then <invoke name="read_file"><parameter name="args">{"file_path": "test.txt"}</parameter></invoke> for you."#;
        
        let json_tools = parser.try_parse_json_tool_calls_from_text(mixed_text);
        let xml_tools = parser.try_parse_xml_tool_calls_from_text(mixed_text);
        
        println!("Mixed text found {} JSON tools and {} XML tools", json_tools.len(), xml_tools.len());
        
        assert!(json_tools.len() >= 1);
        assert!(xml_tools.len() >= 1);
    }

    // Test Case 6: Malformed inputs
    #[test]
    fn test_malformed_inputs() {
        println!("\n=== Testing Malformed Inputs ===");
        
        // Incomplete JSON
        let mut parser = StreamingToolParser::new();
        let tools = parser.try_parse_json_tool_calls_from_text(r#"{"tool":"shell","args":{"command":"#);
        println!("Incomplete JSON found {} tools", tools.len());
        
        // Incomplete XML
        let parser = StreamingToolParser::new();
        let tools = parser.try_parse_xml_tool_calls_from_text(r#"<invoke name="shell"><parameter name="args">{"command": "ls"}"#);
        println!("Incomplete XML found {} tools", tools.len());
        
        // Invalid JSON in XML
        test_xml_parsing(
            r#"<invoke name="shell"><parameter name="args">{invalid json}</parameter></invoke>"#,
            "shell",
            "{invalid json}"
        );
    }

    // Test Case 7: Different tool types
    #[test]
    fn test_different_tool_types() {
        println!("\n=== Testing Different Tool Types ===");
        
        // File operations
        test_json_parsing(
            r#"{"tool":"read_file","args":{"file_path":"test.txt"}}"#,
            "read_file",
            "test.txt"
        );
        
        test_xml_parsing(
            r#"<invoke name="read_file"><parameter name="args">{"file_path": "test.txt"}</parameter></invoke>"#,
            "read_file",
            "test.txt"
        );
        
        // TODO operations
        test_json_parsing(
            r#"{"tool":"todo_read","args":{}}"#,
            "todo_read",
            "{}"
        );
        
        // Complex shell commands
        test_json_parsing(
            r#"{"tool":"shell","args":{"command":"find . -name '*.rs' | head -5"}}"#,
            "shell",
            "find . -name '*.rs' | head -5"
        );
    }

    // Test Case 8: Streaming parser with chunks
    #[test]
    fn test_streaming_parser_chunks() {
        println!("\n=== Testing Streaming Parser with Chunks ===");
        
        let mut parser = StreamingToolParser::new();
        
        // Simulate streaming chunks
        let chunks = vec![
            "I'll run a command: ",
            "<invoke name=\"shell\">",
            "<parameter name=\"args\">{\"command\": \"ls -la\"}",
            "</parameter></invoke> for you."
        ];
        
        let mut all_tools = Vec::new();
        
        for chunk in chunks {
            let tools = parser.process_chunk(&g3_providers::CompletionChunk {
                content: chunk.to_string(),
                tool_calls: None,
                finished: false,
            });
            all_tools.extend(tools);
        }
        
        // Final chunk
        let final_tools = parser.process_chunk(&g3_providers::CompletionChunk {
            content: String::new(),
            tool_calls: None,
            finished: true,
        });
        all_tools.extend(final_tools);
        
        println!("Streaming parser found {} tools", all_tools.len());
        
        if !all_tools.is_empty() {
            let tool = &all_tools[0];
            println!("Tool: {}, Args: {:?}", tool.tool, tool.args);
            assert_eq!(tool.tool, "shell");
            assert!(tool.args.to_string().contains("ls -la"));
        }
    }

    // Test Case 9: Edge cases with special characters
    #[test]
    fn test_special_characters() {
        println!("\n=== Testing Special Characters ===");
        
        // Commands with quotes
        test_xml_parsing(
            r#"<invoke name="shell"><parameter name="args">{"command": "echo 'Hello World'"}</parameter></invoke>"#,
            "shell",
            "Hello World"
        );
        
        // Commands with backslashes
        test_json_parsing(
            r#"{"tool":"shell","args":{"command":"echo \"Path: /home/user\""}}"#,
            "shell",
            "Path: /home/user"
        );
        
        // File paths with spaces
        test_xml_parsing(
            r#"<invoke name="read_file"><parameter name="args">{"file_path": "/home/user/my file.txt"}</parameter></invoke>"#,
            "read_file",
            "my file.txt"
        );
    }

    // Test Case 10: Real-world problematic patterns
    #[test]
    fn test_problematic_patterns() {
        println!("\n=== Testing Problematic Patterns ===");
        
        // Pattern that caused "Missing command argument" error
        test_xml_parsing(
            r#"<invoke name="shell">
<parameter name="args"> backend/
</parameter>
</invoke>"#,
            "shell",
            "backend/"
        );
        
        // Pattern with extra whitespace
        test_xml_parsing(
            r#"<invoke name="shell">
  <parameter name="args">
    ls -la
  </parameter>
</invoke>"#,
            "shell",
            "ls -la"
        );
        
        // Pattern with mixed content
        let mixed_content = r#"I'll check: <invoke name="shell"><parameter name="args">ls</parameter></invoke> and then read {"tool":"read_file","args":{"file_path":"test.txt"}}"#;
        
        let mut parser = StreamingToolParser::new();
        let xml_tools = parser.try_parse_xml_tool_calls_from_text(mixed_content);
        let json_tools = parser.try_parse_json_tool_calls_from_text(mixed_content);
        
        println!("Mixed content found {} XML tools and {} JSON tools", xml_tools.len(), json_tools.len());
        
        assert!(xml_tools.len() >= 1);
        assert!(json_tools.len() >= 1);
    }

    // Test Case 11: Empty and minimal inputs
    #[test]
    fn test_empty_and_minimal() {
        println!("\n=== Testing Empty and Minimal Inputs ===");
        
        let parser = StreamingToolParser::new();
        
        // Empty string
        let tools = parser.try_parse_xml_tool_calls_from_text("");
        assert_eq!(tools.len(), 0);
        
        // Just tool name
        let tools = parser.try_parse_xml_tool_calls_from_text("shell");
        assert_eq!(tools.len(), 0);
        
        // Incomplete XML
        let tools = parser.try_parse_xml_tool_calls_from_text("<invoke");
        assert_eq!(tools.len(), 0);
        
        // Empty JSON
        let mut parser = StreamingToolParser::new();
        let tools = parser.try_parse_json_tool_calls_from_text("{}");
        assert_eq!(tools.len(), 0);
    }

    // Test Case 12: Performance and stress test
    #[test]
    fn test_performance_stress() {
        println!("\n=== Testing Performance and Stress ===");
        
        let mut parser = StreamingToolParser::new();
        
        // Large text with many tool calls
        let mut large_text = String::new();
        for i in 0..10 {
            large_text.push_str(&format!(r#"Command {}: <invoke name="shell"><parameter name="args">{{"command": "echo {}"}}</parameter></invoke> "#, i, i));
        }
        
        let start = std::time::Instant::now();
        let tools = parser.try_parse_xml_tool_calls_from_text(&large_text);
        let duration = start.elapsed();
        
        println!("Parsed {} tools from large text in {:?}", tools.len(), duration);
        
        assert!(tools.len() >= 5); // Should find most of the tools
        assert!(duration.as_millis() < 100); // Should be fast
    }
}