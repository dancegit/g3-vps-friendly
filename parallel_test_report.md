# G3 Tool Parsing - Multi-Configuration Test Report
Generated: 2026-01-09 17:00:25

## Overall Configuration Comparison
| Configuration | Type | Success Rate | Missing Arg Errors | Total Tests |
|---------------|------|-------------|-------------------|-------------|
| anthropic_direct | direct | 0.0% | 0 | 19 |
| minimax_direct | direct | 0.0% | 0 | 19 |
| kimi_direct | direct | 0.0% | 0 | 19 |
| localhost_loadbalancer | loadbalancer | 0.0% | 6 | 19 |

## Detailed Analysis

### Consistently Failing Patterns
- Backend
- Check deployment folder
- Check disk usage
- Check file contents of README.md
- Echo hello world
- Execute shell command: ls -la
- Find Python files in current directory
- Frontend check
- List all files with details
- List backend directory
- List files
- Look at backend directory
- Run shell with ls command
- Shell command: find . -name '*.py'
- Show current directory
- Show src contents
- Test directory
- Use shell to list files
- What files are here?

### Common Error Patterns Across All Configs
- Error: No response received from the model. The model may be experiencing issues or the request may have been malformed.: 20 occurrences
- Error: Anthropic API error 404 Not Found: 404 page not found: 19 occurrences
- Missing command argument[0m: 8 occurrences
- command argument[0m: 8 occurrences
- src: command not found[0m: 4 occurrences
- backend: command not found[0m: 2 occurrences
- Command failed: bash: line 1: src: command not found[0m: 2 occurrences
- bash: line 1: src: command not found[0m: 2 occurrences
- Cargo.toml: command not found[0m: 2 occurrences
- Error: Anthropic API error 401 Unauthorized: {"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"},"request_id":"req_011CWx5Ws1gkvJzKuHJv2xTM"}: 1 occurrences