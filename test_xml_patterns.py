#!/usr/bin/env python3
"""
Focused XML Pattern Testing Script

This script specifically tests the XML patterns that were causing
"Missing command argument" errors and other parsing issues.
"""

import subprocess
import re
import time

def test_xml_pattern(description: str, prompt: str, expected_command: str = None) -> dict:
    """Test a specific XML pattern."""
    print(f"\n🧪 {description}")
    print(f"Prompt: {prompt}")
    
    try:
        result = subprocess.run(
            ["/home/clauderun/.local/bin/g3"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=15
        )
        
        output = result.stdout
        
        # Extract the actual command executed
        command_matches = re.findall(r"command='([^']+)'", output)
        
        success = len(command_matches) > 0
        actual_command = command_matches[0] if command_matches else None
        
        # Check for "Missing command argument" error
        missing_arg_error = "Missing command argument" in output
        
        print(f"✅ Success: {success}")
        print(f"📝 Actual command: {actual_command}")
        print(f"❌ Missing arg error: {missing_arg_error}")
        
        if expected_command and actual_command:
            command_correct = expected_command in actual_command
            print(f"🎯 Command correct: {command_correct}")
        
        return {
            "description": description,
            "prompt": prompt,
            "success": success,
            "actual_command": actual_command,
            "missing_arg_error": missing_arg_error,
            "output_preview": output[:200] + "..." if len(output) > 200 else output
        }
        
    except Exception as e:
        return {
            "description": description,
            "prompt": prompt,
            "success": False,
            "error": str(e)
        }

def test_problematic_xml_patterns():
    """Test the specific XML patterns that were causing issues."""
    
    print("🔍 Testing Problematic XML Patterns")
    
    test_cases = [
        # Patterns that previously caused "Missing command argument"
        ("Simple directory check", "Check backend directory", "backend"),
        ("List deployment files", "List deployment files", "deployment"),
        ("Show src contents", "Show src contents", "src"),
        ("What files are here?", "What files are here?", "ls"),
        ("Look at backend", "Look at backend", "backend"),
        
        # Patterns with ambiguous commands
        ("Backend", "Backend", "backend"),
        ("Frontend", "Frontend", "frontend"),
        ("Test directory", "Test directory", "test"),
        
        # Complex multi-part commands
        ("List then check backend", "List files then check backend", "ls"),
        ("Show current dir and backend", "Show current dir and list backend", "ls"),
        
        # Commands with paths that failed
        ("Check what's in backend", "Check what's in backend", "backend"),
        ("Look at deployment folder", "Look at deployment folder", "deployment"),
        ("Show me the src", "Show me the src directory", "src"),
        
        # XML-specific phrasings
        ("Use shell to list", "Use shell tool to list files", "ls"),
        ("Execute shell command", "Execute shell command: ls -la", "ls -la"),
        ("Run shell with ls", "Run shell with ls command", "ls"),
        ("Shell: ls", "Shell: ls -la", "ls -la"),
        
        # Previously working patterns (for comparison)
        ("List files", "List files", "ls"),
        ("Show directory", "Show current directory", "ls"),
        ("Check files", "Check files in current directory", "ls"),
    ]
    
    results = []
    passed = 0
    failed = 0
    missing_arg_errors = 0
    
    for description, prompt, expected in test_cases:
        result = test_xml_pattern(description, prompt, expected)
        results.append(result)
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
            
        if result.get("missing_arg_error", False):
            missing_arg_errors += 1
    
    # Print summary
    print(f"\n📊 XML Pattern Test Summary:")
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Missing arg errors: {missing_arg_errors}")
    print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
    
    # Show failed tests
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['description']}: {result['prompt']}")
                if result.get("missing_arg_error"):
                    print(f"    → Missing command argument error")
                if result.get("actual_command"):
                    print(f"    → Got command: {result['actual_command']}")
    
    return {
        "total": len(test_cases),
        "passed": passed,
        "failed": failed,
        "missing_arg_errors": missing_arg_errors,
        "success_rate": passed / len(test_cases) * 100,
        "results": results
    }

def main():
    print("🔧 XML Pattern Testing Tool")
    print("=" * 50)
    
    # Run the focused XML pattern tests
    results = test_problematic_xml_patterns()
    
    # Save detailed results
    import json
    with open('/home/clauderun/g3-vps-friendly/xml_pattern_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: /home/clauderun/g3-vps-friendly/xml_pattern_test_results.json")
    
    # Exit with appropriate code
    exit(0 if results["success_rate"] >= 70 else 1)

if __name__ == "__main__":
    main()