import os
import fnmatch
from pathlib import Path

def list_directory(path: str) -> str:
    """List the contents of a directory"""

    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Directory {path} does not exist"
        if not p.is_dir():
            return f"Path {path} is not a directory"

        entries = []
        for item in sorted(p.iterdir()):
            prefix = "📁" if item.is_dir() else "📄"
            size = ""
            if item.is_file():
                s = item.stat().st_size
                size = f"  ({s:,} bytes)"
            entries.append(f"{prefix} {item.name}{size}")
        
        if not entries:
            return f"Directory '{path}' is empty."
        
        return f"Contents of {p}:\n" + "\n".join(entries)
    except PermissionError:
        return f"Error: Permission denied accessing '{path}'."
    except Exception as e:
        return f"Error: {e}"

def read_file(path: str, max_chars: int = 1000) -> str:
    """Read the contents of a file"""

    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"File {path} does not exist"
        if not p.is_file():
            return f"Path {path} is not a file"
        
        try:
            file_content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"Error: Unable to read file '{path}' as text. It may contain non-textual data."

        if len(file_content) > max_chars:
            content = file_content[:max_chars]
            return f"[File truncated to {max_chars} chars]\n\n{content}"
        return f"Contents of {p}:\n\n{file_content}"
    except PermissionError:
        return f"Error: Permission denied reading '{path}'."
    except Exception as e:
        return f"Error: {e}"



def search_files(directory: str, pattern: str) -> str:
    """Search for files matching a name pattern within a directory."""
    try:
        p = Path(directory).expanduser().resolve()
        if not p.exists():
            return f"Error: Directory '{directory}' does not exist."
        
        matches = []
        for root, dirs, files in os.walk(p):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')] # mutates the list in place
            for filename in files:
                if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                    full_path = Path(root) / filename
                    matches.append(str(full_path))
        
        if not matches:
            return f"No files matching '{pattern}' found in '{directory}'."
        
        result = f"Found {len(matches)} file(s) matching '{pattern}':\n"
        result += "\n".join(matches[:50])  # Cap at 50 results
        if len(matches) > 50:
            result += f"\n... and {len(matches) - 50} more."
        return result
    except Exception as e:
        return f"Error: {e}"


def get_working_directory() -> str:
    """Get the current working directory."""
    return f"Current working directory: {os.getcwd()}"

# Registry: maps tool names (as the LLM knows them) to functions
TOOL_REGISTRY = {
    "list_directory": list_directory,
    "read_file": read_file,
    "search_files": search_files,
    "get_working_directory": get_working_directory,
}


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool by name with given inputs. Returns result as string."""
    if name not in TOOL_REGISTRY:
        return f"Error: Unknown tool '{name}'."
    
    func = TOOL_REGISTRY[name]
    try:
        return func(**tool_input)
    except TypeError as e:
        return f"Error calling tool '{name}': {e}"