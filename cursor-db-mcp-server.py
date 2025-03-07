import os
import json
import sqlite3
import platform
import re
from flask import Flask, request, jsonify
from pathlib import Path
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cursor-mcp')

app = Flask(__name__)

class CursorDBManager:
    def __init__(self, cursor_path=None, project_dirs=None):
        """
        Initialize the CursorDBManager with a Cursor main directory and/or list of project directories.
        
        Args:
            cursor_path (str): Path to main Cursor directory (e.g. ~/Library/Application Support/Cursor/User/)
            project_dirs (list): List of paths to Cursor project directories containing state.vscdb files
        """
        if cursor_path:
            self.cursor_path = Path(cursor_path).expanduser().resolve()
        else:
            # Try to get the default cursor path
            self.cursor_path = self.get_default_cursor_path()
            
        self.project_dirs = project_dirs or []
        self.db_paths = {}
        self.projects_info = {}
        self.global_db_path = None
        self.refresh_db_paths()
    
    def get_default_cursor_path(self):
        """Return the default Cursor path based on the operating system"""
        system = platform.system()
        home = Path.home()
        
        default_path = None
        if system == "Darwin":  # macOS
            default_path = home / "Library/Application Support/Cursor/User"
        elif system == "Windows":
            default_path = home / "AppData/Roaming/Cursor/User"
        elif system == "Linux":
            default_path = home / ".config/Cursor/User"
        else:
            logger.warning(f"Unknown operating system: {system}. Cannot determine default Cursor path.")
            return None
        
        logger.info(f"Detected default Cursor path for {system}: {default_path}")
        return default_path
    
    def detect_cursor_projects(self):
        """Detect Cursor projects by scanning the workspaceStorage directory"""
        if not self.cursor_path:
            logger.error("No Cursor path available")
            return []
            
        # Check if the path exists
        if not self.cursor_path.exists():
            logger.error(f"Cursor path does not exist: {self.cursor_path}")
            return []
                
        workspace_storage = self.cursor_path / "workspaceStorage"
        if not workspace_storage.exists():
            logger.warning(f"Workspace storage directory not found: {workspace_storage}")
            return []
            
        logger.info(f"Found workspace storage directory: {workspace_storage}")
        
        projects = []
        
        # Scan all subdirectories in workspaceStorage
        for workspace_dir in workspace_storage.iterdir():
            if not workspace_dir.is_dir():
                continue
                
            workspace_json = workspace_dir / "workspace.json"
            state_db = workspace_dir / "state.vscdb"
            
            if workspace_json.exists() and state_db.exists():
                try:
                    with open(workspace_json, 'r') as f:
                        workspace_data = json.load(f)
                        
                    folder_uri = workspace_data.get("folder")
                    if folder_uri:
                        # Extract the project name from the URI
                        # For "file:///Users/johndamask/code/cursor-chat-browser", get "cursor-chat-browser"
                        project_name = folder_uri.rstrip('/').split('/')[-1]
                        
                        projects.append({
                            "name": project_name,
                            "db_path": str(state_db),
                            "workspace_dir": str(workspace_dir),
                            "folder_uri": folder_uri
                        })
                        logger.info(f"Found project: {project_name} at {state_db}")
                except Exception as e:
                    logger.error(f"Error processing workspace: {workspace_dir}: {e}")
        
        return projects
        
    def refresh_db_paths(self):
        """Scan project directories and identify all state.vscdb files"""
        self.db_paths = {}
        self.projects_info = {}
        
        # First, detect projects from the Cursor directory
        if self.cursor_path:
            cursor_projects = self.detect_cursor_projects()
            for project in cursor_projects:
                project_name = project["name"]
                self.db_paths[project_name] = project["db_path"]
                self.projects_info[project_name] = project
            
            # Set the global storage database path
            global_storage_path = self.cursor_path / "globalStorage" / "state.vscdb"
            if global_storage_path.exists():
                self.global_db_path = str(global_storage_path)
                logger.info(f"Found global storage database at {self.global_db_path}")
            else:
                logger.warning(f"Global storage database not found at {global_storage_path}")
        
        # Then add explicitly specified project directories
        for project_dir in self.project_dirs:
            project_path = Path(project_dir).expanduser().resolve()
            db_path = project_path / "state.vscdb"
            
            if db_path.exists():
                project_name = project_path.name
                self.db_paths[project_name] = str(db_path)
                self.projects_info[project_name] = {
                    "name": project_name,
                    "db_path": str(db_path),
                    "workspace_dir": None,
                    "folder_uri": None
                }
                logger.info(f"Found database: {project_name} at {db_path}")
            else:
                logger.warning(f"No state.vscdb found in {project_path}")
        
    def add_project_dir(self, project_dir):
        """Add a new project directory to the manager"""
        project_path = Path(project_dir).expanduser().resolve()
        if project_path not in self.project_dirs:
            self.project_dirs.append(project_path)
            self.refresh_db_paths()
        return len(self.db_paths)
    
    def list_projects(self, detailed=False):
        """
        Return list of available projects
        
        Args:
            detailed (bool): Whether to return detailed project information
            
        Returns:
            dict: Project information (either just DB paths or full details)
        """
        if detailed:
            return self.projects_info
        return self.db_paths
    
    def execute_query(self, project_name, table_name, query_type, key=None, limit=100):
        """
        Execute a query against a specific project's database
        
        Args:
            project_name (str): Name of the project (key in db_paths)
            table_name (str): Either 'ItemTable' or 'cursorDiskKV'
            query_type (str): Type of query ('get_all', 'get_by_key', 'search_keys')
            key (str, optional): Key to search for when using 'get_by_key' or 'search_keys'
            limit (int): Maximum number of results to return
            
        Returns:
            list: Query results
        """
        if project_name not in self.db_paths:
            raise ValueError(f"Project '{project_name}' not found")
            
        if table_name not in ["ItemTable", "cursorDiskKV"]:
            raise ValueError("Table name must be either 'ItemTable' or 'cursorDiskKV'")
        
        db_path = self.db_paths[project_name]
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if query_type == "get_all":
                cursor.execute(f"SELECT key, value FROM {table_name} LIMIT ?", (limit,))
            elif query_type == "get_by_key" and key:
                cursor.execute(f"SELECT key, value FROM {table_name} WHERE key = ?", (key,))
            elif query_type == "search_keys" and key:
                search_term = f"%{key}%"
                cursor.execute(f"SELECT key, value FROM {table_name} WHERE key LIKE ? LIMIT ?", 
                              (search_term, limit))
            else:
                raise ValueError("Invalid query type or missing key parameter")
                
            results = []
            for row in cursor.fetchall():
                key, value = row
                try:
                    # Try to parse JSON value
                    parsed_value = json.loads(value)
                    results.append({"key": key, "value": parsed_value})
                except json.JSONDecodeError:
                    # If not valid JSON, return as string
                    results.append({"key": key, "value": value})
            
            conn.close()
            return results
            
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise
    
    def get_chat_data(self, project_name):
        """
        Retrieve AI chat data from a project
        
        Args:
            project_name (str): Name of the project
            
        Returns:
            dict: Chat data from the project
        """
        if project_name not in self.db_paths:
            raise ValueError(f"Project '{project_name}' not found")
        
        try:
            results = self.execute_query(
                project_name, 
                "ItemTable", 
                "get_by_key", 
                "workbench.panel.aichat.view.aichat.chatdata"
            )
            
            if results and len(results) > 0:
                return results[0]["value"]
            else:
                return {"error": "No chat data found for this project"}
                
        except Exception as e:
            logger.error(f"Error retrieving chat data: {e}")
            raise
    
    def get_composer_ids(self, project_name):
        """
        Retrieve composer IDs from a project
        
        Args:
            project_name (str): Name of the project
            
        Returns:
            list: List of composer IDs
        """
        if project_name not in self.db_paths:
            raise ValueError(f"Project '{project_name}' not found")
        
        try:
            results = self.execute_query(
                project_name, 
                "ItemTable", 
                "get_by_key", 
                "composer.composerData"
            )
            
            if results and len(results) > 0:
                composer_data = results[0]["value"]
                # Extract composer IDs from the data
                composer_ids = []
                if "allComposers" in composer_data:
                    for composer in composer_data["allComposers"]:
                        if "composerId" in composer:
                            composer_ids.append(composer["composerId"])
                return {
                    "composer_ids": composer_ids,
                    "full_data": composer_data
                }
            else:
                return {"error": "No composer data found for this project"}
                
        except Exception as e:
            logger.error(f"Error retrieving composer IDs: {e}")
            raise
    
    def get_composer_data(self, composer_id):
        """
        Retrieve composer data from global storage
        
        Args:
            composer_id (str): Composer ID
            
        Returns:
            dict: Composer data
        """
        if not self.global_db_path:
            raise ValueError("Global storage database not found")
        
        try:
            conn = sqlite3.connect(self.global_db_path)
            cursor = conn.cursor()
            
            key = f"composerData:{composer_id}"
            cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                try:
                    return {"composer_id": composer_id, "data": json.loads(row[0])}
                except json.JSONDecodeError:
                    return {"composer_id": composer_id, "data": row[0]}
            else:
                return {"error": f"No data found for composer ID: {composer_id}"}
                
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise

