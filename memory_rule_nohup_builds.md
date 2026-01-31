# Memory Rule: Always Use nohup for Builds and Long-Running Operations

**Rule**: Always use `nohup` wrapper for build commands (cargo, uv, npm, etc.) and long-running scripts to prevent interruption and allow background execution.

**Commands to wrap with nohup**:
- `cargo build` → `nohup cargo build`
- `cargo build --release` → `nohup cargo build --release`
- `uv pip install` → `nohup uv pip install`
- `npm install` → `nohup npm install`
- Long-running Python scripts → `nohup python script.py`
- Any command that might take >30 seconds

**Benefits**:
- Prevents interruption if terminal disconnects
- Allows background execution
- Output is captured to `nohup.out` file
- Process continues even if SSH session ends

**Example usage**:
```bash
# Instead of: cargo build --release
# Use: nohup cargo build --release
nohup cargo build --release

# Check progress
tail -f nohup.out
```

**Always remember**: When you see a build command or long-running script, automatically prepend `nohup` to it.