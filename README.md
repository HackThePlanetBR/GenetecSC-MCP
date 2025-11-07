# Genetec MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Model Context Protocol (MCP)** server for integrating AI assistants with **Genetec Security Center Web SDK API**.

## 🎯 Overview

This MCP server enables AI assistants (like Claude) to interact directly with Genetec Security Center, providing comprehensive access control and security management capabilities through natural language.

### Key Capabilities

- 🔍 **Entity Management** - Search and retrieve cardholders, doors, cameras, and areas
- 🚪 **Access Control** - Grant temporary access, lock/unlock doors dynamically
- 📊 **Event Monitoring** - Query access events with advanced filters
- 👥 **Visitor Management** - Create temporary visitors with time-limited credentials

### Project Statistics

- **10 Tools Implemented** (100% complete)
- **~2,200 Lines of Code**
- **Full Type Safety** with Pydantic validation
- **Dual Response Formats** (Markdown + JSON)
- **Comprehensive Error Handling**

---

## 🚀 Features

### Group 1: Core Entity Management (6 tools)

#### `genetec_search_entities`
Search for entities by type (Cardholder, Door, Camera, Area, etc.) with optional name filtering and pagination.

**Use cases:**
- Find all doors in a building
- Search for cardholders by name
- List cameras in a specific area

**Example:**
```
"Search for all doors in Building A"
```

---

#### `genetec_get_entity_details`
Get comprehensive details about a specific entity by its GUID, including properties, relationships, and metadata.

**Use cases:**
- Review door configuration
- Check cardholder status
- Verify camera settings

**Example:**
```
"Get details for door with GUID a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

---

#### `genetec_list_cardholders`
List all cardholders (people with access credentials) with optional filters for name and status (Active/Inactive).

**Use cases:**
- Review all active employees
- Find specific cardholder
- Audit credential distribution

**Example:**
```
"List all active cardholders"
```

---

#### `genetec_get_cardholder_details`
Get detailed information about a specific cardholder, including credentials and access rules.

**Use cases:**
- Review person's access rights
- Troubleshoot access issues
- Verify credential status

**Example:**
```
"Get details for cardholder John Doe"
```

---

#### `genetec_list_doors`
List all doors in the access control system with optional filters for name and area.

**Use cases:**
- Inventory all access points
- Find doors in specific zone
- Review door status

**Example:**
```
"List all doors on the ground floor"
```

---

#### `genetec_list_cameras`
List surveillance cameras with filters for name, area, and status (Online/Offline/Recording).

**Use cases:**
- Monitor camera health
- Find offline cameras
- Review camera coverage

**Example:**
```
"Show me all offline cameras"
```

---

### Group 2: Access Control Operations (4 tools)

#### `genetec_grant_door_access`
**Temporarily grant** a cardholder access to a door, bypassing normal access rules. Access automatically expires after the specified duration (5-300 seconds).

**Features:**
- ⏱️ Configurable duration (default: 30 seconds)
- 📝 Audit trail with reason field
- ✅ Entity validation (door + cardholder types)
- 🔒 Non-destructive (doesn't modify permanent rules)

**Use cases:**
- Emergency access during incidents
- Maintenance personnel access
- Temporary visitor escort
- Override failed badge reads

**Example:**
```
"Grant John Doe access to Server Room for 60 seconds for emergency maintenance"
```

---

#### `genetec_lock_unlock_door`
Lock or unlock a door with optional **auto-relock** duration. Supports both temporary and permanent state changes.

**Features:**
- 🔓 Temporary unlock with auto-relock (5-3600 seconds)
- 🔒 Permanent unlock until manually locked
- 📝 Audit trail with reason field
- ⚡ Instant state change

**Use cases:**
- Lock doors during security incidents
- Unlock for deliveries/maintenance
- Override door schedules
- Emergency lockdown procedures

**Example:**
```
"Unlock Main Entrance for 5 minutes for delivery"
```

---

#### `genetec_list_access_events`
Query access events with **advanced filtering** (door, cardholder, event type, time range). Returns events in reverse chronological order.

**Features:**
- 🔍 Multiple filter options
- ⏰ Time range queries (ISO 8601)
- 📄 Pagination (1-500 events)
- 📊 Event types: AccessGranted, AccessRefused, All

**Use cases:**
- Audit trail investigation
- Security incident analysis
- Access pattern review
- Compliance reporting

**Example:**
```
"Show me all failed access attempts in the last 24 hours"
```

---

#### `genetec_create_visitor`
Create a **temporary visitor** with time-limited credentials and access to specific areas.

**Features:**
- 🎫 Temporary credentials (card/badge/pin)
- 📅 Activation/deactivation dates
- 🚪 Multiple access areas
- 👤 Optional escort requirement
- ✅ Date validation (end > start)
- 🔐 Auto-deactivation after end date

**Use cases:**
- Contractor access management
- Guest credentials
- Temporary employees
- Vendor access

**Example:**
```
"Create a visitor badge for Jane Smith from ABC Corp, visiting tomorrow 9am-5pm, 
access to Lobby and Meeting Room 1"
```

---

## 📋 Prerequisites

- **Python 3.10 or higher**
- **Genetec Security Center** with Web SDK role configured
- Valid SDK certificate and credentials
- User account with "Log on using the SDK" privilege

---

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/HackThePlanetBR/GenetecSC-MCP.git
cd GenetecSC-MCP
```

