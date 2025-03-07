#!/usr/bin/env python3
"""
Installation script for the Cursor DB MCP server.
This script installs all the necessary dependencies, including the MCP CLI.
"""

import subprocess
import sys
import os

def main():
    print("Installing Cursor DB MCP server dependencies...")
    
    # Install basic dependencies
    print("\nInstalling basic dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Install MCP CLI dependencies
    print("\nInstalling MCP CLI dependencies...")
    try:
        # Try to install with quotes to handle square brackets
        subprocess.run([sys.executable, "-m", "pip", "install", "mcp[cli]"])
    except Exception:
        # If that fails, install the dependencies directly
        print("Direct installation of mcp[cli] failed. Installing CLI dependencies individually...")
        subprocess.run([sys.executable, "-m", "pip", "install", "typer>=0.9.0", "rich>=13.0.0"])
    
    print("\nInstallation completed!")
    print("You can now run the MCP server with: python cursor-db-mcp-server.py")
    print("Or test it with: python test_mcp_server.py")

if __name__ == "__main__":
    main() 