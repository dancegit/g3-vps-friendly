# MCP (Model Context Protocol) Integration with g3

This guide explains how to use MCP servers with g3 to extend its capabilities with external tools and services.

## Overview

MCP (Model Context Protocol) allows g3 to communicate with external servers that provide specialized tools and capabilities. This integration enables g3 to use tools like:

- **Playwright MCP**: Browser automation and web scraping
- **Dokploy MCP**: Application deployment and management
- **Custom MCP servers**: Any MCP-compatible server

## Quick Start

### 1. Enable MCP in g3

You can enable MCP in three ways:

**Command line flag:**
```bash
cargo run -- --mcp --chat
```

**Configuration file:**
```toml
[mcp]
enabled = true
config_file = ".mcp.json"
auto_start_servers = true
```

**Mixed approach:**
```bash
cargo run -- --mcp --config g3-mcp-config.toml --chat
```

### 2. Your Existing MCP Configuration

You already have these MCP servers configured:

#### Dokploy MCP Server
- **Name**: `dokploy-mcp`
- **Purpose**: Application deployment and management
- **Configuration**: Uses your Dokploy instance at `http://185.177.73.38:3000/api`
- **Available tools**: List applications, deploy applications, etc.

#### Playwright MCP Server
- **Name**: `playwright`
- **Purpose**: Browser automation and web testing
- **Configuration**: Standard Playwright MCP server
- **Available tools**: Browser navigation, screenshots, element interaction, etc.

## Available MCP Tools in g3

Once MCP is enabled, you can use these g3 tools to manage MCP servers:

### Server Management
- **`mcp_list_servers`**: List all configured MCP servers
- **`mcp_start_server`**: Start a specific MCP server
- **`mcp_stop_server`**: Stop a running MCP server
- **`mcp_get_server_info`**: Get information about a server

### Tool Execution
- **`mcp_call_tool`**: Call a specific tool on an MCP server

## Usage Examples

### List Available MCP Servers
```
List all available MCP servers
```

### Start the Playwright Server
```
Start the playwright MCP server
```

### Use Playwright for Browser Automation
```
Start the playwright server, then navigate to https://example.com and take a screenshot
```

### Use Dokploy for Deployment
```
Start the dokploy-mcp server and list all applications
```

### Combined Example
```
Start the playwright MCP server, navigate to https://httpbin.org/html, take a screenshot, and get the page title
```

## Configuration Details

### MCP Configuration File Format
Your `.mcp.json` file follows the standard MCP configuration format:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["@package/mcp-server"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### Environment Variables
Make sure you have the required environment variables set:
- `DOKPLOY_API_KEY`: For Dokploy MCP server (already configured)
- `PATH`: Must include `npx` and Node.js for MCP servers

## Troubleshooting

### MCP Server Won't Start
1. Check if `npx` is available: `which npx`
2. Verify Node.js is installed: `node --version`
3. Check MCP server logs in g3 output
4. Ensure required environment variables are set

### Tool Execution Fails
1. Verify the MCP server is running: `mcp_list_servers`
2. Check the server status: `mcp_get_server_info`
3. Ensure correct tool names and arguments
4. Check g3 logs for detailed error messages

### Common Issues
- **Port conflicts**: MCP servers may need specific ports
- **Missing dependencies**: Some MCP servers require additional packages
- **Network connectivity**: Ensure MCP servers can reach their target services

## Advanced Usage

### Custom MCP Servers
You can add your own MCP servers by:
1. Creating an MCP server following the [MCP specification](https://modelcontextprotocol.io/)
2. Adding it to your `.mcp.json` configuration
3. Using it through g3's MCP tools

### Multiple Servers
You can run multiple MCP servers simultaneously:
```
Start the playwright server and dokploy-mcp server
```

### Integration with Other g3 Features
MCP tools work alongside other g3 features:
- **WebDriver**: Use both browser automation approaches
- **Shell commands**: Combine MCP with shell operations
- **File operations**: Process MCP results with file tools

## Security Considerations

- MCP servers run as separate processes with their own permissions
- Environment variables may contain sensitive information (API keys)
- Review MCP server permissions and network access
- Use MCP servers from trusted sources only

## Next Steps

1. **Test your setup**: Try the examples above
2. **Explore capabilities**: Each MCP server has unique tools
3. **Integrate workflows**: Combine MCP with g3's existing tools
4. **Monitor performance**: MCP servers add overhead, monitor resource usage

For more information about MCP, visit the [official MCP documentation](https://modelcontextprotocol.io/).