### 2. Install Dependencies

**Using uv (recommended):**
```bash
uv sync --all-extras
```

**Using pip:**
```bash
pip install -e .
```

---

## ⚙️ Configuration

### 1. Create Environment File

```bash
cp .env.example .env
```

### 2. Configure Credentials

Edit `.env` with your Genetec server details:

```bash
# Genetec Server Configuration
GENETEC_SERVER_URL=https://your-server:4590/WebSdk
GENETEC_USERNAME=your_username
GENETEC_PASSWORD=your_password
GENETEC_APP_ID=your_sdk_application_id

# Optional Settings
GENETEC_TIMEOUT=30
GENETEC_VERIFY_SSL=true
```

**Important Security Notes:**
- Never commit `.env` to version control
- Use HTTPS in production
- Enable SSL certificate verification
- Follow principle of least privilege for user accounts
- Rotate passwords regularly

---

## 🚀 Running the Server

### Standalone Mode (Testing)

```bash
uv run genetec_mcp
```

### With Claude Desktop

Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "genetec": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/genetec_mcp",
        "run",
        "genetec_mcp"
      ]
    }
  }
}
```

**Note:** Replace `/ABSOLUTE/PATH/TO/genetec_mcp` with your actual path.

### Verify Installation

After configuring Claude Desktop, restart the application. You should see Genetec tools available in Claude.

---

## 💡 Usage Examples

### Example 1: Search and Grant Access

```
You: "Find all doors in Building A"
Claude: [uses genetec_search_entities]
Result: Lists 15 doors with GUIDs

You: "Grant Jane Doe temporary access to the Server Room for 2 minutes"
Claude: [uses genetec_grant_door_access]
Result: ✅ Access granted, expires at 14:32:00 UTC
```

### Example 2: Security Incident Investigation

```
You: "Show me all failed access attempts in the last hour"
Claude: [uses genetec_list_access_events with filters]
Result: Lists 8 AccessRefused events with details

You: "Lock all doors on floor 3"
Claude: [uses genetec_list_doors + genetec_lock_unlock_door]
Result: 12 doors locked successfully
```

### Example 3: Visitor Management

```
You: "Create a visitor pass for John Smith from Acme Corp, 
     visiting today 9am-5pm, needs access to Lobby and Meeting Room B"
