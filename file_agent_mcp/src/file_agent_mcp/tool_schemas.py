"""
Tool schemas:
Key learning: Notice the description fields. These are not for you — they're instructions to the LLM. Good descriptions are what make tools get used correctly. This is prompt engineering at the tool level.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_working_directory",
            "description": (
                "Returns the current working directory. "
                "Use this first to understand where you are in the filesystem "
                "before navigating relative paths."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": (
                "Lists the files and subdirectories inside a given directory path. "
                "Use this to explore the filesystem and find relevant files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the directory to list.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Reads and returns the text content of a file. "
                "Use this to read configuration files, notes, code, logs, etc. "
                "Do not use on binary files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file to read.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": (
                "Recursively searches a directory for files whose names match "
                "a glob pattern (e.g. '*.py', '*.md', 'config*'). "
                "Use this when you know the file type or partial name but not exact location."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Root directory to search in.",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern for filename matching, e.g. '*.txt', 'README*'.",
                    },
                },
                "required": ["directory", "pattern"],
            },
        },
    },
]
