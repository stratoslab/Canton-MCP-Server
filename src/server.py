from fastmcp import FastMCP
from pydantic import BaseModel, Field
import os
import json
from pathlib import Path

# Initialize the MCP Server
mcp = FastMCP("Canton Ledgerview Assistant")

# --- Helper Models (Pydantic) ---
class ProjectSummary(BaseModel):
    name: str
    dependencies: dict[str, str] = Field(default_factory=dict)
    total_files: int

# --- Resources (The "Intelligence") ---
# These serve the embedded documentation files as MCP Resources.
# Agents can read these to understand Canton/DAML architecture.

DOCS_DIR = Path(__file__).parent.parent / "docs"

def _read_doc(filename: str) -> str:
    """Helper to read documentation files."""
    doc_path = DOCS_DIR / filename
    if doc_path.exists():
        return doc_path.read_text()
    return f"Error: Documentation file {filename} not found."

@mcp.resource("canton://docs/ledger-model")
def get_ledger_model() -> str:
    """Returns the complete DAML Ledger Model documentation."""
    return _read_doc("daml_ledger_model.md")

@mcp.resource("canton://docs/architecture")
def get_canton_architecture() -> str:
    """Returns the Canton Network architecture and deployment guide."""
    return _read_doc("canton_architecture.md")

@mcp.resource("canton://docs/language-reference")
def get_daml_language_reference() -> str:
    """Returns the DAML language reference and syntax guide."""
    return _read_doc("daml_language_reference.md")

@mcp.resource("canton://docs/chainsafe-mcp")
def get_chainsafe_mcp_reference() -> str:
    """Returns the ChainSafe Canton MCP Server architecture and tool implementation guide."""
    return _read_doc("chainsafe_mcp_reference.md")

@mcp.resource("canton://docs/llm-architecture")
def get_llm_architecture() -> str:
    """Returns the LLM-Primary Architecture for DAML analysis."""
    return _read_doc("llm_architecture.md")

@mcp.resource("canton://docs/quickstart-demo")
def get_quickstart_demo() -> str:
    """Returns the Canton Network Quickstart Demo walkthrough guide."""
    return _read_doc("canton_quickstart_demo.md")

@mcp.tool()
def list_available_docs() -> str:
    """Lists all available Canton/DAML documentation resources."""
    docs = list(DOCS_DIR.glob("*.md"))
    if not docs:
        return "No documentation files found."
    
    doc_list = []
    for doc in sorted(docs):
        doc_list.append(f"- {doc.stem}: canton://docs/{doc.stem.replace('_', '-')}")
    
    return "Available Documentation Resources:\n" + "\n".join(doc_list)

@mcp.resource("canton://docs/daml-intro")
def get_daml_introduction() -> str:
    """Returns the DAML Introduction and Tutorial."""
    return _read_doc("daml_introduction.md")

@mcp.resource("canton://docs/daml-patterns")
def get_daml_patterns() -> str:
    """Returns the DAML Design Patterns and Anti-Patterns guide."""
    return _read_doc("daml_patterns.md")

@mcp.resource("canton://docs/splice-overview")
def get_splice_overview() -> str:
    """Returns the Splice & Global Synchronizer Overview."""
    return _read_doc("splice_overview.md")

@mcp.resource("canton://docs/splice-scan-api")
def get_splice_scan_api() -> str:
    """Returns the Splice Scan API Reference."""
    return _read_doc("splice_scan_api.md")

@mcp.tool()
def add_documentation(filename: str, content: str, description: str = "") -> str:
    """
    Adds a new documentation file to the MCP server's knowledge base.
    
    Args:
        filename: name of the file (e.g., 'my_guide.md')
        content: The markdown content of the documentation
        description: Short description of what this doc covers
    """
    if not filename.endswith(".md"):
        filename += ".md"
    
    # Sanitize filename to prevent directory traversal
    safe_filename = Path(filename).name
    file_path = DOCS_DIR / safe_filename
    
    try:
        if file_path.exists():
            return f"Error: File '{safe_filename}' already exists. Please use a different name or manually update it."
            
        file_path.write_text(content)
        return f"Successfully added documentation: {safe_filename}\nIt will be available via the 'list_available_docs' tool."
    except Exception as e:
        return f"Failed to save documentation: {str(e)}"

# --- Tools ---

@mcp.tool()
async def analyze_daml_safety(code: str) -> str:
    """
    Analyzes DAML code against the Canton Safety Gates.
    This simulates the 'intelligent' reasoning by checking for specific safety markers.
    """
    issues = []
    if "signatory" not in code.lower():
        issues.append("Warning: No signatories defined. This contract might be unauthorized.")
    if "controller" not in code.lower():
        issues.append("Warning: No controllers defined. The contract may be immutable/unusable.")
    
    if not issues:
        return "✅ DAML code passes basic safety gate analysis."
    return "❌ Safety Issues Found:\n- " + "\n- ".join(issues)

