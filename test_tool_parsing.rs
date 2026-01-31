use serde_json;

#[derive(Debug, serde::Deserialize)]
struct ToolCall {
    tool: String,
    args: serde_json::Value,
}

fn main() {
    // Test different JSON formats that the LLM might generate
    let test_cases = vec![
        r#"{"tool":"shell","args":{"command":"ls -la"}}"#,
        r#"{ "tool":"shell","args":{"command":"ls -la"}}"#,
        r#"{"tool" :"shell","args":{"command":"ls -la"}}"#,
        r#"{ "tool" :"shell","args":{"command":"ls -la"}}"#,
        r#"<invoke name="shell"><parameter name="command">ls -la</parameter></invoke>"#,
        r#"<tool name="shell" command="ls -la"/>"#,
    ];

    for (i, test_case) in test_cases.iter().enumerate() {
        println!("Test case {}: {}", i + 1, test_case);
        match serde_json::from_str::<ToolCall>(test_case) {
            Ok(tool_call) => println!("  ✅ Parsed successfully: {:?}", tool_call),
            Err(e) => println!("  ❌ Failed to parse: {}", e),
        }
        println!();
    }
}