#!/usr/bin/env python3
"""
Parallel Testing Script for G3 Tool Parsing

This script runs comprehensive tests across multiple configurations in parallel
to identify issues with different providers and pinpoint load balancer problems.
"""

import subprocess
import json
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
import re

class ParallelTester:
    def __init__(self):
        self.configs = {
            "localhost_loadbalancer": {
                "config": "test_localhost_config.toml",
                "description": "Local load balancer (current setup)",
                "type": "loadbalancer"
            },
            "minimax_direct": {
                "config": "config.anthropic.minimax.toml", 
                "description": "MiniMax direct API",
                "type": "direct"
            },
            "kimi_direct": {
                "config": "config.anthropic.kimi.toml",
                "description": "Kimi direct API", 
                "type": "direct"
            },
            "anthropic_direct": {
                "config": "config.anthropic.direct.toml",
                "description": "Anthropic direct API",
                "type": "direct"
            }
        }
        
        self.test_prompts = [
            # Basic commands that should work reliably
            "List files",
            "Show current directory", 
            "Check file contents of README.md",
            "List backend directory",
            
            # Commands that were causing XML parsing issues
            "What files are here?",
            "Look at backend directory",
            "Check deployment folder",
            "Show src contents",
            
            # Complex commands with arguments
            "List all files with details",
            "Find Python files in current directory",
            "Echo hello world",
            "Check disk usage",
            
            # Ambiguous commands that might cause issues
            "Backend",
            "Frontend check", 
            "Test directory",
            
            # XML-heavy phrasings
            "Use shell to list files",
            "Execute shell command: ls -la",
            "Run shell with ls command",
            "Shell command: find . -name '*.py'"
        ]
        
        self.results = {}

    def run_single_test(self, config_name: str, prompt: str) -> Dict[str, Any]:
        """Run a single test with the specified configuration."""
        config = self.configs[config_name]
        g3_binary = "/home/clauderun/.local/bin/g3"
        
        print(f"🧪 Testing {config_name}: {prompt}")
        
        start_time = time.time()
        
        try:
            # Run G3 with specific config
            result = subprocess.run(
                [g3_binary, "--config", config["config"]],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=20
            )
            
            duration = time.time() - start_time
            output = result.stdout
            
            # Analyze output
            tool_calls = self.extract_tool_calls(output)
            errors = self.extract_errors(output)
            has_missing_arg = "Missing command argument" in output
            
            test_result = {
                "config": config_name,
                "config_description": config["description"],
                "config_type": config["type"],
                "prompt": prompt,
                "success": len(errors) == 0 and len(tool_calls) > 0 and not has_missing_arg,
                "duration": duration,
                "tool_calls": tool_calls,
                "errors": errors,
                "has_missing_arg_error": has_missing_arg,
                "output_preview": output[:300] + "..." if len(output) > 300 else output,
                "return_code": result.returncode
            }
            
            print(f"✅ {config_name}: {prompt} - {'SUCCESS' if test_result['success'] else 'FAILED'}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            return {
                "config": config_name,
                "prompt": prompt,
                "success": False,
                "duration": time.time() - start_time,
                "error": "Timeout after 20 seconds"
            }
        except Exception as e:
            return {
                "config": config_name,
                "prompt": prompt,
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    def extract_tool_calls(self, output: str) -> list:
        """Extract tool calls from G3 output."""
        tool_calls = []
        
        # Look for tool execution patterns
        tool_pattern = r'┌─\[1;32m\s+(\w+)\[0m\[35m\s+\|\s+(.+?)\[0m'
        matches = re.findall(tool_pattern, output, re.MULTILINE | re.DOTALL)
        
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

    def extract_errors(self, output: str) -> list:
        """Extract errors from G3 output."""
        errors = []
        
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

    def run_config_tests(self, config_name: str) -> Dict[str, Any]:
        """Run all tests for a specific configuration."""
        print(f"\n{'='*60}")
        print(f"🚀 Testing configuration: {config_name}")
        print(f"Description: {self.configs[config_name]['description']}")
        print(f"{'='*60}")
        
        config_results = []
        
        for prompt in self.test_prompts:
            result = self.run_single_test(config_name, prompt)
            config_results.append(result)
        
        # Calculate statistics
        total_tests = len(config_results)
        successful_tests = sum(1 for r in config_results if r.get('success', False))
        missing_arg_errors = sum(1 for r in config_results if r.get('has_missing_arg_error', False))
        
        config_summary = {
            "config_name": config_name,
            "config_info": self.configs[config_name],
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "missing_arg_errors": missing_arg_errors,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": config_results
        }
        
        print(f"\n📊 {config_name} Summary:")
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Missing arg errors: {missing_arg_errors}")
        print(f"Success rate: {config_summary['success_rate']:.1f}%")
        
        return config_summary

    def run_all_tests_parallel(self) -> Dict[str, Any]:
        """Run tests for all configurations in parallel."""
        print("🚀 Starting Parallel Testing Across Multiple Configurations")
        print("=" * 80)
        
        all_results = {}
        
        # Use ThreadPoolExecutor for parallel testing
        with ThreadPoolExecutor(max_workers=len(self.configs)) as executor:
            # Submit all config tests
            future_to_config = {
                executor.submit(self.run_config_tests, config_name): config_name
                for config_name in self.configs.keys()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_config):
                config_name = future_to_config[future]
                try:
                    result = future.result()
                    all_results[config_name] = result
                except Exception as e:
                    print(f"❌ Error testing {config_name}: {e}")
                    all_results[config_name] = {
                        "config_name": config_name,
                        "error": str(e),
                        "results": []
                    }
        
        return all_results

    def generate_comparison_report(self, all_results: Dict[str, Any]) -> str:
        """Generate a comprehensive comparison report."""
        report = []
        report.append("# G3 Tool Parsing - Multi-Configuration Test Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall summary
        total_tests = len(self.test_prompts)
        report.append("## Overall Configuration Comparison")
        report.append("| Configuration | Type | Success Rate | Missing Arg Errors | Total Tests |")
        report.append("|---------------|------|-------------|-------------------|-------------|")
        
        for config_name, result in all_results.items():
            if "results" in result:
                success_rate = result.get("success_rate", 0)
                missing_errors = result.get("missing_arg_errors", 0)
                report.append(f"| {config_name} | {result['config_info']['type']} | {success_rate:.1f}% | {missing_errors} | {result.get('total_tests', 0)} |")
        
        # Detailed analysis
        report.append("\n## Detailed Analysis")
        
        # Find patterns that work vs don't work
        all_success_patterns = set()
        all_failure_patterns = set()
        
        for config_name, result in all_results.items():
            if "results" in result:
                for test_result in result["results"]:
                    prompt = test_result["prompt"]
                    if test_result.get("success", False):
                        all_success_patterns.add(prompt)
                    else:
                        all_failure_patterns.add(prompt)
        
        # Patterns that consistently fail
        consistent_failures = all_failure_patterns - all_success_patterns
        if consistent_failures:
            report.append("\n### Consistently Failing Patterns")
            for pattern in sorted(consistent_failures):
                report.append(f"- {pattern}")
        
        # Patterns that work with direct APIs but not load balancer
        load_balancer_result = all_results.get("localhost_loadbalancer", {})
        direct_api_results = [r for name, r in all_results.items() if name != "localhost_loadbalancer" and "results" in r]
        
        if load_balancer_result and direct_api_results:
            lb_failures = {r["prompt"] for r in load_balancer_result.get("results", []) if not r.get("success", False)}
            direct_successes = set()
            for direct_result in direct_api_results:
                direct_successes.update({r["prompt"] for r in direct_result.get("results", []) if r.get("success", False)})
            
            lb_specific_failures = lb_failures & direct_successes
            if lb_specific_failures:
                report.append("\n### Load Balancer Specific Issues")
                report.append("These patterns fail with load balancer but work with direct APIs:")
                for pattern in sorted(lb_specific_failures):
                    report.append(f"- {pattern}")
        
        # Common errors across all configs
        all_errors = []
        for config_result in all_results.values():
            if "results" in config_result:
                for test_result in config_result["results"]:
                    if "errors" in test_result:
                        all_errors.extend(test_result["errors"])
        
        if all_errors:
            error_counts = {}
            for error in all_errors:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            report.append("\n### Common Error Patterns Across All Configs")
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"- {error}: {count} occurrences")
        
        return "\n".join(report)

def main():
    tester = ParallelTester()
    
    # Run all tests in parallel
    all_results = tester.run_all_tests_parallel()
    
    # Generate comparison report
    report = tester.generate_comparison_report(all_results)
    
    # Save results
    with open('/home/clauderun/g3-vps-friendly/parallel_test_report.md', 'w') as f:
        f.write(report)
    
    with open('/home/clauderun/g3-vps-friendly/parallel_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📊 Report saved to: /home/clauderun/g3-vps-friendly/parallel_test_report.md")
    print(f"📈 Detailed results saved to: /home/clauderun/g3-vps-friendly/parallel_test_results.json")
    
    # Calculate overall success rate
    total_tests = 0
    total_successes = 0
    for result in all_results.values():
        if "successful_tests" in result:
            total_tests += result["total_tests"]
            total_successes += result["successful_tests"]
    
    overall_success_rate = (total_successes / total_tests * 100) if total_tests > 0 else 0
    print(f"\n🎯 Overall Success Rate: {overall_success_rate:.1f}%")
    
    exit(0 if overall_success_rate >= 75 else 1)

if __name__ == "__main__":
    main()