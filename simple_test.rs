fn main() {
    // Test JSON parsing manually
    let json_str = r#"{"tool":"shell","args":{"command":"ls -la"}}"#;
    
    println!("Testing JSON: {}", json_str);
    
    // Manual JSON validation
    match json_str.find("{"tool":"") {
        Some(pos) => println!("Found tool pattern at position: {}", pos),
        None => println!("Tool pattern not found"),
    }
    
    // Test if it's valid JSON
    match serde_json::from_str::<serde_json::Value>(json_str) {
        Ok(value) => println!("Valid JSON: {:?}", value),
        Err(e) => println!("Invalid JSON: {}", e),
    }
}