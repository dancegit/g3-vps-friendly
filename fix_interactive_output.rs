// Fix for interactive mode tool output display issue
// This patch adds explicit flushing and fixes race conditions in tool output display

use std::io::{self, Write};

// Key fixes needed:

1. **Add explicit flushing after tool execution completion**
   In the tool execution loop, add flush after tool results are displayed:

```rust
// After displaying tool results in the execution loop
if tool_call.tool != "final_output" {
    // ... existing display code ...
    
    // CRITICAL: Add explicit flush to ensure output is displayed
    self.ui_writer.flush();
}
```

2. **Fix race condition in streaming output**
   In ConsoleUiWriter, ensure tool output is flushed immediately:

```rust
fn print_tool_output_line(&self, line: &str) {
    // Skip the TODO list header line
    if line.starts_with("📝 TODO list:") {
        return;
    }
    println!("│ \x1b[2m{}\x1b[0m", line);
    
    // CRITICAL: Add immediate flush
    let _ = io::stdout().flush();
}
```

3. **Add flush after tool completion**
   In the tool execution completion:

```rust
// After tool execution is complete
self.ui_writer.print_tool_timing(&Self::format_duration(exec_duration), tokens_delta, self.context_window.percentage_used());

// CRITICAL: Ensure all tool output is flushed
self.ui_writer.flush();
```

4. **Fix potential buffering issue in interactive prompt**
   Before showing the interactive prompt, ensure all previous output is flushed:

```rust
// Before showing "g3>" prompt in interactive mode
self.ui_writer.flush();
```

// The root cause appears to be:
// 1. Tool execution completes and generates output
// 2. UI writer displays the output but it's buffered
// 3. Interactive prompt appears before buffer is flushed
// 4. User sees the prompt but not the tool output

// This creates the illusion that tools aren't executing
// when they're actually working but the output is buffered