@mcp.tool()
def generate_canton_deployment_script(network_type: str = "dev") -> str:
    """
    Generates a starter deployment script for a Canton network.
    """
    if network_type == "prod":
        return "# PROD DEPLOYMENT\n# 1. Verify DCAP settings\n# 2. Check x402 payment routes\n# 3. Submit to Canton Ledger"
    return "# DEV DEPLOYMENT\n# 1. daml build\n# 2. daml ledger upload-dar --host localhost --port 6865"

@mcp.tool()
def get_project_summary(project_path: str = ".") -> str:

    """
    Reads the package.json and counts files in the specified project path to provide a summary.
    Arguments:
        project_path: Relative or absolute path to the project root.
    """
    base_path = Path(project_path).resolve()
    
    # Check for package.json
    package_json_path = base_path / "package.json"
    if not package_json_path.exists():
        return f"Error: No package.json found at {base_path}"
    
    try:
        with open(package_json_path, 'r') as f:
            data = json.load(f)
            
        name = data.get("name", "Unknown")
        deps = data.get("dependencies", {})
        
        # Count files roughly (ignoring node_modules)
        file_count = 0
        for _ in base_path.rglob("*"):
             if "node_modules" not in str(_):
                 file_count += 1

        return f"Project: {name}\nDependencies: {', '.join(deps.keys())}\nEstimated Files: {file_count}"

    except Exception as e:
        return f"Failed to analyze project: {str(e)}"

@mcp.tool()
def check_server_status() -> str:
    """Returns a simple 'OK' if the server is up."""
    return "Server is running and healthy!"

