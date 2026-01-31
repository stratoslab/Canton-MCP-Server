# Canton Ledgerview MCP Server

This is a custom Model Context Protocol (MCP) server for the Ledgerview project. It provides tools to analyze the project structure and status.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (for Python dependency management)

## Installation

Clone the repository:
```bash
git clone https://github.com/stratoslab/Canton-MCP-Server.git
cd Canton-MCP-Server
```

## Running the Server

You can run the server directly using `uv`:

```bash
uv run src/server.py
```

## Setup with Claude Desktop / generic MCP Client

Add the following to your MCP settings file (e.g., `~/Library/Application Support/Code/User/globalStorage/rooveterinary.roo-cline/settings/cline_mcp_settings.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "canton-ledgerview": {
      "command": "uv",
      "args": [
        "run",
        "src/server.py"
      ],
      "cwd": "/absolute/path/to/Canton-MCP-Server"
    }
  }
}
```

## Available Tools

- `get_project_summary`: Returns a summary of the project (name, dependencies, file count).
- `check_server_status`: Returns "OK" if reachable.

