# File Agent Manifest

A CLI agent that navigates and reads your local filesystem. Behavior is defined by a **manifest**: a role document, a list of skills, and settings—all configured in YAML and Markdown instead of hardcoded prompts.

## Features

- **Manifest-driven**: Agent identity and behavior come from `agent.yaml`, `ROLE.md`, and skill files under `skills/`.
- **Filesystem tools**: List directories, search files by pattern, read file contents (with safe size limits).
- **OpenAI tool-calling**: Uses an LLM (default: `gpt-4o-mini`) to plan and execute multi-step file operations.
- **Rich CLI**: Commands like `reset`, `history`, `help`, and `exit`; output via [Rich](https://github.com/Textualize/rich).

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key (set in `.env` as `OPENAI_API_KEY`)

## Setup

```bash
cd file_agent_manifest
uv sync
```

Create a `.env` in the project root (or next to where you run the app) with:

```
OPENAI_API_KEY=sk-...
```

## Run

```bash
uv run file-agent-manifest
```

Or after `uv sync`:

```bash
uv run python -m file_agent_manifest.main
```

## Manifest layout

| Item | Purpose |
|------|--------|
| **`agent.yaml`** | Top-level config: model, role path, skill paths, safety settings. |
| **`ROLE.md`** | System prompt: identity, responsibilities, reasoning style, boundaries. |
| **`skills/*/SKILL.md`** | Loaded in order; each adds instructions and patterns for the agent. |

The agent builds its system prompt by concatenating the role and all enabled skills. Paths in the manifest are relative to the package directory (`src/file_agent_manifest/`).

### Example: `agent.yaml`

```yaml
name: "File Agent Manifest"
model:
  provider: openai
  name: gpt-4o-mini
role: ROLE.md
skills:
  - skills/filesystem/SKILL.md
  - skills/summarizer/SKILL.md
settings:
  max_iterations: 10
  max_file_size_kb: 500
```

### Bundled skills

- **Filesystem** — Orient with `get_working_directory`, then use `list_directory` and `search_files` to find files.
- **Summarizer** — Use `read_file` and summarize by file type (e.g. `.toml`, `.py`, `.md`).

## CLI commands

At the `You` prompt you can type:

- **`reset`** — Clear conversation history (keeps system prompt).
- **`history`** — Show how many messages are in the current context.
- **`help`** — Show available commands and example questions.
- **`exit`** — Quit the agent.

## Customization

- **Change behavior**: Edit `ROLE.md` or the Markdown in `skills/`; restart the app.
- **Add a skill**: Add a new `skills/<name>/SKILL.md` and append its path under `skills` in `agent.yaml`.
- **Change model**: Update `model.name` in `agent.yaml` (e.g. `gpt-4o`).
- **Different manifest**: Instantiate with another path (e.g. for testing) by passing `manifest_path` to `FileAgent` in code.

## Finding the skills folder from the CLI

When you run the agent, the process current working directory is usually the **project root** (`file_agent_manifest/`). The skills live under the package at `src/file_agent_manifest/skills/`. To have the agent list or summarize them, ask for that path explicitly, for example:

- *"List the contents of `src/file_agent_manifest/skills`"*
- *"Read and summarize each SKILL.md in `src/file_agent_manifest/skills`"*

Or use search: *"Search for files named SKILL.md in the current directory and summarize each one."*