# Entry point for 'uv run'
if __name__ == "__main__":
    import sys
    
    # Check if we're running in HTTP mode (for Docker)
    if "--http" in sys.argv or os.getenv("MCP_HTTP_MODE"):
        host = "0.0.0.0"
        port = 8000
        
        # Parse command line arguments
        for i, arg in enumerate(sys.argv):
            if arg == "--host" and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
            elif arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        
        # Use environment variables if available
        host = os.getenv("HOST", host)
        port = int(os.getenv("PORT", port))
        
        print(f"Starting Canton Ledgerview MCP Server on {host}:{port}")
        
        # Create HTTP server with MCP endpoints
        import uvicorn
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
        from pydantic import BaseModel
        from typing import Dict, Any, List
        
        app = FastAPI(title="Canton Ledgerview MCP Server")
        
        class ToolCallRequest(BaseModel):
            arguments: Dict[str, Any] = {}
        
        class ResourceReadRequest(BaseModel):
            uri: str
        
        @app.get("/")
        async def root():
            return {"message": "Canton Ledgerview MCP Server", "status": "running"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @app.get("/tools")
        async def list_tools():
            return {
                "tools": [
                    {"name": "analyze_daml_safety", "description": "Analyzes DAML code against Canton Safety Gates"},
                    {"name": "generate_canton_deployment_script", "description": "Generates Canton deployment script"},
                    {"name": "get_project_summary", "description": "Returns project summary"},
                    {"name": "check_server_status", "description": "Returns server status"},
                    {"name": "list_available_docs", "description": "Lists available documentation"},
                    {"name": "add_documentation", "description": "Adds new documentation"}
                ]
            }
        
        @app.post("/tools/{tool_name}/call")
        async def call_tool(tool_name: str, request: ToolCallRequest):
            try:
                args = request.arguments
                
                if tool_name == "analyze_daml_safety":
                    code = args.get("code", "")
                    issues = []
                    if "signatory" not in code.lower():
                        issues.append("Warning: No signatories defined. This contract might be unauthorized.")
                    if "controller" not in code.lower():
                        issues.append("Warning: No controllers defined. The contract may be immutable/unusable.")
                    
                    if not issues:
                        result = "✅ DAML code passes basic safety gate analysis."
                    else:
                        result = "❌ Safety Issues Found:\n- " + "\n- ".join(issues)
                        
                elif tool_name == "generate_canton_deployment_script":
                    network_type = args.get("network_type", "dev")
                    if network_type == "prod":
                        result = "# PROD DEPLOYMENT\n# 1. Verify DCAP settings\n# 2. Check x402 payment routes\n# 3. Submit to Canton Ledger"
                    else:
                        result = "# DEV DEPLOYMENT\n# 1. daml build\n# 2. daml ledger upload-dar --host localhost --port 6865"
                        
                elif tool_name == "get_project_summary":
                    project_path = args.get("project_path", ".")
                    base_path = Path(project_path).resolve()
                    
                    package_json_path = base_path / "package.json"
                    if not package_json_path.exists():
                        result = f"Error: No package.json found at {base_path}"
                    else:
                        try:
                            with open(package_json_path, 'r') as f:
                                data = json.load(f)
                                
                            name = data.get("name", "Unknown")
                            deps = data.get("dependencies", {})
                            
                            file_count = 0
                            for _ in base_path.rglob("*"):
                                 if "node_modules" not in str(_):
                                     file_count += 1

                            result = f"Project: {name}\nDependencies: {', '.join(deps.keys())}\nEstimated Files: {file_count}"
                        except Exception as e:
                            result = f"Failed to analyze project: {str(e)}"
                            
                elif tool_name == "check_server_status":
                    result = "Server is running and healthy!"
                    
                elif tool_name == "list_available_docs":
                    docs = list(DOCS_DIR.glob("*.md"))
                    if not docs:
                        result = "No documentation files found."
                    else:
                        doc_list = []
                        for doc in sorted(docs):
                            doc_list.append(f"- {doc.stem}: canton://docs/{doc.stem.replace('_', '-')}")
                        result = "Available Documentation Resources:\n" + "\n".join(doc_list)
                        
                elif tool_name == "add_documentation":
                    filename = args.get("filename", "")
                    content = args.get("content", "")
                    description = args.get("description", "")
                    
                    if not filename.endswith(".md"):
                        filename += ".md"
                    
                    safe_filename = Path(filename).name
                    file_path = DOCS_DIR / safe_filename
                    
                    try:
                        if file_path.exists():
                            result = f"Error: File '{safe_filename}' already exists. Please use a different name or manually update it."
                        else:
                            file_path.write_text(content)
                            result = f"Successfully added documentation: {safe_filename}\nIt will be available via the 'list_available_docs' tool."
                    except Exception as e:
                        result = f"Failed to save documentation: {str(e)}"
                        
                else:
                    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
                
                return {
                    "content": [{"type": "text", "text": result}],
                    "isError": False
                }
            except Exception as e:
                return {
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                    "isError": True
                }
        
        @app.get("/resources")
        async def list_resources():
            return {
                "resources": [
                    {"name": "DAML Ledger Model", "uri": "canton://docs/ledger-model", "mimeType": "text/markdown"},
                    {"name": "Canton Architecture", "uri": "canton://docs/architecture", "mimeType": "text/markdown"},
                    {"name": "DAML Language Reference", "uri": "canton://docs/language-reference", "mimeType": "text/markdown"},
                    {"name": "ChainSafe MCP Reference", "uri": "canton://docs/chainsafe-mcp", "mimeType": "text/markdown"},
                    {"name": "LLM Architecture", "uri": "canton://docs/llm-architecture", "mimeType": "text/markdown"},
                    {"name": "Quickstart Demo", "uri": "canton://docs/quickstart-demo", "mimeType": "text/markdown"},
                    {"name": "DAML Introduction", "uri": "canton://docs/daml-intro", "mimeType": "text/markdown"},
                    {"name": "DAML Patterns", "uri": "canton://docs/daml-patterns", "mimeType": "text/markdown"},
                    {"name": "Splice Overview", "uri": "canton://docs/splice-overview", "mimeType": "text/markdown"},
                    {"name": "Splice Scan API", "uri": "canton://docs/splice-scan-api", "mimeType": "text/markdown"}
                ]
            }
        
        @app.post("/resources/read")
        async def read_resource(request: ResourceReadRequest):
            try:
                uri = request.uri
                
                # Map URIs to documentation files
                uri_to_file = {
                    "canton://docs/ledger-model": "daml_ledger_model.md",
                    "canton://docs/architecture": "canton_architecture.md",
                    "canton://docs/language-reference": "daml_language_reference.md",
                    "canton://docs/chainsafe-mcp": "chainsafe_mcp_reference.md",
                    "canton://docs/llm-architecture": "llm_architecture.md",
                    "canton://docs/quickstart-demo": "canton_quickstart_demo.md",
                    "canton://docs/daml-intro": "daml_introduction.md",
                    "canton://docs/daml-patterns": "daml_patterns.md",
                    "canton://docs/splice-overview": "splice_overview.md",
                    "canton://docs/splice-scan-api": "splice_scan_api.md"
                }
                
                if uri not in uri_to_file:
                    raise HTTPException(status_code=404, detail=f"Resource '{uri}' not found")
                
                filename = uri_to_file[uri]
                doc_path = DOCS_DIR / filename
                
                if doc_path.exists():
                    content = doc_path.read_text()
                else:
                    content = f"Error: Documentation file {filename} not found."
                
                return {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": content
                    }]
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        uvicorn.run(app, host=host, port=port)
    else:
        # Default stdio mode for MCP
        mcp.run()
