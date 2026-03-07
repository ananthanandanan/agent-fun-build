# Skill: Filesystem Navigation

## Purpose

Navigate local directory structures to locate files and understand project layout.

## Available Tools

- `get_working_directory` — Always call this first if you don't know where you are
- `list_directory(path)` — List contents of a directory
- `search_files(directory, pattern)` — Find files by glob pattern

## When to Use This Skill

- User asks "what files are in X"
- User asks "find me the config file"
- User asks "what's the structure of this project"
- You need to locate a file before reading it

## Step-by-Step Reasoning Pattern

1. **Orient**: If path context is missing, call `get_working_directory` first
2. **Broad scan**: Call `list_directory` on the root or most likely parent directory
3. **Narrow down**: If listing is large, use `search_files` with a targeted pattern
4. **Confirm before reading**: Verify the file exists in a listing before calling `read_file`

## Common Patterns

### Finding a config file

```
search_files(directory=".", pattern="*.toml")
→ if found, list its path
→ then use read_file skill to read it
```

### Understanding a project

```
get_working_directory()
→ list_directory(path=<cwd>)
→ for each interesting subdir, list_directory again (max 2 levels deep)
```

## Error Handling

- If a path doesn't exist: report it clearly, suggest `search_files` as fallback
- If a directory is empty: say so, don't keep drilling down
- If permission denied: report it and stop trying that path
