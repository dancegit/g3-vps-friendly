#!/usr/bin/env python3
"""
Quick Diagnostic Script for Tool Parsing Issues

This script quickly tests the current state of tool parsing to identify
remaining issues after the XML parsing fixes.
"""

import subprocess
import time
import re

def quick_test(prompt: str, expected_pattern: str = None) -> dict:
    """Run a quick test and analyze the result."""
    print(f"\n🧪 Testing: {prompt}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            ["/home/clauderun/.local/bin/g3"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=15
        )
        
        duration = time.time() - start_time
        output = result.stdout
        
        # Check for key indicators
        has_missing_arg = "Missing command argument" in output
        has_tool_execution = "SHELL_TOOL: About to call" in output
        has_command = re.search(r"command='([^']+)'", output)
        
        actual_command = has_command.group(1) if has_command else None
        
        success = has_tool_execution and not has_missing_arg and actual_command is not None
        
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"✅ Tool execution: {has_tool_execution}")
        print(f"❌ Missing arg error: {has_missing_arg}")
        print(f"📝 Actual command: {actual_command}")
        print(f"🎯 Success: {success}")
        
        return {
            "prompt": prompt,
            "success": success,
            "duration": duration,
            "has_missing_arg": has_missing_arg,
            "has_tool_execution": has_tool_execution,
            "actual_command": actual_command,
            "output_preview": output[:200] + "..." if len(output) > 200 else output
        }
        
    except Exception as e:
        return {
            "prompt": prompt,
            "success": False,
            "error": str(e)
        }

def run_diagnostic():
    """Run a quick diagnostic test suite."""
    print("🔍 Quick Tool Parsing Diagnostic")
    print("=" * 50)
    
    # Test cases that were problematic before the fix
    test_cases = [
        "List files",
        "Check backend directory", 
        "What files are here?",
        "Show backend contents",
        "List deployment files",
        "Look at src directory",
        "Check current directory",
        "Show all files"
    ]
    
    results = []
    passed = 0
    failed = 0
    missing_arg_errors = 0
    
    for prompt in test_cases:
        result = quick_test(prompt)
        results.append(result)
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
            if result.get("has_missing_arg"):
                missing_arg_errors += 1
    
    # Generate summary
    print(f"\n📊 Diagnostic Summary:")
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Missing arg errors: {missing_arg_errors}")
    print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
    
    # Show failures
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['prompt']}")
                if result.get("has_missing_arg"):
                    print(f"    → Missing command argument")
                if result.get("actual_command"):
                    print(f"    → Got: {result['actual_command']}")
    
    return {
        "total": len(test_cases),
        "passed": passed,
        "failed": failed,
        "missing_arg_errors": missing_arg_errors,
        "success_rate": passed / len(test_cases) * 100,
        "results": results
    }

def main():
    results = run_diagnostic()
    
    # Save results
    import json
    with open('/home/clauderun/g3-vps-friendly/quick_diagnostic_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: /home/clauderun/g3-vps-friendly/quick_diagnostic_results.json")
    
    # Exit with appropriate code
    exit(0 if results["success_rate"] >= 80 else 1)

if __name__ == "__main__":
    main()