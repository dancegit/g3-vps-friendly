#!/usr/bin/env python3
"""
Debug script to see what content is in the accumulated buffer when XML parsing happens.
"""

import subprocess
import re

def test_buffer_content():
    """Test to see what XML content is in the accumulated buffer."""
    
    print("🔍 Testing accumulated buffer content for XML parsing")
    print("=" * 60)
    
    # Run with debug logging and capture the buffer processing
    result = subprocess.run([
        '/home/clauderun/.local/bin/g3',
        '--config', 'test_localhost_config.toml',
        '--new-session',
        '--quiet',
        'execute "echo BUFFER_CONTENT_TEST"'
    ], capture_output=True, text=True, timeout=15)
    
    print(f"Return code: {result.returncode}")
    
    # Look for XML-related debug messages
    debug_output = result.stderr
    
    # Extract the text that gets parsed for XML
    xml_parsing_lines = []
    current_content = ""
    
    for line in debug_output.split('\n'):
        if "🔍 XML_PARSER: Starting XML parsing for text:" in line:
            # Extract the content that XML parser is trying to parse
            match = re.search(r"text: '([^']+)'", line)
            if match:
                content = match.group(1)
                xml_parsing_lines.append(content)
                if len(content) > 50:  # Only store substantial content
                    current_content = content
    
    print(f"\n=== XML PARSING ATTEMPTS ===")
    for i, content in enumerate(xml_parsing_lines):
        print(f"{i+1}. XML parser tried to parse: '{content[:100]}...'")
    
    if current_content:
        print(f"\n=== FINAL BUFFER CONTENT ===")
        print(f"Last substantial content: '{current_content}'")
        
        # Check if this looks like XML
        if "<invoke" in current_content or "<tool" in current_content:
            print("✅ Contains XML-like content")
        else:
            print("❌ Does not contain clear XML content")
            
        # Look for complete XML structure
        if "<invoke_tool_call>" in current_content and "</invoke_tool_call>" in current_content:
            print("✅ Contains complete XML invoke structure")
        else:
            print("❌ Does not contain complete XML structure")
    
    # Also look for the buffer processing message
    buffer_messages = []
    for line in debug_output.split('\n'):
        if "Found {} XML tool calls in buffer at stream end" in line:
            buffer_messages.append(line)
        elif "XML_PARSER: Found" in line and "tools" in line:
            buffer_messages.append(line)
    
    print(f"\n=== BUFFER PROCESSING RESULTS ===")
    for msg in buffer_messages:
        print(f"{msg}")
    
    if not buffer_messages:
        print("❌ No XML tool calls found in buffer processing")
    else:
        print("✅ XML tool calls processing detected")

if __name__ == "__main__":
    test_buffer_content()