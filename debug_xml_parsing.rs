// Simple test to debug XML parsing
fn main() {
    // Test case that should work
    let xml1 = r#"<invoke name="shell"><parameter name="args">{"command": "ls"}</parameter></invoke>"#;
    println!("Test 1 - Should work: {}", xml1);
    
    // Test case that might be failing
    let xml2 = r#"<invoke name="shell"><parameter name="args">ls backend/</parameter></invoke>"#;
    println!("Test 2 - Might fail: {}", xml2);
    
    // Test the parsing logic manually
    println!("\nTesting argument extraction logic:");
    
    // Simulate the parsing for xml2
    let xml_str = xml2;
    if let Some(param_start) = xml_str.find('>') {
        println!("Found '>' at position: {}", param_start);
        let content_start = param_start + 1;
        if let Some(param_end) = xml_str[content_start..].find("</") {
            println!("Found '</' at position: {}", param_end);
            let content = &xml_str[content_start..content_start + param_end];
            println!("Extracted content: '{}'", content);
            
            // Try to parse as JSON
            match serde_json::from_str::<serde_json::Value>(content) {
                Ok(json) => println!("Parsed as JSON: {:?}", json),
                Err(e) => {
                    println!("Failed to parse as JSON: {}", e);
                    println!("Would create simple args: {{\"command\": \"{}\"}}", content.trim());
                }
            }
        }
    }
}