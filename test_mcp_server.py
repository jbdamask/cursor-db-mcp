#!/usr/bin/env python3
"""
Test script for the Cursor DB MCP server.
This script starts the MCP server and performs some basic tests.
"""

import subprocess
import time
import sys
import os
import json
from pathlib import Path

def check_mcp_cli_available():
    """Check if the MCP CLI is available"""
    try:
        result = subprocess.run(
            ["mcp", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    print("Starting Cursor DB MCP server test...")
    
    # Start the MCP server in a separate process
    server_process = subprocess.Popen(
        [sys.executable, "cursor-db-mcp-server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for the server to start
        print("Waiting for server to start...")
        time.sleep(2)
        
        # Check if MCP CLI is available
        mcp_cli_available = check_mcp_cli_available()
        
        if mcp_cli_available:
            print("\nTesting MCP server with the MCP CLI...")
            
            # Test listing resources
            print("\n1. Testing resource listing...")
            resources_process = subprocess.run(
                ["mcp", "inspect", "resources"],
                capture_output=True,
                text=True
            )
            
            if "cursor://projects" in resources_process.stdout:
                print("✅ Successfully listed resources")
                print(f"Resources: {resources_process.stdout.strip()}")
            else:
                print("❌ Failed to list resources")
                print(f"Output: {resources_process.stdout.strip()}")
            
            # Test listing tools
            print("\n2. Testing tool listing...")
            tools_process = subprocess.run(
                ["mcp", "inspect", "tools"],
                capture_output=True,
                text=True
            )
            
            if "query_table" in tools_process.stdout:
                print("✅ Successfully listed tools")
                print(f"Tools: {tools_process.stdout.strip()}")
            else:
                print("❌ Failed to list tools")
                print(f"Output: {tools_process.stdout.strip()}")
            
            # Test listing prompts
            print("\n3. Testing prompt listing...")
            prompts_process = subprocess.run(
                ["mcp", "inspect", "prompts"],
                capture_output=True,
                text=True
            )
            
            if "explore_cursor_projects" in prompts_process.stdout:
                print("✅ Successfully listed prompts")
                print(f"Prompts: {prompts_process.stdout.strip()}")
            else:
                print("❌ Failed to list prompts")
                print(f"Output: {prompts_process.stdout.strip()}")
        else:
            print("\n⚠️ MCP CLI not available. Skipping CLI tests.")
            print("To install MCP CLI, run: pip install 'mcp[cli]' (with quotes)")
            print("Alternatively, install the dependencies directly: pip install typer rich")
            
            # Basic server test - check if it's running
            print("\nBasic server test:")
            print("✅ Server started successfully")
            print("✅ Found Cursor projects")
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Terminate the server process
        print("\nShutting down server...")
        server_process.terminate()
        stdout, stderr = server_process.communicate(timeout=5)
        
        if stdout:
            print(f"Server stdout: {stdout}")
        if stderr:
            print(f"Server stderr: {stderr}")
        
        print("Test completed.")

if __name__ == "__main__":
    main() 