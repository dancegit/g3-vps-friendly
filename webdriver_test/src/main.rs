use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    println!("Testing WebDriver functionality...");
    
    // Test ChromeDriver connection
    match test_chrome_driver().await {
        Ok(_) => println!("✅ ChromeDriver test successful!"),
        Err(e) => println!("❌ ChromeDriver test failed: {}", e),
    }
    
    Ok(())
}

async fn test_chrome_driver() -> Result<()> {
    use fantoccini::{ClientBuilder, Locator};
    
    println!("Connecting to ChromeDriver on port 9515...");
    
    let mut caps = serde_json::Map::new();
    caps.insert(
        "browserName".to_string(),
        serde_json::Value::String("chrome".to_string()),
    );

    // Set up Chrome options for headless mode
    let mut chrome_options = serde_json::Map::new();
    chrome_options.insert(
        "args".to_string(),
        serde_json::Value::Array(vec![
            serde_json::Value::String("--headless=new".to_string()),
            serde_json::Value::String("--disable-gpu".to_string()),
            serde_json::Value::String("--no-sandbox".to_string()),
            serde_json::Value::String("--disable-dev-shm-usage".to_string()),
            serde_json::Value::String("--window-size=1920,1080".to_string()),
        ]),
    );

    caps.insert(
        "goog:chromeOptions".to_string(),
        serde_json::Value::Object(chrome_options),
    );

    let client = ClientBuilder::native()
        .capabilities(caps)
        .connect("http://localhost:9515")
        .await?;

    println!("✅ Connected to ChromeDriver!");
    
    println!("Navigating to example.com...");
    client.goto("https://example.com").await?;
    
    let title = client.title().await?;
    println!("Page title: {}", title);
    
    let url = client.current_url().await?;
    println!("Current URL: {}", url);
    
    println!("Finding page elements...");
    let h1_element = client.find(Locator::Css("h1")).await?;
    let h1_text = h1_element.text().await?;
    println!("H1 text: {}", h1_text);
    
    println!("Taking screenshot...");
    let screenshot = client.screenshot().await?;
    let screenshot_path = "/tmp/webdriver-test-screenshot.png";
    std::fs::write(screenshot_path, screenshot)?;
    println!("Screenshot saved to: {}", screenshot_path);
    
    println!("Closing browser...");
    client.close().await?;
    
    Ok(())
}