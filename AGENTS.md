# AGENTS.md
Guidance for coding agents working in this repository.
## Scope
- Repository root: `agent_fun_build`
- Active project: `file_agent/`
- Language/runtime: Python `3.12` (`file_agent/.python-version`)
- Package/workflow tool: `uv` (`file_agent/uv.lock` present)
- Build backend: Hatchling (`file_agent/pyproject.toml`)
## Repository Layout
- `file_agent/pyproject.toml` - package metadata, dependencies, entrypoint
- `file_agent/src/file_agent/main.py` - CLI loop and command handling
- `file_agent/src/file_agent/agent.py` - LLM interaction and tool-call loop
- `file_agent/src/file_agent/tools.py` - filesystem tool implementations
- `file_agent/src/file_agent/tool_schemas.py` - JSON tool specs exposed to model
- `file_agent/README.md` - currently empty
## Build, Lint, and Test Commands
Run commands from `file_agent/` unless noted otherwise.
### Setup
```bash
uv sync
```
### Run app
```bash
uv run file-agent
```
Alternative:
```bash
uv run python -m file_agent.main
```
### Build
```bash
uv build
```
Artifacts are created in `file_agent/dist/`.
### Lint/format/type-check (current state)
No linter, formatter, or type-checker is configured today.
If introducing tooling, prefer:
- Lint + format: `ruff`
- Static typing: `mypy` or `pyright`
- Tests: `pytest`
### Tests (current state + recommended commands)
No test suite currently exists (`tests/` missing, no test dependency configured).
When tests are added, use `pytest` and these command patterns:
Run all tests:
```bash
uv run pytest
```
Run a single test file:
```bash
uv run pytest tests/test_agent.py
```
Run a single test function (important for fast iteration):
```bash
uv run pytest tests/test_agent.py::test_handles_tool_calls
```
Run a single class test method:
```bash
uv run pytest tests/test_agent.py::TestFileAgent::test_reset
```
Run tests by keyword:
```bash
uv run pytest -k "tool and reset"
```
If `unittest` is used instead:
```bash
uv run python -m unittest tests.test_agent.TestFileAgent.test_reset
```
## Code Style Guidelines
These rules are inferred from the current codebase and should be treated as defaults.
### Imports
- Group imports in this order:
  1) standard library
  2) third-party
  3) local package imports
- Prefer explicit imports; avoid wildcard imports.
- Usually keep one import per line.
- Use relative imports for same-package modules (for example `from .tools import execute_tool`).
### Formatting
- Follow PEP 8 baseline style.
- Use 4 spaces for indentation.
- Prefer double-quoted strings.
- Keep logical whitespace between blocks to preserve readability.
- Wrap long expressions/strings with parentheses rather than cramped lines.
### Types and Signatures
- Add type hints to public functions and methods.
- Keep non-trivial return types explicit.
- Prefer concrete types (`str`, `dict[str, Any]`, `list[str]`) when practical.
- For complex JSON-like structures, introduce typed aliases or `TypedDict`.
### Naming Conventions
- Modules: `snake_case`
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE` (for example `SYSTEM_PROMPT`, `TOOLS`)
- Use descriptive names for tool APIs (for example `list_directory`, `search_files`).
### Error Handling
- Validate path preconditions before reading/walking filesystem state.
- Catch specific exceptions first (`PermissionError`, `UnicodeDecodeError`, etc.).
- Return clear user-facing error messages from tool functions.
- Use broad `except Exception as e` only as a final fallback.
- Avoid silently swallowing unexpected exceptions in core flows.
### Logging and User Output
- CLI output should use `rich` primitives (`Console`, `Panel`, `Rule`, `Prompt`).
- Keep runtime messages concise, actionable, and user-oriented.
- Remove or guard ad-hoc debug prints before shipping.
### Agent Loop and Tool-Call Behavior
- Preserve OpenAI chat history shape expected by tool-calling APIs.
- For tool responses, keep `tool_call_id` exactly aligned with each tool call.
- Keep loop safety valves (for example `max_iterations`) to prevent runaway cycles.
- Keep tool outputs bounded (truncate overly large text results when needed).
### Tool and Schema Design
- Keep tool schemas clear and instruction-oriented for model behavior.
- Keep arguments minimal and strongly defined.
- Keep tool functions deterministic and plain-text returning.
- Prefer small, composable tools over one broad, ambiguous tool.
### Security and Safety
- Never commit secrets (`.env`, tokens, API keys, credentials).
- Treat filesystem paths as untrusted; normalize with `Path(...).expanduser().resolve()`.
- Avoid destructive file operations unless explicitly requested.
## Cursor / Copilot Rule Files
Checked locations:
- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`
Current status: no Cursor or Copilot rule files were found.
If any are added later, treat them as repository policy and merge them into this guidance.
## Suggested Agent Workflow
1. Inspect `file_agent/pyproject.toml` first for runtime/build truth.
2. Read nearby modules before introducing abstractions.
3. Keep edits small and focused in `file_agent/src/file_agent/`.
4. Validate behavior quickly with `uv run file-agent`.
5. If tests exist, run single targeted tests first, then full suite.
6. Keep docs/config updates in sync with behavior changes.

## Pull Request Hygiene
- Keep PRs focused on one behavior change or one refactor at a time.
- Include why the change is needed, not only what changed.
- Avoid broad renames unless they remove clear confusion.
- Do not include unrelated formatting-only churn.
- Mention manual verification steps in the PR description.

## Quick Validation Checklist
- Can the app start with `uv run file-agent`?
- Are imports grouped and ordered consistently?
- Are new public functions type-annotated?
- Are error messages clear for invalid path/permission issues?
- Are tool outputs bounded to avoid huge context payloads?
- Did you avoid adding secrets or local machine paths?
