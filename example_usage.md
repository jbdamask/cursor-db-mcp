# Example Usage with Claude

This document demonstrates how to interact with the Cursor DB MCP server through Claude.

## Install the server in Claude Desktop:

```bash
mcp install cursor-db-mcp-server.py
```

## Example Interactions

### Listing Projects

**User**: "Can you show me a list of my Cursor projects?"

**Claude**: 
```
I'll retrieve a list of your Cursor projects.

Here are the Cursor projects I found:
- project1 (path: /Users/username/Library/Application Support/Cursor/User/workspaceStorage/abc123/state.vscdb)
- project2 (path: /Users/username/Library/Application Support/Cursor/User/workspaceStorage/def456/state.vscdb)
- custom-project (path: /Users/username/code/custom-project/state.vscdb)
```

### Viewing Chat History

**User**: "Show me the chat history from my 'project1' project."

**Claude**:
```
I'll retrieve the chat history from your 'project1' project.

Here's the chat history I found:

Chat: "Understanding React Hooks"
- You: "Can you explain how useEffect works in React?"
- Claude: "The useEffect hook in React is used for handling side effects in functional components..."

Chat: "Debugging API Connection"
- You: "I'm getting a 401 error when connecting to the API. Here's my code..."
- Claude: "It looks like you're missing the authorization header in your request..."
```

### Querying Database Tables

**User**: "Can you search for keys related to 'settings' in the ItemTable of my 'project1' project?"

**Claude**:
```
I'll search for keys related to 'settings' in the ItemTable of your 'project1' project.

Here are the results:
1. Key: "workbench.settings.editor"
   Value: {"mode": "ui", "lastFocusedSettingId": "editor.fontSize"}

2. Key: "settings.language"
   Value: "en"

3. Key: "settings.theme"
   Value: "dark"
```

### Analyzing Chat Data

**User**: "Can you analyze the chat data from my 'project1' project and tell me what topics I've been discussing most frequently?"

**Claude**:
```
I'll analyze the chat data from your 'project1' project.

Based on your chat history, here are the most frequent topics you've been discussing:
1. React Hooks and Components (5 conversations)
2. API Integration (3 conversations)
3. CSS Styling (2 conversations)
4. Performance Optimization (2 conversations)
5. Debugging (1 conversation)

The most common questions were about state management in React and handling API responses.
``` 