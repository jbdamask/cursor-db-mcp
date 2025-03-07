# Note - this is currently just a web service. It is NOT an MCP server yet

# Cursor Database MCP (Management Control Panel)

A lightweight API server for accessing and querying Cursor IDE's SQLite databases. This tool allows you to retrieve chat and composer data from Cursor projects without directly interacting with the underlying SQLite databases.

## Overview

Cursor IDE stores various data in SQLite databases located in the user's application support directory. This includes:

- **Project-specific data**: Stored in `workspaceStorage/<workspace-id>/state.vscdb`
- **Global data**: Stored in `globalStorage/state.vscdb`

This tool provides a simple REST API to access this data, making it easier to retrieve and analyze your Cursor IDE usage, including AI chat conversations and composer sessions.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cursor-db-mcp.git
   cd cursor-db-mcp
   ```

2. Install dependencies:
   ```
   pip install flask
   ```

## Usage

### Starting the Server

```bash
python cursor-data-mcp-server.py [options]
```

Options:
- `--host`: Host to run the server on (default: 127.0.0.1)
- `--port`: Port to run the server on (default: 5000)
- `--cursor-path`: Path to Cursor User directory (e.g., ~/Library/Application Support/Cursor/User/)
- `--project-dirs`: List of additional Cursor project directories to scan

If `--cursor-path` is not specified, the server will attempt to detect the default Cursor path based on your operating system:
- macOS: `~/Library/Application Support/Cursor/User`
- Windows: `~/AppData/Roaming/Cursor/User`
- Linux: `~/.config/Cursor/User`

### API Endpoints

#### List All Projects

```
GET /projects
```

Returns a list of all detected Cursor projects and their database paths.

Example request:
```bash
curl http://localhost:5000/projects
```

Example response:
```json
{
  "cursor-chat-browser": "/Users/username/Library/Application Support/Cursor/User/workspaceStorage/abc123/state.vscdb",
  "cursor-db-mcp": "/Users/username/Library/Application Support/Cursor/User/workspaceStorage/def456/state.vscdb"
}
```

For more detailed information, use the `detailed` query parameter:

```bash
curl http://localhost:5000/projects?detailed=true
```

#### Retrieve Chat Data from a Project

```
GET /projects/<project_name>/chat
```

Retrieves all AI chat data from a specific project.

Example request:
```bash
curl http://localhost:5000/projects/cursor-chat-browser/chat
```

Example response:
```json
{
  "tabs": [
    {
      "tabId": "636eac61-69dc-4b77-ae64-26cfa7d557fd",
      "chatTitle": "Understanding the 'asChild' Prop in Button Component",
      "bubbles": [
        {
          "selections": [...],
          "text": "What does the asChild prop do in this Button component?",
          "type": 1
        },
        {
          "text": "The `asChild` prop in the Button component...",
          "type": 2
        }
      ]
    }
  ]
}
```

#### Retrieve Composer IDs from a Project

```
GET /projects/<project_name>/composers
```

Retrieves all composer IDs and related data from a specific project.

Example request:
```bash
curl http://localhost:5000/projects/cursor-chat-browser/composers
```

Example response:
```json
{
  "composer_ids": [
    "245ba35e-de7e-42d4-b35a-dd5ac10cdef7",
    "193af03f-0b57-4dea-ab62-5331f98ba4cc",
    "4de0a10c-a70e-46b7-8392-228561f714d6"
  ],
  "full_data": {
    "allComposers": [
      {
        "type": "head",
        "composerId": "245ba35e-de7e-42d4-b35a-dd5ac10cdef7",
        "name": "Professional Form Layout Enhancement",
        "lastUpdatedAt": 1741020042402,
        "createdAt": 1741017278208,
        "unifiedMode": "agent",
        "forceMode": "edit"
      },
      ...
    ],
    "selectedComposerId": "193af03f-0b57-4dea-ab62-5331f98ba4cc"
  }
}
```

#### Retrieve Composer Data from Global Storage

```
GET /composers/<composer_id>
```

Retrieves detailed data for a specific composer session from the global storage database.

Example request:
```bash
curl http://localhost:5000/composers/362d91aa-2339-4382-8173-8044ac63bca2
```

Example response:
```json
{
  "composer_id": "362d91aa-2339-4382-8173-8044ac63bca2",
  "data": {
    "composerId": "362d91aa-2339-4382-8173-8044ac63bca2",
    "richText": "...",
    "hasLoaded": true,
    "text": "",
    "conversation": [
      {
        "type": 1,
        "bubbleId": "6fdeddb3-9707-4d25-a4a3-81e5675dd876",
        "text": "replace this date window with just today",
        "relevantFiles": [...]
      },
      {
        "type": 2,
        "bubbleId": "2797fa2c-c3a0-4d63-87fe-d37df7cb1dd5",
        "text": "I'll modify the `getDefaultDateRange` function...",
        "codeBlocks": [...]
      }
    ],
    "status": "completed"
  }
}
```

#### Query a Specific Table in a Project's Database

```
GET /projects/<project_name>/tables/<table_name>
```

Queries a specific table in a project's database. The table name must be either `ItemTable` or `cursorDiskKV`.

Parameters:
- `query_type`: Type of query (`get_all`, `get_by_key`, `search_keys`). Default: `get_all`
- `key`: Key to search for when using `get_by_key` or `search_keys`
- `limit`: Maximum number of results to return. Default: 100

Example request:
```bash
curl "http://localhost:5000/projects/cursor-chat-browser/tables/ItemTable?query_type=search_keys&key=workbench"
```

Example response:
```json
[
  {
    "key": "workbench.panel.aichat.view.aichat.chatdata",
    "value": {
      "tabs": [...]
    }
  },
  {
    "key": "workbench.view.explorer",
    "value": {
      "collapsed": false
    }
  }
]
```

#### Refresh Database Paths

```
GET /refresh
```

Refreshes the list of database paths by rescanning the Cursor directory and project directories.

Example request:
```bash
curl http://localhost:5000/refresh
```

Example response:
```json
{
  "message": "Database paths refreshed",
  "projects": {
    "cursor-chat-browser": "/Users/username/Library/Application Support/Cursor/User/workspaceStorage/abc123/state.vscdb",
    "cursor-db-mcp": "/Users/username/Library/Application Support/Cursor/User/workspaceStorage/def456/state.vscdb"
  }
}
```

## Use Cases

- **Analyzing Chat History**: Extract and analyze your AI chat conversations to understand your usage patterns.
- **Backing Up Composer Sessions**: Save your composer sessions for future reference or backup.
- **Data Mining**: Extract insights from your coding sessions and AI interactions.
- **Integration with Other Tools**: Use the API to integrate Cursor data with other tools or dashboards.

## Limitations

- This tool is read-only and does not modify any Cursor databases.
- The structure of Cursor's databases may change with updates to the IDE.
- Large responses may be slow to process, especially for projects with extensive chat or composer history.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 