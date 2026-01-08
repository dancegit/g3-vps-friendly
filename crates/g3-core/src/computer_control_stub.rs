//! Stub implementation of computer control functionality for headless environments.
//!
//! This module provides stub implementations that return "not supported" errors
//! for all computer control operations, allowing the core G3 functionality to
//! compile and run without GUI dependencies.

use anyhow::Result;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};

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
    async fn navigate(&mut self, _url: &str) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn current_url(&self) -> Result<String> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn title(&self) -> Result<String> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn find_element(&mut self, _selector: &str) -> Result<WebElement> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn find_elements(&mut self, _selector: &str) -> Result<Vec<WebElement>> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn execute_script(&mut self, _script: &str, _args: Vec<serde_json::Value>) -> Result<serde_json::Value> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn page_source(&self) -> Result<String> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn screenshot(&mut self, _path: &str) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn close(&mut self) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn quit(mut self) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    // Additional methods that are used by the WebDriverSession
    async fn back(&mut self) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn forward(&mut self) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    async fn refresh(&mut self) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
}

/// Represents a web element in the DOM
pub struct WebElement;

impl WebElement {
    pub async fn click(&mut self) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    pub async fn send_keys(&mut self, _keys: &str) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    pub async fn text(&self) -> Result<String> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    pub async fn get_text(&self) -> Result<String> {
        self.text().await
    }
    
    pub async fn clear(&mut self) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    pub async fn get_attribute(&self, _name: &str) -> Result<Option<String>> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
    
    pub async fn screenshot(&self, _path: &str) -> Result<()> {
        anyhow::bail!("WebDriver not supported in headless environment")
    }
}

/// Computer controller trait
#[async_trait]
pub trait ComputerController: Send + Sync {
    async fn take_screenshot(
        &self,
        _path: &str,
        _region: Option<Rect>,
        _window_id: Option<&str>,
    ) -> Result<()> {
        anyhow::bail!("Computer control not supported in headless environment")
    }

    async fn extract_text_from_screen(&self, _region: Rect, _window_id: &str) -> Result<String> {
        anyhow::bail!("Computer control not supported in headless environment")
    }
    
    async fn extract_text_from_image(&self, _path: &str) -> Result<String> {
        anyhow::bail!("Computer control not supported in headless environment")
    }
    
    async fn extract_text_with_locations(&self, _path: &str) -> Result<Vec<TextLocation>> {
        anyhow::bail!("Computer control not supported in headless environment")
    }
    
    async fn find_text_in_app(
        &self,
        _app_name: &str,
        _search_text: &str,
    ) -> Result<Option<TextLocation>> {
        anyhow::bail!("Computer control not supported in headless environment")
    }

    fn move_mouse(&self, _x: i32, _y: i32) -> Result<()> {
        anyhow::bail!("Computer control not supported in headless environment")
    }
    
    fn click_at(&self, _x: i32, _y: i32, _app_name: Option<&str>) -> Result<()> {
        anyhow::bail!("Computer control not supported in headless environment")
    }
}

/// Safari WebDriver implementation
pub struct SafariDriver;

impl SafariDriver {
    pub async fn with_port(_port: u16) -> Result<Self> {
        anyhow::bail!("Safari WebDriver not supported in headless environment")
    }
    
    pub async fn back(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver not supported in headless environment")
    }
    
    pub async fn forward(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver not supported in headless environment")
    }
    
    pub async fn refresh(&mut self) -> Result<()> {
        anyhow::bail!("Safari WebDriver not supported in headless environment")
    }
}

#[async_trait]
impl WebDriverController for SafariDriver {}

/// Chrome WebDriver implementation
pub struct ChromeDriver;

impl ChromeDriver {
    pub async fn with_port_headless(_port: u16) -> Result<Self> {
        anyhow::bail!("Chrome WebDriver not supported in headless environment")
    }
    
    pub async fn with_port_headless_and_binary(_port: u16, _binary: Option<&str>) -> Result<Self> {
        anyhow::bail!("Chrome WebDriver not supported in headless environment")
    }
    
    pub async fn back(&mut self) -> Result<()> {
        anyhow::bail!("Chrome WebDriver not supported in headless environment")
    }
    
    pub async fn forward(&mut self) -> Result<()> {
        anyhow::bail!("Chrome WebDriver not supported in headless environment")
    }
    
    pub async fn refresh(&mut self) -> Result<()> {
        anyhow::bail!("Chrome WebDriver not supported in headless environment")
    }
}

#[async_trait]
impl WebDriverController for ChromeDriver {}

/// macOS-specific types (stubs)
pub struct AXApplication;
pub struct AXElement;
pub struct MacAxController;

impl MacAxController {
    pub fn new() -> Result<Self> {
        anyhow::bail!("macOS accessibility not supported in headless environment")
    }
}

/// Platform-specific constructor - returns error for all platforms
pub fn create_controller() -> Result<Box<dyn ComputerController>> {
    anyhow::bail!("Computer control not supported in headless environment. Set computer_control.enabled = false in config.")
}

/// WebDriver types for convenience
pub mod types {
    pub use super::{Rect, TextLocation};
}