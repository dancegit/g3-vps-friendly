#[cfg(test)]
mod tests {
    use super::computer_control::{ChromeDriver, WebDriverController};
    use anyhow::Result;

    #[tokio::test]
    #[ignore] // This test requires ChromeDriver to be running
    async fn test_chrome_driver_integration() -> Result<()> {
        // This test assumes ChromeDriver is running on port 9515
        let mut driver = ChromeDriver::with_port_headless(9515).await?;
        
        // Navigate to a test page
        driver.navigate("https://example.com").await?;
        
        // Get page info
        let title = driver.title().await?;
        assert_eq!(title, "Example Domain");
        
        let url = driver.current_url().await?;
        assert!(url.contains("example.com"));
        
        // Find and interact with elements
        let h1_element = driver.find_element("h1").await?;
        let h1_text = h1_element.text().await?;
        assert!(h1_text.contains("Example Domain"));
        
        // Test navigation
        driver.back().await?;
        driver.forward().await?;
        driver.refresh().await?;
        
        // Take screenshot
        driver.screenshot("/tmp/g3-webdriver-test.png").await?;
        
        // Clean up
        driver.quit().await?;
        
        Ok(())
    }
}