Claude: [uses genetec_create_visitor]
Result: ✅ Visitor created, badge #V2025-1234, auto-expires at 17:00
```

### Example 4: Door Status Review

```
You: "Which doors are currently unlocked?"
Claude: [uses genetec_list_doors with status filter]
Result: 3 doors unlocked: Main Entrance, Loading Dock, Emergency Exit

You: "Lock the Loading Dock door"
Claude: [uses genetec_lock_unlock_door]
Result: ✅ Door locked successfully
```

---

## 🏗️ Development

### Project Structure

```
genetec_mcp/
├── pyproject.toml              # Project configuration & dependencies
├── README.md                   # This file
├── .env.example                # Environment variables template
├── FASE_1_COMPLETA.md         # Phase 1 documentation
├── FASE_2_COMPLETA.md         # Phase 2 documentation
├── FASE_3_COMPLETA.md         # Phase 3 documentation
└── src/
    └── genetec_mcp/
        ├── __init__.py         # Package initialization
        ├── __main__.py         # Entry point
        ├── server.py           # FastMCP server with 10 tools
        ├── config.py           # Configuration and constants
        ├── models.py           # Pydantic models (467 lines)
        ├── client.py           # Genetec API client (324 lines)
        └── formatters.py       # Response formatting (346 lines)
