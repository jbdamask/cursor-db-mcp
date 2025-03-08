#!/usr/bin/env python3
"""
Installation script for the Cursor DB MCP server.
This script creates a virtual environment and installs all necessary dependencies,
including the MCP CLI, into that isolated environment.
"""

import subprocess
import sys
import os
import platform
import shutil
import site

def create_and_setup_venv():
    """Create a virtual environment and return the path to its Python executable."""
    venv_dir = ".venv"
    
    # Check if venv already exists
    if os.path.exists(venv_dir):
        print(f"Virtual environment already exists at ./{venv_dir}")
        should_recreate = input("Do you want to recreate it? (y/n): ").lower().strip()
        if should_recreate == 'y':
            print(f"Removing existing virtual environment at ./{venv_dir}...")
            shutil.rmtree(venv_dir)
        else:
            print(f"Using existing virtual environment at ./{venv_dir}")
    
    # Create venv if it doesn't exist or was removed
    if not os.path.exists(venv_dir):
        print(f"\nCreating virtual environment in ./{venv_dir}...")
        try:
            # Use the built-in venv module
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        except subprocess.CalledProcessError:
            print("Failed to create virtual environment using venv module.")
            print("Please make sure you have the venv module installed.")
            sys.exit(1)
    
    # Determine the path to the Python executable in the virtual environment
    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_path = os.path.join(venv_dir, "bin", "python")
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # Verify the virtual environment was created successfully
    if not os.path.exists(python_path):
        print(f"Error: Could not find Python executable at {python_path}")
        print("Virtual environment creation may have failed.")
        sys.exit(1)
        
    return python_path

def main():
    print("Setting up Cursor DB MCP server...")
    
    # Create virtual environment and get the Python path
    python_path = create_and_setup_venv()
    
    # Upgrade pip in the virtual environment
    print("\nUpgrading pip in the virtual environment...")
    subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install basic dependencies
    print("\nInstalling basic dependencies...")
    subprocess.check_call([python_path, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Install MCP CLI dependencies
    print("\nInstalling MCP CLI dependencies...")
    try:
        # Try to install with quotes to handle square brackets
        subprocess.check_call([python_path, "-m", "pip", "install", "mcp[cli]"])
    except subprocess.CalledProcessError:
        # If that fails, install the dependencies directly
        print("Direct installation of mcp[cli] failed. Installing CLI dependencies individually...")
        subprocess.check_call([python_path, "-m", "pip", "install", "mcp", "typer>=0.9.0", "rich>=13.0.0"])
    
    print("\nInstallation completed successfully!")
    
    # Print activation instructions
    venv_dir = "venv"
    print(f"\nTo use the Cursor DB MCP server, you need to activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"    {venv_dir}\\Scripts\\activate")
    else:
        print(f"    source {venv_dir}/bin/activate")
    
    print("\nAfter activation, you can test the MCP server with:")
    print("    python test_mcp_server.py")


if __name__ == "__main__":
    main() 