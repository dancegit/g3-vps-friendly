use g3_core::streaming_parser::StreamingToolParser;

fn main() {
    println!("Testing XML parsing functionality...");
    
    let parser = StreamingToolParser::new();
    
    // Test XML format that the LLM generates
    let xml_text = r#"I'll run a command: <invoke name="shell"><parameter name="args">{"command": "echo hello"}</parameter></invoke> for you."#;
    
    println!("Input text: {}", xml_text);
    
    let tools = parser.try_parse_xml_tool_calls_from_text(xml_text);
    
    println!("Found {} XML tools", tools.len());
    
    for (i, tool) in tools.iter().enumerate() {
        println!("Tool {}: name={}, args={}", i, tool.tool, tool.args);
    }
    
    // Test JSON format for comparison
    let json_text = r#"I'll run a command: {"tool":"shell","args":{"command":"echo hello"}} for you."#;
    
    println!("\nTesting JSON parsing for comparison...");
    println!("Input text: {}", json_text);
    
    // Note: This method requires &mut self, so we'd need a mutable parser
    // For now, let's just test the XML parsing
}