#!/usr/bin/env python3
"""
Test script for the Cursor DB MCP server.
This script starts the MCP server and performs tests using the MCP Python SDK.
"""

import subprocess
import time
import sys
import os
import json
import asyncio
from pathlib import Path

# Import MCP client libraries with correct paths
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server using the Python SDK"""
    print("Starting Cursor DB MCP server test...")
    
    try:
        print("\nTesting MCP server with the Python SDK...")
        
        # Use stdio_client to start the server and connect to it
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["cursor-db-mcp-server.py"],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            print("✅ Successfully started MCP server process")
            
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Successfully initialized connection to MCP server")
                
                # Test 1: List available resources
                print("\n1. Testing resource listing...")
                resources = await session.list_resources()
                
                if resources and any(hasattr(r, 'uri') and "cursor://projects" in r.uri for r in resources):
                    print("✅ Successfully listed resources")
                    print(f"Resources: {[getattr(r, 'uri', str(r)) for r in resources]}")
                else:
                    print("❌ Failed to find expected resources")
                    print(f"Resources found: {resources}")
                
                # Test 2: List available tools
                print("\n2. Testing tool listing...")
                tools = await session.list_tools()
                
                if tools and any(hasattr(t, 'name') and "query_table" in t.name for t in tools):
                    print("✅ Successfully listed tools")
                    print(f"Tools: {[getattr(t, 'name', str(t)) for t in tools]}")
                else:
                    print("❌ Failed to find expected tools")
                    print(f"Tools found: {tools}")
                
                # Test 3: List available prompts
                print("\n3. Testing prompt listing...")
                prompts = await session.list_prompts()
                
                if prompts and any(hasattr(p, 'name') and "explore_cursor_projects" in p.name for p in prompts):
                    print("✅ Successfully listed prompts")
                    print(f"Prompts: {[getattr(p, 'name', str(p)) for p in prompts]}")
                else:
                    print("❌ Failed to find expected prompts")
                    print(f"Prompts found: {prompts}")
                
                # Test 4: Call a tool
                print("\n4. Testing tool execution...")
                try:
                    # Get list of projects first
                    projects_result = await session.call_tool("cursorprojects")
                    
                    if projects_result and isinstance(projects_result, list):
                        print("✅ Successfully called cursorprojects tool")
                        print(f"Projects: {projects_result}")
                        
                        # If we have projects, try querying one
                        if projects_result:
                            project_name = projects_result[0]  # Use the first project
                            query_result = await session.call_tool(
                                "query_table", 
                                arguments={
                                    "project_name": project_name,
                                    "table_name": "ItemTable",
                                    "query_type": "get_all",
                                    "limit": 5
                                }
                            )
                            
                            if query_result:
                                print("✅ Successfully queried project database")
                                print(f"Query result: {query_result[:2]}...")  # Show first 2 items
                            else:
                                print("❌ Failed to query project database")
                    else:
                        print("❌ Failed to call cursorprojects tool")
                        print(f"Result: {projects_result}")
                except Exception as e:
                    print(f"❌ Error calling tool: {e}")
                
                # Test 5: Read a resource
                print("\n5. Testing resource reading...")
                try:
                    # Try to read the projects resource
                    content, mime_type = await session.read_resource("cursor://projects")
                    
                    if content:
                        print("✅ Successfully read cursor://projects resource")
                        print(f"Content type: {mime_type}")
                        print(f"Content preview: {content[:100]}...")  # Show first 100 chars
                    else:
                        print("❌ Failed to read cursor://projects resource")
                except Exception as e:
                    print(f"❌ Error reading resource: {e}")
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        
    print("Test completed.")


def main():
    """Main entry point"""
    asyncio.run(test_mcp_server())


if __name__ == "__main__":
    main() 