# file_agent_mcp_manifest/tool_loader.py
import json
from pathlib import Path
from .tool_schemas import TOOLS as ALL_SCHEMAS
from .tools import TOOL_REGISTRY

BASE_DIR = Path(__file__).parent 


def load_tools_from_manifest(mcp_path: str = "mcp.json"):
    """
    Read mcp.json and return only the tools declared there.
    This is the "simple manifest" version — no actual MCP servers yet.
    """
    with open(BASE_DIR / mcp_path) as f:
        mcp_config = json.load(f)

    # Collect which tool names are declared across all servers
    enabled_tool_names = set()
    for server in mcp_config["servers"]:
        enabled_tool_names.update(server["tools"])

    # Filter schemas to only enabled tools
    active_schemas = [
        schema for schema in ALL_SCHEMAS
        if schema["function"]["name"] in enabled_tool_names
    ]

    # Filter registry to only enabled tools
    active_registry = {
        name: fn
        for name, fn in TOOL_REGISTRY.items()
        if name in enabled_tool_names
    }

    return active_schemas, active_registry