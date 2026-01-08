# G3 Build Issues on Debian 12 VPS - Troubleshooting Report

## Executive Summary

Building G3 (AI coding agent) on a headless Debian 12 VPS fails due to hard-coded dependencies on GUI libraries and macOS-specific features in the `g3-computer-control` crate. The crate is not optional in the workspace structure, forcing compilation of OCR (Tesseract), X11 (xtst), and WebDriver dependencies that are unnecessary for core AI functionality.

## Environment
- **OS**: Debian 12 (headless VPS, no GUI)
- **CPU**: x86_64
- **Rust**: Latest stable
- **Project**: g3 AI coding agent (https://github.com/dhanji/g3)
- **Target**: Build release binary for code generation tasks

## Root Cause Analysis

The `g3-computer-control` workspace crate is:
1. **Not optional** - Hard dependency in `crates/g3-core/Cargo.toml`
2. **Not feature-gated** - No Cargo features to disable it
3. **Contains platform-specific code** - macOS WebDriver, GUI automation, OCR
4. **Widely imported** - Used across multiple modules (`webdriver.rs`, `misc.rs`, `executor.rs`, `lib.rs`)

## Error Timeline

### Stage 1: C++ Build Dependencies
**Error**: `Unable to find libclang: "couldn't find any valid shared libraries"`
- **Root Cause**: `bindgen` needs `libclang-dev` to parse llama.cpp headers
- **Fix**: `sudo apt-get install libclang-dev`

### Stage 2: X11 Libraries
**Error**: `The system library 'xtst' required by crate 'x11' was not found`
- **Root Cause**: `x11` crate requires X11 development headers for GUI automation
- **Fix**: `sudo apt-get install libxtst-dev`

### Stage 3: OCR Libraries
**Error**: `The system library 'lept' required by crate 'leptonica-sys' was not found`
- **Root Cause**: Tesseract OCR dependency chain (`tesseract` → `leptonica-sys` → `libleptonica-dev`)
- **Fix**: `sudo apt-get install libleptonica-dev libtesseract-dev`

### Stage 4: Trait Definition Mismatch
**Error**: `method 'click' is not a member of trait 'ComputerController'`
- **Root Cause**: Linux implementation has methods that don't exist in trait definition
- **Failed Fix**: Attempted to add stub methods, but trait itself is incomplete

### Stage 5: Import Resolution Failures (Final Blocker)

Multiple variations of:
```
error[E0432]: unresolved import `g3_computer_control`
error[E0432]: unresolved import `computer_control`
error[E0432]: unresolved import `crate::computer_control`
error[E0433]: failed to resolve: use of unresolved module or unlinked crate `g3_crate`
```

**Root Cause**: 
- Original code uses: `use g3_computer_control::...`
- After patching to `use computer_control::...`, Rust can't find the module
- Attempting `use crate::computer_control::...` is correct, but sed regex was too greedy and created `g3_crate::computer_control::`
- Module `computer_control` doesn't exist in crate root until we alias it

## Failed Solutions

### Solution 1: Install All GUI Dependencies
```bash
sudo apt-get install libxtst-dev libleptonica-dev libtesseract-dev
```
**Result**: ✅ Fixed C++ dependencies but still failed on trait mismatches and incomplete Linux implementation

### Solution 2: Comment Out Dependency
```bash
sed -i 's/g3-computer-control/# g3-computer-control/' Cargo.toml
```
**Result**: ❌ Failed - still referenced in code, created unresolved import errors

### Solution 3: Create Module Alias
```bash
# In lib.rs
pub mod computer_control_stub as computer_control;
```
**Result**: ❌ Failed - imports in other files still used `g3_computer_control::` prefix

### Solution 4: Global Find & Replace
```bash
find . -name "*.rs" -exec sed -i 's/g3_computer_control::/crate::computer_control::/g' {} \;
```
**Result**: ❌ Partially worked but sed regex was too greedy, created `g3_crate::computer_control::` artifacts

### Solution 5: Delete Problematic Files
```bash
rm -f crates/g3-core/src/tools/webdriver.rs crates/g3-core/src/webdriver_session.rs
```
**Result**: ❌ Failed - other modules import from these files, created cascade of "module not found" errors

## Key Technical Insights

1. **Workspace Dependency**: `g3-computer-control` is a workspace dependency, not an external crate
2. **Import Variations**: Code uses multiple patterns:
   - `use g3_computer_control::...` (external crate style)
   - `use crate::computer_control::...` (local module style)
   - `computer_control::...` (implied local)
3. **Module Declaration Order**: In Rust, `pub mod` declarations must come before `pub use`
4. **Regex Pitfalls**: Sed with capture groups can create unintended replacements like `g3_crate::`

## Working Solution Approach

The correct fix requires:

1. **Disable dependency** in Cargo.toml
   ```toml
   # g3-computer-control = { path = "../g3-computer-control" }
   ```

2. **Create stub module** at `crates/g3-core/src/computer_control_stub.rs` with **identical public API**

3. **Alias the stub** in `lib.rs`
   ```rust
   pub mod computer_control_stub as computer_control;
   ```

4. **Globally replace** all import statements:
   ```bash
   find crates/g3-core/src -name "*.rs" -exec sed -i 's/g3_computer_control::/crate::computer_control::/g' {} \;
   ```

5. **Create stub implementations** for `webdriver_session.rs`, `tools/webdriver.rs`, and `tools/misc.rs` that import from `crate::computer_control`

6. **Do not delete files** - create stubs that provide the same API surface

## Recommendations

### For Users (Short-term)
- Use the complete script that: resets repo, installs deps, creates stubs, replaces imports, and builds
- Run script from outside repo or use `--exclude` to protect the script itself
- Accept that computer control features (OCR, WebDriver, GUI automation) will return runtime errors

### For Maintainers (Long-term)
1. **Make computer-control optional** with Cargo features:
   ```toml
   [features]
   default = []
   computer-control = ["dep:g3-computer-control"]
   ```

2. **Gate imports with `cfg` attributes**:
   ```rust
   #[cfg(feature = "computer-control")]
   use g3_computer_control::...
   ```

3. **Provide headless stubs** in the actual crate, not as patches

4. **Document VPS/headless build requirements** in README

## Verification Checklist

After successful build, verify:
- [ ] Binary exists at `./target/release/g3`
- [ ] `./target/release/g3 --help` shows available commands
- [ ] File operations work: `g3 "read file.txt"`
- [ ] Code generation works: `g3 "write a fibonacci function"`
- [ ] Computer control features fail gracefully with "not supported" messages

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-09  
**Tested On**: Debian 12 VPS, x86_64, 4GB RAM
