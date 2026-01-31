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
# These are exposed as static information that the Agent can read to understand Canton/DAML safety.

@mcp.resource("canton://docs/safety-gates")
def get_safety_gates() -> str:
    """Returns the core Safety Gates architecture for Canton development."""
    return """
    Canton Safety Gates Architecture:
    Gate 1: DAML Compiler Safety - Patterns must compile successfully.
    Gate 2: Safety Annotations - Patterns must have safety metadata.
    Gate 3: Formal Verification - Safety properties must be verified.
    Gate 4: Production Readiness - Must be production-tested and certified.
    """

@mcp.resource("canton://docs/auth-patterns")
def get_auth_patterns() -> str:
    """Returns canonical DAML authorization patterns."""
    return """
    DAML Authorization Patterns:
    1. Proposer-Acceptor: Ensures multi-party agreement.
    2. Delegation: One party authorizes another to act.
    3. Mandatory Signatories: Contracts cannot be created without required signatures.
    """

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
    mcp.run()
