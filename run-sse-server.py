#!/usr/bin/env python
import os
import sys
import logging
from mcp.server.sse import SseServerTransport
from mcp.server.fastmcp import FastMCP
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('sse-server')

def main():
    # Load the MCP server module
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cursor-db-mcp-server.py")
    spec = importlib.util.spec_from_file_location("cursor_db_mcp_server", server_path)
    server_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_module)
    
    # Get the MCP server instance
    mcp = server_module.mcp
    
    # Set up SSE transport
    port = 8765
    logger.info(f"Starting SSE server on port {port}")
    
    # Create an SSE transport
    transport = SseServerTransport(endpoint="/sse")
    
    # The SSE server will be available at http://localhost:8765/sse
    logger.info(f"SSE URL: http://localhost:{port}/sse")
    
    # Run the server
    mcp.run(transport)

if __name__ == "__main__":
    main() 