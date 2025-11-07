"""Entry point for running the Genetec MCP server."""

from .server import mcp

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    mcp.run()