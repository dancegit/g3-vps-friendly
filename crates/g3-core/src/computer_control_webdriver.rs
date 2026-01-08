//! WebDriver-enabled implementation of computer control functionality for headless environments.
//!
//! This module provides real WebDriver functionality for browser automation while
//! stubbing out GUI/OCR operations that require native libraries.

use anyhow::{Context, Result};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use fantoccini::{Client, ClientBuilder};
use std::time::Duration;

// Re-export types that are used in the API
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct Rect {
    pub x: i32,
    pub y: i32,
    pub width: i32,
    pub height: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextLocation {
    pub text: String,
    pub x: i32,
    pub y: i32,
    pub width: i32,
    pub height: i32,
    pub confidence: f32,
}

/// WebDriver controller trait
#[async_trait]
pub trait WebDriverController: Send + Sync + Sized {
    /// Navigate to a URL
    async fn navigate(&mut self, url: &str) -> Result<()>;
    
    async fn current_url(&self) -> Result<String>;
    
    async fn title(&self) -> Result<String>;
    
    async fn find_element(&mut self, selector: &str) -> Result<WebElement>;
    
    async fn find_elements(&mut self, selector: &str) -> Result<Vec<WebElement>>;
    
    async fn execute_script(&mut self, script: &str, args: Vec<serde_json::Value>) -> Result<serde_json::Value>;
    
    async fn page_source(&self) -> Result<String>;
    
    async fn screenshot(&mut self, path: &str) -> Result<()>;
    
    async fn close(&mut self) -> Result<()>;
    
    async fn quit(mut self) -> Result<()>;
    
    // Additional methods that are used by the WebDriverSession
    async fn back(&mut self) -> Result<()>;
    
    async fn forward(&mut self) -> Result<()>;
    
    async fn refresh(&mut self) -> Result<()>;
}

/// Represents a web element in the DOM
pub struct WebElement {
    inner: fantoccini::elements::Element,
}

impl WebElement {
    pub async fn click(&mut self) -> Result<()> {
        self.inner.click().await?;
        Ok(())
    }
    
    pub async fn send_keys(&mut self, keys: &str) -> Result<()> {
        self.inner.send_keys(keys).await?;
        Ok(())
    }
    
    pub async fn text(&self) -> Result<String> {
        Ok(self.inner.text().await?)
    }
    
    pub async fn get_text(&self) -> Result<String> {
        self.text().await
    }
    
    pub async fn clear(&mut self) -> Result<()> {
        self.inner.clear().await?;
        Ok(())
    }
    
    pub async fn get_attribute(&self, name: &str) -> Result<Option<String>> {
        Ok(self.inner.attr(name).await?)
    }
    
    pub async fn screenshot(&self, path: &str) -> Result<()> {
        let png_data = self.inner.screenshot().await?;
        std::fs::write(path, png_data)?;
        Ok(())
    }
}

/// Computer controller trait - stubbed for headless environment
#[async_trait]
pub trait ComputerController: Send + Sync {
    async fn take_screenshot(
        &self,
        _path: &str,
        _region: Option<Rect>,
        _window_id: Option<&str>,
    ) -> Result<()> {
        anyhow::bail!("Screenshot capture not supported in headless environment (use WebDriver screenshot instead)")
    }

    async fn extract_text_from_screen(&self, _region: Rect, _window_id: &str) -> Result<String> {
        anyhow::bail!("OCR not supported in headless environment")
    }
    
    async fn extract_text_from_image(&self, _path: &str) -> Result<String> {
        anyhow::bail!("OCR not supported in headless environment")
    }
    
    async fn extract_text_with_locations(&self, _path: &str) -> Result<Vec<TextLocation>> {
        anyhow::bail!("OCR not supported in headless environment")
    }
    
    async fn find_text_in_app(
        &self,
        _app_name: &str,
        _search_text: &str,
    ) -> Result<Option<TextLocation>> {
        anyhow::bail!("OCR not supported in headless environment")
    }

    fn move_mouse(&self, _x: i32, _y: i32) -> Result<()> {
        anyhow::bail!("Mouse control not supported in headless environment")
    }
    
    fn click_at(&self, _x: i32, _y: i32, _app_name: Option<&str>) -> Result<()> {
        anyhow::bail!("Mouse control not supported in headless environment")
    }
}

/// Chrome WebDriver implementation with headless support
pub struct ChromeDriver {
    client: Client,
}

impl ChromeDriver {
    pub async fn with_port_headless(port: u16) -> Result<Self> {
        Self::with_port_headless_and_binary(port, None).await
    }
    
    pub async fn with_port_headless_and_binary(port: u16, chrome_binary: Option<&str>) -> Result<Self> {
        let url = format!("http://localhost:{}", port);

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
                // Use a unique temp directory to avoid conflicts with running Chrome instances
                serde_json::Value::String(format!("--user-data-dir=/tmp/g3-chrome-{}", std::process::id())),
                serde_json::Value::String("--headless=new".to_string()),
                serde_json::Value::String("--disable-gpu".to_string()),
                serde_json::Value::String("--no-sandbox".to_string()),
                serde_json::Value::String("--disable-dev-shm-usage".to_string()),
                serde_json::Value::String("--window-size=1920,1080".to_string()),
            ]),
        );

        // If a custom Chrome binary is specified, use it
        if let Some(binary) = chrome_binary {
            chrome_options.insert("binary".to_string(), serde_json::Value::String(binary.to_string()));
        }

        caps.insert(
            "goog:chromeOptions".to_string(),
            serde_json::Value::Object(chrome_options),
        );

        // Use a timeout for the connection attempt to avoid hanging indefinitely
        let mut builder = ClientBuilder::native();
        let connect_future = builder
            .capabilities(caps)
            .connect(&url);
        
        let client = tokio::time::timeout(Duration::from_secs(30), connect_future)
            .await
            .context("Connection to ChromeDriver timed out after 30 seconds")?
            .context("Failed to connect to ChromeDriver")?;

        Ok(Self { client })
    }
    
    pub async fn back(&mut self) -> Result<()> {
        self.client.back().await?;
        Ok(())
    }
    
    pub async fn forward(&mut self) -> Result<()> {
        self.client.forward().await?;
        Ok(())
    }
    
    pub async fn refresh(&mut self) -> Result<()> {
        self.client.refresh().await?;
        Ok(())
    }
}

