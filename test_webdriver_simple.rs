use std::process::Command;

fn main() {
    println!("Testing WebDriver setup...");
    
    // Test if chromedriver is available
    match Command::new("chromedriver").arg("--version").output() {
        Ok(output) => {
            let version = String::from_utf8_lossy(&output.stdout);
            println!("✅ ChromeDriver found: {}", version.trim());
        }
        Err(e) => {
            println!("❌ ChromeDriver not found: {}", e);
            return;
        }
    }
    
    // Test if chromium is available
    match Command::new("chromium").arg("--version").output() {
        Ok(output) => {
            let version = String::from_utf8_lossy(&output.stdout);
            println!("✅ Chromium found: {}", version.trim());
        }
        Err(e) => {
            println!("❌ Chromium not found: {}", e);
            return;
        }
    }
    
    println!("✅ WebDriver prerequisites are available!");
    println!("\nTo enable WebDriver in g3, use one of these methods:");
    println!("1. Command line: g3 --webdriver --chrome-headless");
    println!("2. Configuration: Set webdriver.enabled = true in your config file");
}