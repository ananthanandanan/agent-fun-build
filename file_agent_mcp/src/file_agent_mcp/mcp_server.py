# file_agent_mcp/mcp_server.py
#
# Run standalone with:  uv run python -m file_agent_mcp.mcp_server
#
# IMPORTANT — stdio transport rule:
# Never use print() in this file. It writes to stdout and corrupts
# the JSON-RPC stream. Use logging to stderr instead.

import logging
import sys
from mcp.server.fastmcp import FastMCP

from .tools import list_directory, read_file, search_files, get_working_directory

# All logs go to stderr — stdout is reserved for the JSON-RPC protocol
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

# FastMCP reads the function's docstring as the tool description
# and derives the input schema from Python type hints automatically.
# No manual Tool(...) definitions needed.
mcp = FastMCP("filesystem-server")


@mcp.tool()
def get_working_directory_tool() -> str:
    """Returns the current working directory.
    Use this first to orient yourself before navigating relative paths."""
    return get_working_directory()


@mcp.tool()
def list_directory_tool(path: str) -> str:
    """Lists all files and subdirectories inside a given directory path.
    Use this to explore the filesystem and find relevant files.

    Args:
        path: Absolute or relative path to the directory to list.
    """
    return list_directory(path)


@mcp.tool()
def read_file_tool(path: str) -> str:
    """Reads and returns the text content of a file.
    Use this to read configuration files, notes, code, logs, etc.
    Do not use on binary files.

    Args:
        path: Absolute or relative path to the file to read.
    """
    return read_file(path)


@mcp.tool()
def search_files_tool(directory: str, pattern: str) -> str:
    """Recursively searches a directory for files whose names match a glob pattern.
    Use this when you know the file type or partial name but not the exact location.

    Args:
        directory: Root directory to search in.
        pattern: Glob pattern for filename matching, e.g. '*.txt', 'README*', '*.py'.
    """
    return search_files(directory, pattern)


def main():
    logger.info("Starting filesystem MCP server on stdio...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()