#[async_trait]
impl WebDriverController for ChromeDriver {
    async fn navigate(&mut self, url: &str) -> Result<()> {
        self.client.goto(url).await?;
        Ok(())
    }
    
    async fn current_url(&self) -> Result<String> {
        Ok(self.client.current_url().await?.to_string())
    }
    
    async fn title(&self) -> Result<String> {
        Ok(self.client.title().await?)
    }
    
    async fn find_element(&mut self, selector: &str) -> Result<WebElement> {
        let elem = self.client.find(fantoccini::Locator::Css(selector)).await?;
        Ok(WebElement { inner: elem })
    }
    
    async fn find_elements(&mut self, selector: &str) -> Result<Vec<WebElement>> {
        let elems = self.client.find_all(fantoccini::Locator::Css(selector)).await?;
        Ok(elems.into_iter().map(|inner| WebElement { inner }).collect())
    }
    
    async fn execute_script(&mut self, script: &str, args: Vec<serde_json::Value>) -> Result<serde_json::Value> {
        Ok(self.client.execute(script, args).await?)
    }
    
    async fn page_source(&self) -> Result<String> {
        Ok(self.client.source().await?)
    }
    
    async fn screenshot(&mut self, path: &str) -> Result<()> {
        let png_data = self.client.screenshot().await?;
        std::fs::write(path, png_data)?;
        Ok(())
    }
    
    async fn close(&mut self) -> Result<()> {
        self.client.close_window().await?;
        Ok(())
    }
    
    async fn quit(mut self) -> Result<()> {
        self.client.close().await?;
        Ok(())
    }
    
    async fn back(&mut self) -> Result<()> {
        self.client.back().await?;
        Ok(())
    }
    
    async fn forward(&mut self) -> Result<()> {
        self.client.forward().await?;
        Ok(())
    }
    
    async fn refresh(&mut self) -> Result<()> {
        self.client.refresh().await?;
        Ok(())
    }
}

/// Safari WebDriver implementation - stubbed for Linux
pub struct SafariDriver;

impl SafariDriver {
    pub async fn with_port(_port: u16) -> Result<Self> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    pub async fn back(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    pub async fn forward(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    pub async fn refresh(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
}

#[async_trait]
impl WebDriverController for SafariDriver {
    async fn navigate(&mut self, _url: &str) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn current_url(&self) -> Result<String> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn title(&self) -> Result<String> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn find_element(&mut self, _selector: &str) -> Result<WebElement> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn find_elements(&mut self, _selector: &str) -> Result<Vec<WebElement>> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn execute_script(&mut self, _script: &str, _args: Vec<serde_json::Value>) -> Result<serde_json::Value> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn page_source(&self) -> Result<String> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn screenshot(&mut self, _path: &str) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn close(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn quit(mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn back(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn forward(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
    
    async fn refresh(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver is not available on Linux. Use Chrome WebDriver instead.")
    }
}

/// macOS-specific types (stubs)
pub struct AXApplication;
pub struct AXElement;
pub struct MacAxController;

impl MacAxController {
    pub fn new() -> Result<Self> {
        anyhow::bail!("macOS accessibility not supported on Linux")
    }
}

/// Platform-specific constructor - returns error for all platforms (WebDriver is separate)
pub fn create_controller() -> Result<Box<dyn ComputerController>> {
    anyhow::bail!("Native computer control not supported in headless environment. Use WebDriver for browser automation.")
}

/// WebDriver types for convenience
pub mod types {
    pub use super::{Rect, TextLocation};
}