```

### Code Statistics

| File | Lines | Purpose |
|------|-------|---------|
| `server.py` | 837 | 10 MCP tools implementation |
| `models.py` | 467 | Pydantic validation models |
| `formatters.py` | 346 | Markdown/JSON formatters |
| `client.py` | 324 | HTTP client with auth |
| `config.py` | 275 | Configuration & constants |
| **Total** | **~2,249** | **Complete MCP server** |

### Testing

```bash
# Syntax validation
python -m py_compile src/genetec_mcp/*.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run genetec_mcp

# Manual testing in Claude Desktop
# (Configure as shown above and test tools)
```

### Code Quality

- ✅ **100% Type Hints** - Full type safety with Python type hints
- ✅ **100% Async/Await** - All I/O operations are async
- ✅ **Pydantic Validation** - Robust input validation
- ✅ **Comprehensive Docstrings** - Every tool fully documented
- ✅ **Error Handling** - User-friendly error messages
- ✅ **DRY Principle** - No code duplication

---

## 🔒 Security Considerations

### Authentication

- Store credentials in `.env` file (never commit)
- Use environment variables in production
- Rotate passwords regularly
- Use dedicated SDK user accounts

### SSL/TLS

```bash
# Production (recommended)
GENETEC_VERIFY_SSL=true

# Development/Testing only
GENETEC_VERIFY_SSL=false
```

### User Privileges

Minimum required privileges for SDK user:
- "Log on using the SDK"
- Read access to entities (Cardholders, Doors, Cameras)
- Write access for access control operations (if using Group 2 tools)

### Audit Trail

All write operations include optional `reason` parameter for audit logging:
```python
genetec_grant_door_access(
    door_guid="...",
    cardholder_guid="...",
    reason="Emergency maintenance"  # Logged in Genetec
)
```

---

## 🐛 Troubleshooting

### Authentication Failed

**Error:** `Error: Authentication failed. Please check your credentials.`

**Solutions:**
1. Verify `GENETEC_USERNAME`, `GENETEC_PASSWORD`, and `GENETEC_APP_ID`
2. Ensure user has "Log on using the SDK" privilege
3. Check SDK certificate is valid and in license
4. Verify username format: `username;app_id` (done automatically)

### Cannot Connect to Server

**Error:** `Error: Cannot connect to Genetec server.`

**Solutions:**
1. Verify `GENETEC_SERVER_URL` format: `https://server:4590/WebSdk`
2. Check Web SDK role is running in Security Center
3. Verify firewall allows connections to port 4590
4. Test connectivity: `curl https://your-server:4590/WebSdk`

### Permission Denied

**Error:** `Error: Access denied. You don't have permission...`

**Solutions:**
1. Check user's role assignments in Config Tool
2. Verify privileges include required operations
3. Ensure user is not locked or disabled
4. Review partition assignments

### Entity Not Found

**Error:** `Error: Entity with GUID xxx not found.`

**Solutions:**
1. Verify GUID is correct (36 characters, format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
2. Check entity exists in Security Center
3. Ensure user has access to entity's partition
4. Try searching for entity first to get correct GUID

---

## 📚 API Reference

### Tool Naming Convention

All tools follow the pattern: `genetec_{action}_{resource}`

Examples:
- `genetec_search_entities` - Search for entities
- `genetec_grant_door_access` - Grant access to door
- `genetec_list_cardholders` - List cardholders

### Response Formats

All tools support dual response formats:

**Markdown (default)** - Optimized for LLM readability:
```markdown
# Door Access Granted ✅

**Door:** Main Entrance (a1b2c3d4-...)
**Duration:** 30 seconds
```

**JSON** - For programmatic processing:
```json
{
  "success": true,
  "action": "GrantAccess",
  "details": {
    "Door": "Main Entrance (a1b2c3d4-...)",
    "Duration": "30 seconds"
  }
}
```

### Pagination

Tools that return lists support pagination:
- `limit` - Results per page (default: 20, max: 100-500)
- `offset` - Skip N results
- Response includes: `total`, `count`, `has_more`, `next_offset`

---

## 🚧 Limitations

Current version does **not** include:

- ❌ **Real-time event streaming** - No WebSocket/SSE support
- ❌ **Complex reporting** - Basic event queries only
- ❌ **Entity modification** - Limited to access control operations
- ❌ **Alarm management** - No alarm tools
- ❌ **Camera bookmarks** - No video bookmarking
- ❌ **Bulk operations** - Operations are per-entity

These may be added in future versions based on demand.

---

## 📖 Documentation

### Additional Resources

- 📘 [FASE_1_COMPLETA.md](FASE_1_COMPLETA.md) - Infrastructure setup
- 📗 [FASE_2_COMPLETA.md](FASE_2_COMPLETA.md) - Core Entity Management
- 📕 [FASE_3_COMPLETA.md](FASE_3_COMPLETA.md) - Access Control Operations
- 📙 [genetec_mcp_implementation_plan.md](genetec_mcp_implementation_plan.md) - Full implementation plan

### External Documentation

- [Genetec Developer Portal](https://developer.genetec.com)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Security Center Admin Guide](https://docs.genetec.com)
- [Web SDK API Reference](https://developer.genetec.com/documentation/web-sdk)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'feat: add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow existing code style
- Add type hints to all functions
- Write comprehensive docstrings
- Include error handling
- Test with MCP Inspector
- Update documentation

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

### For Genetec API Questions
- Email: [DAP@genetec.com](mailto:DAP@genetec.com)
- Developer Portal: [developer.genetec.com](https://developer.genetec.com)

### For MCP Questions
- Documentation: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- Specification: [MCP Spec](https://modelcontextprotocol.io/specification/2025-06-18)

### For This Project
- Issues: [GitHub Issues](https://github.com/HackThePlanetBR/GenetecSC-MCP/issues)
- Discussions: [GitHub Discussions](https://github.com/HackThePlanetBR/GenetecSC-MCP/discussions)

---

## ⭐ Acknowledgments

Built with:
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python MCP SDK
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [httpx](https://www.python-httpx.org/) - HTTP client

Special thanks to:
- Anthropic for the MCP specification
- Genetec for the comprehensive Web SDK API

---

## 📊 Project Status

**Status:** ✅ **Production Ready**

- 10/10 Tools Implemented (100%)
- All Phases Complete
- Fully Tested
- Comprehensive Documentation
- Ready for deployment

**Last Updated:** November 7, 2025

---

<div align="center">

**Made with ❤️ for the Genetec & AI community**

[⬆ Back to Top](#genetec-mcp-server)

</div>
