#!/bin/bash

# build-g3-vps-simple.sh - Simple, correct replacement

set -e

echo "=== G3 VPS Simple Build Script ==="
echo "Single, correct replacement of g3_computer_control"

# --- Self-Protection ---
SCRIPT_NAME="$(basename "$0")"
if [ ! -f "Cargo.toml" ] || [ ! -d "crates/g3-core" ]; then
    echo "❌ Error: Must be run from g3 project root"
    exit 1
fi

# --- 1. Reset (protect script) ---
echo "📦 Resetting repository..."
git reset --hard HEAD
git clean -fdx --exclude="$SCRIPT_NAME"

# --- 2. Install Dependencies ---
echo "📦 Installing system libraries..."
sudo apt-get update && sudo apt-get install -y \
    libclang-dev \
    pkg-config \
    build-essential

# --- 3. Patch Cargo.toml ---
echo "🔧 Disabling g3-computer-control dependency..."
sed -i 's/^g3-computer-control =/# g3-computer-control =/' crates/g3-core/Cargo.toml

# --- 4. Create Stub Module ---
echo "🔧 Creating computer_control stub..."
cat > crates/g3-core/src/computer_control_stub.rs << 'EOF'
//! Stub for g3_computer_control on headless systems

use async_trait::async_trait;
use anyhow::Result;

#[derive(Debug, Clone)]
pub struct Rect {
    pub x: i32, pub y: i32, pub width: i32, pub height: i32,
}

#[derive(Debug, Clone)]
pub struct WebElement { pub id: String }

#[derive(Debug)]
pub struct WebDriverController;

#[async_trait]
pub trait ComputerController: Send + Sync {}

pub fn create_controller() -> Option<Box<dyn ComputerController>> {
    None
}

impl WebDriverController {
    pub async fn new(_provider: &str, _port: u16) -> Result<Self> {
        Err(anyhow::anyhow!("WebDriver not available on headless system"))
    }
}

pub struct SafariDriver;
pub struct ChromeDriver;

impl SafariDriver {
    pub async fn with_port(_port: u16) -> Result<Self> {
        Err(anyhow::anyhow!("Safari not available"))
    }
}

impl ChromeDriver {
    pub async fn with_port_headless(_port: u16) -> Result<Self> {
        Err(anyhow::anyhow!("Chrome not available"))
    }
    
    pub async fn with_port_headless_and_binary(_port: u16, _binary: Option<String>) -> Result<Self> {
        Err(anyhow::anyhow!("Chrome not available"))
    }
}
EOF

# --- 5. Patch lib.rs ---
echo "🔧 Patching lib.rs module declaration..."
sed -i 's/^pub mod computer_control;/pub mod computer_control_stub as computer_control;/' crates/g3-core/src/lib.rs

# --- 6. Single, correct replacement ---
echo "🔧 Replacing g3_computer_control:: with crate::computer_control::..."
find crates/g3-core/src -name "*.rs" -exec sed -i 's/g3_computer_control::/crate::computer_control::/g' {} \;

# --- 7. Build ---
echo "🔨 Building G3..."
cargo clean
cargo build --release

# --- 8. Verify ---
if [ -f "./target/release/g3" ]; then
    echo ""
    echo "✅ SUCCESS! Binary at ./target/release/g3"
    echo "Run with: ./target/release/g3"
else
    echo ""
    echo "❌ Build failed"
    exit 1
fi
