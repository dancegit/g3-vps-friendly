use std::process::Command;

fn main() {
    println!("Testing g3 tool execution...");
    
    let output = Command::new("./target/release/g3")
        .args(&["--config", "/home/clauderun/.config/g3/config.toml", "execute echo 'test success'"])
        .output();
    
    match output {
        Ok(result) => {
            println!("STDOUT: {}", String::from_utf8_lossy(&result.stdout));
            println!("STDERR: {}", String::from_utf8_lossy(&result.stderr));
            println!("Status: {}", result.status);
        }
        Err(e) => {
            println!("Error: {}", e);
        }
    }
}
