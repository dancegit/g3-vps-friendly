#!/usr/bin/env python3
"""
Debug the provider registration logic by examining the config structure.
"""

import toml

def debug_config():
    """Debug the configuration structure."""
    
    config_content = """
[providers]
default_provider = "minimax.default"

[providers.openai_compatible.minimax]
model = "minimax-m2"
base_url = "https://api.minimax.io/v1"
api_key = "test-key"
max_tokens = 64000
temperature = 0.3

[agent]
name = "test-agent"
provider = "minimax.default"
fallback_default_max_tokens = 8192
enable_streaming = true
timeout_seconds = 60
max_retry_attempts = 3
autonomous_max_retry_attempts = 6
allow_multiple_tool_calls = true
auto_compact = true

[computer_control]
enabled = false
require_confirmation = true
max_actions_per_second = 5

[webdriver]
enabled = true
browser = "chrome-headless"
safari_port = 4444
chrome_port = 9515

[macax]
enabled = false

[ui]
machine_mode = true
"""
    
    try:
        config = toml.loads(config_content)
        print("Configuration structure:")
        print(f"default_provider: {config['providers']['default_provider']}")
        print(f"openai_compatible section: {list(config['providers']['openai_compatible'].keys())}")
        
        # Check if 'minimax' exists in openai_compatible
        if 'minimax' in config['providers']['openai_compatible']:
            print(f"✅ 'minimax' found in openai_compatible section")
            minimax_config = config['providers']['openai_compatible']['minimax']
            print(f"minimax config: {minimax_config}")
        else:
            print(f"❌ 'minimax' NOT found in openai_compatible section")
            
        # Parse the provider reference
        provider_ref = config['providers']['default_provider']
        parts = provider_ref.split('.')
        print(f"\nProvider reference: {provider_ref}")
        print(f"Parts: {parts}")
        
        if len(parts) == 2:
            provider_type, config_name = parts
            print(f"Provider type: {provider_type}")
            print(f"Config name: {config_name}")
            
            # Check if provider_type exists in openai_compatible
            if provider_type in config['providers']['openai_compatible']:
                print(f"✅ Provider type '{provider_type}' found in openai_compatible")
            else:
                print(f"❌ Provider type '{provider_type}' NOT found in openai_compatible")
        
    except Exception as e:
        print(f"Error parsing config: {e}")

if __name__ == "__main__":
    debug_config()