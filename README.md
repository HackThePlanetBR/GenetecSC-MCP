# Genetec MCP Server

A Model Context Protocol (MCP) server for integrating with Genetec Security Center Web SDK API.

## Overview

This MCP server provides AI assistants with the ability to interact with Genetec Security Center, enabling:
- Entity management (cardholders, doors, cameras, etc.)
- Access control operations (grant access, lock/unlock doors)
- Event monitoring and reporting
- Visitor management

## Features

### Group 1: Core Entity Management
- `genetec_search_entities` - Search for entities by type
- `genetec_get_entity_details` - Get detailed entity information
- `genetec_list_cardholders` - List cardholders with filters
- `genetec_get_cardholder_details` - Get cardholder details
- `genetec_list_doors` - List doors in the system
- `genetec_list_cameras` - List cameras in the system

### Group 2: Access Control Operations
- `genetec_grant_door_access` - Grant temporary door access
- `genetec_lock_unlock_door` - Lock or unlock a door
- `genetec_list_access_events` - List recent access events
- `genetec_create_visitor` - Create temporary visitor with credentials

## Prerequisites

- Python 3.10 or higher
- Genetec Security Center with Web SDK role configured
- Valid SDK certificate and credentials

## Installation

1. Clone or download this repository

2. Install using uv (recommended):
```bash
cd genetec_mcp
uv sync --all-extras
```

Or using pip:
```bash
cd genetec_mcp
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and configure your Genetec server details:
```bash
GENETEC_SERVER_URL=https://your-server:4590/WebSdk
GENETEC_USERNAME=your_username
GENETEC_PASSWORD=your_password
GENETEC_APP_ID=your_sdk_application_id
```

## Running the Server

### Standalone (for testing)
```bash
uv run genetec_mcp
```

### With Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "genetec": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/genetec_mcp",
        "run",
        "genetec_mcp"
      ]
    }
  }
}
```

## Usage Examples

### Search for entities
```
Search for all doors in the system
```

### Get entity details
```
Get details for door with GUID a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Grant temporary access
```
Grant John Doe (cardholder GUID: xxx) temporary access to Main Entrance (door GUID: yyy) for 60 seconds
```

### List access events
```
Show me access events for the Server Room in the last 24 hours
```

## Development

### Project Structure
```
genetec_mcp/
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── .env.example            # Environment variables template
└── src/
    └── genetec_mcp/
        ├── __init__.py     # Package initialization
        ├── __main__.py     # Entry point
        ├── server.py       # Main server with tool implementations
        ├── config.py       # Configuration and constants
        ├── models.py       # Pydantic models for validation
        ├── client.py       # Genetec API client
        └── formatters.py   # Response formatting utilities
```

### Running Tests
```bash
# Syntax check
python -m py_compile src/genetec_mcp/*.py

# Run with MCP Inspector (for testing tools)
npx @modelcontextprotocol/inspector uv run genetec_mcp
```

## Limitations

- Streaming events (real-time monitoring) not yet implemented
- Complex reporting features not yet implemented
- Entity modification limited to access control operations
- No alarm management in current version

## Security Considerations

- Always use HTTPS in production environments
- Store credentials securely (use environment variables, never commit .env)
- Follow principle of least privilege for user accounts
- Enable SSL certificate verification in production
- Regularly rotate passwords and SDK certificates

## Troubleshooting

### "Authentication failed"
- Verify GENETEC_USERNAME, GENETEC_PASSWORD, and GENETEC_APP_ID are correct
- Ensure user has "Log on using the SDK" privilege enabled
- Check that SDK certificate is valid and included in license

### "Cannot connect to server"
- Verify GENETEC_SERVER_URL is correct (include protocol and port)
- Check that Web SDK role is running in Security Center
- Ensure firewall allows connections to port 4590

### "Permission denied"
- User account needs appropriate privileges for the requested operation
- Check user's role assignments in Security Center Config Tool

## References

- [Genetec Developer Portal](https://developer.genetec.com)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Security Center Administrator Guide](https://docs.genetec.com)

## License

MIT

## Support

For Genetec API questions: [DAP@genetec.com](mailto:DAP@genetec.com)  
For MCP questions: [MCP Documentation](https://modelcontextprotocol.io)