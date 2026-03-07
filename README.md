# Agent Fun Build

This repository contains experimental CLI file-agent projects and build iterations. Each project is a terminal app that uses OpenAI tool-calling to inspect local files and directories; the builds progress from a minimal agent to a manifest-driven, MCP-powered version.

## Builds overview

| Project | Description | Entrypoint |
|---------|-------------|------------|
| **file_agent** | Base agent: hardcoded tool schemas and implementations, simple system prompt. | `uv run file-agent` |
| **file_agent_manifest** | Manifest-driven: role and skills from `agent.yaml`, `ROLE.md`, and `skills/*.md`. Tools still in-process. | `uv run file-agent-manifest` |
| **file_agent_mcp_manifest** | Manifest + MCP-style config: `mcp.json` selects which tools are enabled; tools run in-process from a module. | `uv run file-agent-mcp-manifest` |
| **file_agent_mcp** | Full MCP: tools come from a real MCP server (stdio). Manifest defines role/skills; `mcp.json` defines server(s). | `uv run file-agent-mcp` |

All builds share the same core idea: an interactive chat loop, filesystem tools (`get_working_directory`, `list_directory`, `read_file`, `search_files`), and Rich CLI with `reset`, `history`, `help`, `exit`.

- **file_agent** — Start here: one place for prompts, schemas, and tool code.
- **file_agent_manifest** — Behavior and identity move into YAML/Markdown (role + skills).
- **file_agent_mcp_manifest** — Tool set is configured via `mcp.json` (which tools to expose), still in-process.
- **file_agent_mcp** — Tools are provided by an MCP server subprocess; add or swap servers without changing agent code.

## Repository structure

```text
agent_fun_build/
  README.md                 # This file
  AGENTS.md                 # Guidance for coding agents in this repo
  file_agent/               # Base build: hardcoded tools + schemas
    README.md
    pyproject.toml
    src/file_agent/
  file_agent_manifest/      # Manifest build: role + skills from YAML/MD
    README.md
    pyproject.toml
    src/file_agent_manifest/
  file_agent_mcp_manifest/  # MCP-style manifest: tool set from mcp.json (in-process)
    README.md
    pyproject.toml
    src/file_agent_mcp_manifest/
  file_agent_mcp/           # Full MCP: tools from MCP server over stdio
    README.md
    pyproject.toml
    src/file_agent_mcp/
```

## Quick start (any project)

From the repo root, pick a project and run:

```bash
cd <project_dir>   # e.g. file_agent, file_agent_mcp
uv sync
```

Create a `.env` in that directory (or where you run from) with:

```bash
OPENAI_API_KEY=your_api_key_here
```

Then start the agent:

| Project | Command |
|---------|--------|
| file_agent | `uv run file-agent` |
| file_agent_manifest | `uv run file-agent-manifest` |
| file_agent_mcp_manifest | `uv run file-agent-mcp-manifest` |
| file_agent_mcp | `uv run file-agent-mcp` |

Project-specific setup, layout, and options are in each project’s `README.md`.

## Environment

- **Python**: 3.12+
- **Package manager**: [uv](https://docs.astral.sh/uv/) (recommended) or pip
- **OpenAI**: API key in `.env` as `OPENAI_API_KEY`

## Build (wheel)

From the project directory:

```bash
uv build
```

Artifacts go to `<project_dir>/dist/`.

## Screenshot

![File Agent CLI screenshot](file_agent/screenshot.png)

## Notes

- Each project is a separate Python package with its own `pyproject.toml` and dependencies.
- `AGENTS.md` at the repo root describes scope, layout, and conventions for the `file_agent/` tree; adapt as needed for the other builds.
- The repository may grow with more agent experiments over time.
