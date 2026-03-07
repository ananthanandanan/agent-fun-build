# File Agent MCP

A CLI agent that navigates and reads your local filesystem. Behavior is defined by a **manifest** (role, skills, settings in YAML/Markdown), and **tools are loaded dynamically** from an MCP-style manifest (`mcp.json`) instead of being hardcoded.

![File Agent MCP](screenshot.png)

## Features

- **Manifest-driven**: Agent identity and behavior come from `agent.yaml`, `ROLE.md`, and skill files under `skills/`.
- **MCP-style tool loading**: Which tools the agent can use is declared in `mcp.json` per “server”; only those tools are registered with the LLM and executed.
- **Filesystem tools**: List directories, search files by pattern, read file contents (with safe size limits)—all selectable via the MCP manifest.
- **OpenAI tool-calling**: Uses an LLM (default: `gpt-4o-mini`) to plan and execute multi-step file operations.
- **Rich CLI**: Commands like `reset`, `history`, `help`, and `exit`; output via [Rich](https://github.com/Textualize/rich).

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key (set in `.env` as `OPENAI_API_KEY`)

## Setup

```bash
cd file_agent_mcp_manifest
uv sync
```

Create a `.env` in the project root (or next to where you run the app) with:

```
OPENAI_API_KEY=sk-...
```

## Run

```bash
uv run file-agent-mcp-manifest
```

Or after `uv sync`:

```bash
uv run python -m file_agent_mcp_manifest.main
```

## Tool loading: MCP manifest (`mcp.json`)

Tools are **dynamically loaded** from the MCP manifest. The agent does not see every possible tool—only the ones listed under each server’s `tools` array.

| Field            | Purpose                                                                                                                                         |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **`mcpVersion`** | Manifest format version.                                                                                                                        |
| **`servers`**    | List of tool sources. Each server has a `name`, optional `description`, `transport`, `module`, and **`tools`** (array of tool names to enable). |

The loader reads `mcp.json`, collects all enabled tool names across servers, then filters the internal tool schemas and registry to only those names. So you control the agent’s tool set by editing the manifest.

### Example: `mcp.json`

```json
{
  "mcpVersion": "0.1",
  "servers": [
    {
      "name": "filesystem",
      "description": "Local filesystem read operations",
      "transport": "local",
      "module": "file_agent_mcp_manifest.tools",
      "tools": [
        "get_working_directory",
        "list_directory",
        "read_file",
        "search_files"
      ]
    }
  ]
}
```

- **Enable a tool**: Add its name to the `tools` array for the appropriate server.
- **Disable a tool**: Remove it from `tools` (or omit that server).
- **Add another server**: Add a new entry to `servers` with its own `tools` list (implementation may resolve tools from the given `module` or a future MCP transport).

Paths to `mcp.json` and `agent.yaml` are resolved from the package directory (`src/file_agent_mcp_manifest/`).

## Agent manifest layout (`agent.yaml`)

| Item                    | Purpose                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------ |
| **`agent.yaml`**        | Top-level config: model, role path, MCP manifest path, skill paths, safety settings. |
| **`ROLE.md`**           | System prompt: identity, responsibilities, reasoning style, boundaries.              |
| **`skills/*/SKILL.md`** | Loaded in order; each adds instructions and patterns for the agent.                  |

The agent builds its system prompt by concatenating the role and all enabled skills. Paths in the manifest are relative to the package directory (`src/file_agent_mcp_manifest/`).

### Example: `agent.yaml`

```yaml
name: "File Agent MCP Manifest"
model:
  provider: openai
  name: gpt-4o-mini
role: ROLE.md
mcp: mcp.json
skills:
  - skills/filesystem/SKILL.md
  - skills/summarizer/SKILL.md
settings:
  max_iterations: 10
  max_file_size_kb: 500
```

### Bundled skills

- **Filesystem** — Orient with `get_working_directory`, then use `list_directory` and `search_files` to find files (when enabled in `mcp.json`).
- **Summarizer** — Use `read_file` and summarize by file type (e.g. `.toml`, `.py`, `.md`).

## CLI commands

At the `You` prompt you can type:

- **`reset`** — Clear conversation history (keeps system prompt).
- **`history`** — Show how many messages are in the current context.
- **`help`** — Show available commands and example questions.
- **`exit`** — Quit the agent.

## Customization

- **Change behavior**: Edit `ROLE.md` or the Markdown in `skills/`; restart the app.
- **Change which tools are available**: Edit `mcp.json`—add or remove tool names under each server’s `tools` array.
- **Add a skill**: Add a new `skills/<name>/SKILL.md` and append its path under `skills` in `agent.yaml`.
- **Change model**: Update `model.name` in `agent.yaml` (e.g. `gpt-4o`).
- **Different MCP config**: Set `mcp` in `agent.yaml` to another path (e.g. `mcp-minimal.json`). For code-level override you can still pass `mcp_path` to `FileAgent`.
- **Different manifests**: Pass `manifest_path` to `FileAgent` in code to use another `agent.yaml`.

## Finding the skills folder from the CLI

When you run the agent, the process current working directory is usually the **project root** (`file_agent_mcp_manifest/`). The skills live under the package at `src/file_agent_mcp_manifest/skills/`. To have the agent list or summarize them, ask for that path explicitly, for example:

- _"List the contents of `src/file_agent_mcp_manifest/skills`"_
- _"Read and summarize each SKILL.md in `src/file_agent_mcp_manifest/skills`"_

Or use search: _"Search for files named SKILL.md in the current directory and summarize each one."_
