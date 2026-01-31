#!/usr/bin/env python3
"""
Comprehensive Tool Parsing Test Script

This script tests the G3 tool with various prompts that should trigger
different tool calling formats and patterns.
"""

import subprocess
import json
import time
import re
from typing import List, Dict, Any, Optional

class ToolParsingTest:
    def __init__(self):
        self.g3_binary = "/home/clauderun/.local/bin/g3"
        self.test_results = []
        
    def run_g3_test(self, prompt: str, expected_tool: str = None, expected_args: str = None) -> Dict[str, Any]:
        """Run a single test with G3 and analyze the output."""
        print(f"\n🧪 Testing: {prompt}")
        
        start_time = time.time()
        
        try:
            # Run G3 with the prompt
            result = subprocess.run(
                [self.g3_binary],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            duration = time.time() - start_time
            output = result.stdout
            stderr = result.stderr
            
            print(f"⏱️  Duration: {duration:.2f}s")
            
            # Analyze the output
            tool_calls = self.extract_tool_calls(output)
            errors = self.extract_errors(output)
            
            test_result = {
                "prompt": prompt,
                "success": len(errors) == 0,
                "duration": duration,
                "tool_calls": tool_calls,
                "errors": errors,
                "output": output[:500],  # First 500 chars
                "stderr": stderr[:500]
            }
            
            # Check expectations
            if expected_tool:
                test_result["expected_tool"] = expected_tool
                test_result["tool_found"] = any(tc["tool"] == expected_tool for tc in tool_calls)
            
            if expected_args:
                test_result["expected_args"] = expected_args
                test_result["args_found"] = any(expected_args in tc["args"] for tc in tool_calls)
            
            print(f"✅ Success: {test_result['success']}, Tool calls: {len(tool_calls)}, Errors: {len(errors)}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            return {
                "prompt": prompt,
                "success": False,
                "duration": time.time() - start_time,
                "error": "Timeout after 30 seconds"
            }
        except Exception as e:
            return {
                "prompt": prompt,
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def extract_tool_calls(self, output: str) -> List[Dict[str, str]]:
        """Extract tool calls from G3 output."""
        tool_calls = []
        
        # Look for tool execution patterns
        tool_pattern = r'┌─\[1;32m\s+(\w+)\[0m\[35m\s+\|\s+(.+?)\[0m'
        matches = re.findall(tool_pattern, output)
        
        for tool, args in matches:
            tool_calls.append({
                "tool": tool.strip(),
                "args": args.strip()
            })
        
        # Also look for shell command execution patterns
        shell_pattern = r'command=\'([^\']+)\''
        shell_matches = re.findall(shell_pattern, output)
        for command in shell_matches:
            tool_calls.append({
                "tool": "shell",
                "args": command
            })
        
        return tool_calls
    
    def extract_errors(self, output: str) -> List[str]:
        """Extract errors from G3 output."""
        errors = []
        
        # Look for common error patterns
        error_patterns = [
            r"❌\s+(.+)",
            r"Missing\s+(.+)",
            r"Command failed:\s+(.+)",
            r"bash:\s+line\s+\d+:\s+(.+)"
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            errors.extend(matches)
        
        return errors
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests covering various scenarios."""
        print("🚀 Starting Comprehensive Tool Parsing Tests")
        
        test_cases = [
            # Basic commands
            ("List files", "shell", "ls"),
            ("Show current directory", "shell", "pwd"),
            ("Check file contents", "read_file", "file"),
            
            # Complex commands
            ("List all files with details", "shell", "ls -la"),
            ("Find Python files", "shell", "find . -name '*.py'"),
            ("Check disk usage", "shell", "df -h"),
            
            # Commands with paths
            ("List backend directory", "shell", "ls backend"),
            ("Check deployment folder", "shell", "ls deployment"),
            ("Show src contents", "shell", "ls src"),
            
            # Commands with quotes
            ("Echo hello world", "shell", "echo 'hello world'"),
            ("Print path", "shell", "echo \"PATH: \$PATH\""),
            
            # File operations
            ("Read README file", "read_file", "README"),
            ("Check Cargo.toml", "read_file", "Cargo.toml"),
            ("Look at package.json", "read_file", "package.json"),
            
            # TODO operations
            ("Read TODO list", "todo_read", "todo"),
            ("Show current tasks", "todo_read", "tasks"),
            
            # Edge cases
            ("Run multiple commands: ls and pwd", "shell", "ls"),
            ("Check both frontend and backend", "shell", "frontend"),
            ("List then read", "shell", "list"),
            
            # Ambiguous commands
            ("Backend", "shell", "backend"),
            ("Frontend check", "shell", "frontend"),
            ("Test", "shell", "test"),
            
            # Commands that previously failed
            ("What files are here?", "shell", "ls"),
            ("Show me the directory", "shell", "ls"),
            ("Check what's in backend", "shell", "ls backend"),
            ("Look at deployment files", "shell", "ls deployment"),
            
            # XML-specific test patterns
            ("Run shell command ls", "shell", "ls"),
            ("Execute shell with ls", "shell", "ls"),
            ("Use shell tool to list", "shell", "list"),
            ("Shell command: ls -la", "shell", "ls -la"),
            
            # Complex multi-step requests
            ("List files and then check backend", "shell", "ls"),
            ("Show current dir and list backend", "shell", "ls"),
            ("Find all txt files and show first one", "shell", "find"),
        ]
        
        results = []
        passed = 0
        failed = 0
        
        for prompt, expected_tool, expected_args in test_cases:
            result = self.run_g3_test(prompt, expected_tool, expected_args)
            results.append(result)
            
            if result.get("success", False):
                passed += 1
            else:
                failed += 1
        
        # Generate summary
        summary = {
            "total_tests": len(test_cases),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(test_cases) * 100 if test_cases else 0,
            "results": results,
            "timestamp": time.time()
        }
        
        print(f"\n📊 Test Summary:")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass rate: {summary['pass_rate']:.1f}%")
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate a detailed report of the test results."""
        report = []
        report.append("# Comprehensive Tool Parsing Test Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Pass Rate: {summary['pass_rate']:.1f}%")
        report.append("")
        
        # Failed tests
        failed_tests = [r for r in summary['results'] if not r.get('success', False)]
        if failed_tests:
            report.append("## Failed Tests")
            for test in failed_tests[:10]:  # Show first 10 failures
                report.append(f"\n### Prompt: {test['prompt']}")
                if 'expected_tool' in test:
                    report.append(f"Expected tool: {test['expected_tool']}")
                if 'expected_args' in test:
                    report.append(f"Expected args: {test['expected_args']}")
                report.append(f"Success: {test['success']}")
                if 'errors' in test and test['errors']:
                    report.append(f"Errors: {', '.join(test['errors'])}")
                if 'tool_calls' in test:
                    report.append(f"Tool calls: {len(test['tool_calls'])}")
                    for tc in test['tool_calls']:
                        report.append(f"  - {tc['tool']}: {tc['args']}")
                if 'error' in test:
                    report.append(f"Error: {test['error']}")
        
        # Common error patterns
        all_errors = []
        for test in summary['results']:
            if 'errors' in test:
                all_errors.extend(test['errors'])
        
        if all_errors:
            error_counts = {}
            for error in all_errors:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            report.append("\n## Common Error Patterns")
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"- {error}: {count} occurrences")
        
        return "\n".join(report)

def main():
    tester = ToolParsingTest()
    
    # Run comprehensive tests
    summary = tester.run_comprehensive_tests()
    
    # Generate and save report
    report = tester.generate_report(summary)
    
    with open('/home/clauderun/g3-vps-friendly/tool_parsing_test_report.md', 'w') as f:
        f.write(report)
    
    # Save detailed results
    with open('/home/clauderun/g3-vps-friendly/tool_parsing_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Report saved to: /home/clauderun/g3-vps-friendly/tool_parsing_test_report.md")
    print(f"📊 Detailed results saved to: /home/clauderun/g3-vps-friendly/tool_parsing_test_results.json")
    
    # Exit with appropriate code
    exit(0 if summary['pass_rate'] >= 80 else 1)

if __name__ == "__main__":
    main()