# Initialize the DB manager (will be configured in main())

@app.route('/projects', methods=['GET'])
def list_projects():
    """List all available projects and their database paths"""
    detailed = request.args.get('detailed', 'false').lower() == 'true'
    return jsonify(db_manager.list_projects(detailed))

@app.route('/projects/<project_name>/chat', methods=['GET'])
def get_project_chat(project_name):
    """Retrieve AI chat data from a project"""
    try:
        chat_data = db_manager.get_chat_data(project_name)
        return jsonify(chat_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error retrieving chat data: {str(e)}"}), 500

@app.route('/projects/<project_name>/composers', methods=['GET'])
def get_project_composers(project_name):
    """Retrieve composer IDs from a project"""
    try:
        composer_data = db_manager.get_composer_ids(project_name)
        return jsonify(composer_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error retrieving composer data: {str(e)}"}), 500

@app.route('/composers/<composer_id>', methods=['GET'])
def get_composer_data(composer_id):
    """Retrieve composer data from global storage"""
    try:
        composer_data = db_manager.get_composer_data(composer_id)
        return jsonify(composer_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error retrieving composer data: {str(e)}"}), 500

@app.route('/projects/<project_name>/tables/<table_name>', methods=['GET'])
def query_table(project_name, table_name):
    """Query a specific table in a project's database"""
    query_type = request.args.get('query_type', 'get_all')
    key = request.args.get('key')
    limit = int(request.args.get('limit', 100))
    
    try:
        results = db_manager.execute_query(project_name, table_name, query_type, key, limit)
        return jsonify(results)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/refresh', methods=['GET'])
def refresh_databases():
    """Refresh the list of database paths"""
    db_manager.refresh_db_paths()
    return jsonify({
        "message": "Database paths refreshed",
        "projects": db_manager.list_projects()
    })

def main():
    parser = argparse.ArgumentParser(description='Cursor IDE SQLite Database Query Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--cursor-path', help='Path to Cursor User directory (e.g. ~/Library/Application Support/Cursor/User/)')
    parser.add_argument('--project-dirs', nargs='+', help='List of additional Cursor project directories to scan')
    
    args = parser.parse_args()
    
    # Initialize the DB manager with the Cursor path
    global db_manager
    db_manager = CursorDBManager(cursor_path=args.cursor_path)
    
    # Add explicitly specified project directories
    if args.project_dirs:
        for project_dir in args.project_dirs:
            db_manager.add_project_dir(project_dir)
    
    # Log detected Cursor path
    if db_manager.cursor_path:
        logger.info(f"Using Cursor path: {db_manager.cursor_path}")
    else:
        logger.warning("No Cursor path specified or detected")
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"Available projects: {list(db_manager.list_projects().keys())}")
    
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()