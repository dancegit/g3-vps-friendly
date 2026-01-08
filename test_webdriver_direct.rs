// Direct test of G3's WebDriver functionality
use g3_core::computer_control::{ChromeDriver, WebDriverController};
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    println!("Testing G3 WebDriver integration directly...");
    
    // Test ChromeDriver connection using G3's implementation
    match test_g3_chrome_driver().await {
        Ok(_) => println!("✅ G3 WebDriver test successful!"),
        Err(e) => println!("❌ G3 WebDriver test failed: {}", e),
    }
    
    Ok(())
}

async fn test_g3_chrome_driver() -> Result<()> {
    println!("Connecting to ChromeDriver on port 9515 using G3 implementation...");
    
    // Use G3's ChromeDriver implementation
    let mut driver = ChromeDriver::with_port_headless(9515).await?;
    
    println!("✅ Connected to ChromeDriver with G3 implementation!");
    
    println!("Navigating to example.com...");
    driver.navigate("https://example.com").await?;
    
    let title = driver.title().await?;
    println!("Page title: {}", title);
    
    let url = driver.current_url().await?;
    println!("Current URL: {}", url);
    
    println!("Finding page elements...");
    let mut h1_element = driver.find_element("h1").await?;
    let h1_text = h1_element.text().await?;
    println!("H1 text: {}", h1_text);
    
    println!("Taking screenshot...");
    driver.screenshot("/tmp/g3-webdriver-test-screenshot.png").await?;
    println!("Screenshot saved to: /tmp/g3-webdriver-test-screenshot.png");
    
    println!("Testing navigation...");
    driver.back().await?;
    println!("✅ Back navigation successful");
    
    driver.forward().await?;
    println!("✅ Forward navigation successful");
    
    driver.refresh().await?;
    println!("✅ Page refresh successful");
    
    println!("Closing browser...");
    driver.quit().await?;
    
    Ok(())
}