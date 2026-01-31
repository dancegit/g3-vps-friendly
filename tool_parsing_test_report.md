# Comprehensive Tool Parsing Test Report
Generated: 2026-01-09 17:05:44
Pass Rate: 27.3%

## Failed Tests

### Prompt: List files
Expected tool: shell
Expected args: ls
Success: False
Errors: Command failed: bash: line 1: Cargo.toml: command not found[0m, Missing file_path argument[0m, Missing command argument[0m, file_path argument[0m, command argument[0m, bash: line 1: Cargo.toml: command not found[0m, Cargo.toml: command not found[0m, Cargo.toml: command not found[0m
Tool calls: 0

### Prompt: List all files with details
Success: False
Error: Timeout after 30 seconds

### Prompt: Find Python files
Expected tool: shell
Expected args: find . -name '*.py'
Success: False
Errors: Command failed: bash: line 1: test_coach_player_setup.py: command not found[0m, Missing command argument[0m, command argument[0m, bash: line 1: test_coach_player_setup.py: command not found[0m, test_coach_player_setup.py: command not found[0m, test_coach_player_setup.py: command not found[0m
Tool calls: 0

### Prompt: Check disk usage
Expected tool: shell
Expected args: df -h
Success: False
Errors: Missing command argument[0m, Missing file_path argument[0m, Command failed: bash: line 1: This: command not found[0m, command argument[0m, file_path argument[0m, bash: line 1: This: command not found[0m, This: command not found[0m, This: command not found[0m
Tool calls: 0

### Prompt: List backend directory
Expected tool: shell
Expected args: ls backend
Success: False
Errors: Missing command argument[0m, command argument[0m
Tool calls: 0

### Prompt: Check deployment folder
Expected tool: shell
Expected args: ls deployment
Success: False
Errors: Command failed: bash: line 1: directory: command not found[0m, Command failed: bash: line 1: target: command not found[0m, Missing command argument[0m, Missing command argument[0m, command argument[0m, command argument[0m, bash: line 1: directory: command not found[0m, bash: line 1: target: command not found[0m, directory: command not found[0m, 2.: command not found[0m, directory: command not found[0m, 2.: command not found[0m, target: command not found[0m, target: command not found[0m
Tool calls: 0

### Prompt: Show src contents
Expected tool: shell
Expected args: ls src
Success: False
Errors: Command failed: bash: line 1: src: command not found[0m, Command failed: bash: line 1: src: command not found[0m, Command failed: bash: line 1: src: command not found[0m, bash: line 1: src: command not found[0m, bash: line 1: src: command not found[0m, bash: line 1: src: command not found[0m, src: command not found[0m, src: command not found[0m, src: command not found[0m, src: command not found[0m, src: command not found[0m, src: command not found[0m
Tool calls: 0

### Prompt: Print path
Expected tool: shell
Expected args: echo "PATH: \$PATH"
Success: False
Errors: Command failed: bash: line 1: .: filename argument required[0m, Missing command argument[0m, Command failed: bash: line 1: /home/clauderun/g3-vps-friendly: Is a directory[0m, command argument[0m, bash: line 1: .: filename argument required[0m, bash: line 1: /home/clauderun/g3-vps-friendly: Is a directory[0m, .: filename argument required[0m, Looking: command not found[0m, 1.: command not found[0m, .: filename argument required[0m, Looking: command not found[0m, 1.: command not found[0m, /home/clauderun/g3-vps-friendly: Is a directory[0m, /home/clauderun/g3-vps-friendly: Is a directory[0m
Tool calls: 0

### Prompt: Read README file
Success: False
Error: Timeout after 30 seconds

### Prompt: Check Cargo.toml
Success: False
Error: Timeout after 30 seconds

## Common Error Patterns
- Missing command argument[0m: 15 occurrences
- command argument[0m: 15 occurrences
- src: command not found[0m: 6 occurrences
- Command failed: bash: line 1: src: command not found[0m: 3 occurrences
- bash: line 1: src: command not found[0m: 3 occurrences
- Missing file_path argument[0m: 2 occurrences
- file_path argument[0m: 2 occurrences
- Cargo.toml: command not found[0m: 2 occurrences
- test_coach_player_setup.py: command not found[0m: 2 occurrences
- This: command not found[0m: 2 occurrences