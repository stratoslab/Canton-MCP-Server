# Canton Ledgerview MCP Server

This is a custom Model Context Protocol (MCP) server for the Ledgerview project. It provides tools to analyze the project structure and status with full HTTP API integration.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (for Python dependency management)
- Docker (for containerized deployment)

## Quick Start with Docker

```bash
git clone https://github.com/stratoslab/Canton-MCP-Server.git
cd Canton-MCP-Server
docker build -t canton-mcp-server .
docker run -d -p 8000:8000 --name canton-mcp canton-mcp-server
```

Server will be available at `http://localhost:8000`

## Local Development

Run the server directly using `uv`:

```bash
uv run src/server.py
```

## MCP Client Setup

Add the following to your MCP settings file (e.g., `claude_desktop_config.json`):

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

## HTTP API Integration

The server provides REST endpoints for AI agents and web applications:

### Tool Execution
Execute any MCP tool via HTTP:

```bash
POST /tools/{tool_name}/call
Content-Type: application/json

{
  "arguments": {
    "arg1": "value1",
    "arg2": "value2"
  }
}
```

**Example - DAML Safety Analysis:**
```bash
curl -X POST http://localhost:8000/tools/analyze_daml_safety/call \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"code": "template Limited\n  with\n    owner: Party\n  where\n    signatory owner"}}'
```

**Response:**
```json
{
  "content": [{"type": "text", "text": "✅ DAML code passes basic safety gate analysis."}],
  "isError": false
}
```

### Resource Management
List and read documentation resources:

```bash
# List all resources
GET /resources

# Read specific resource
POST /resources/read
Content-Type: application/json

{
  "uri": "canton://docs/ledger-model"
}
```

### Available Endpoints
- `GET /` - Server status
- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /tools/{name}/call` - Execute tool
- `GET /resources` - List documentation resources
- `POST /resources/read` - Read documentation content

## Intelligence Features

This server includes embedded knowledge about Canton and DAML:

### Resources
Agents can read these specialized resources to understand Canton architecture:
- `canton://docs/ledger-model`: DAML Ledger Model documentation
- `canton://docs/architecture`: Canton Network architecture
- `canton://docs/language-reference`: DAML language reference
- `canton://docs/chainsafe-mcp`: ChainSafe MCP reference
- `canton://docs/llm-architecture`: LLM-Primary Architecture
- `canton://docs/quickstart-demo`: Canton Network Quickstart Demo
- `canton://docs/daml-intro`: DAML Introduction and Tutorial
- `canton://docs/daml-patterns`: DAML Design Patterns
- `canton://docs/splice-overview`: Splice & Global Synchronizer Overview
- `canton://docs/splice-scan-api`: Splice Scan API Reference

### Specialized Tools
- `analyze_daml_safety`: Performs semantic analysis on DAML code to identify missing safety markers
- `generate_canton_deployment_script`: Generates tailored scripts for Dev/Prod environments
- `get_project_summary`: Returns a summary of the project
- `check_server_status`: Returns "OK" if reachable
- `list_available_docs`: Lists all available documentation resources
- `add_documentation`: Adds new documentation to the knowledge base


