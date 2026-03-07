# Skill: File Summarization

## Purpose

Read file contents and extract meaningful, structured information from them.

## Available Tools

- `read_file(path)` — Read a file's text content (max 8000 chars, truncated if larger)

## When to Use This Skill

- User asks "what does X file contain"
- User asks "summarize this file"
- User asks "what are the dependencies in pyproject.toml"
- You've located a file and now need to understand its contents

## Reasoning Pattern

1. **Check the extension first** — infer what kind of file it is before reading
2. **Read it** — call `read_file`
3. **Extract by file type:**
   - `.toml` / `.yaml` / `.json` → list the top-level keys and their values
   - `.py` → describe the module's purpose, classes, and key functions
   - `.md` → summarize the topic and main sections
   - `.env` → list variable names (NOT values — these may be secrets)
   - Unknown → describe the structure and content type

## Output Format

Always structure your summary as:

- **File**: the path
- **Type**: what kind of file it is
- **Summary**: 2-4 sentences on purpose and content
- **Key contents**: bullet list of the most important items

## Cautions

- Never print raw `.env` file values — only print key names
- If file is truncated (you'll see "[File truncated]"), note that in your summary
- Binary files will error — report this and move on
