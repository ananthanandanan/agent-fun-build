# Agent Fun Build

This repository contains experimental agent projects and build iterations.

Right now, the active project is `file_agent/`: a Python CLI agent that uses OpenAI tool-calling to inspect local files and directories.

## Repository structure

```text
agent_fun_build/
  README.md
  screenshot.png
  file_agent/
    README.md
    pyproject.toml
    src/file_agent/
```

## Active project: File Agent

`file_agent` is a terminal app that:

- runs an interactive chat loop
- can call filesystem tools (`get_working_directory`, `list_directory`, `read_file`, `search_files`)
- shows output with a `rich`-based CLI interface

Project-specific docs live in `file_agent/README.md`.

## Screenshot

![File Agent CLI screenshot](file_agent/screenshot.png)

## Quick start

From the repository root:

```bash
cd file_agent
uv sync
uv run file-agent
```

You can also run:

```bash
uv run python -m file_agent.main
```

## Environment

Create `file_agent/.env` with:

```bash
OPENAI_API_KEY=your_api_key_here
```

## Build

From `file_agent/`:

```bash
uv build
```

Artifacts are generated in `file_agent/dist/`.

## Notes

- Runtime target is Python `3.12+`.
- The repository may grow to include more agent experiments over time.
