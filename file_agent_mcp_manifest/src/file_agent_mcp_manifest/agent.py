# src/file_agent_mcp_manifest/agent.py
import json
import openai
from rich.console import Console
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).parent 

from .tool_loader import load_tools_from_manifest

console = Console()


def load_agent_manifest(path: str = "agent.yaml") -> dict:
    """
    Load the agent manifest from a YAML file.
    """
    with open(BASE_DIR / path, "r") as f:
        return yaml.safe_load(f)

def load_role(role_path: str) -> str:
    """Read the ROLE.md file and return it as the system prompt."""
    return (BASE_DIR / role_path).read_text(encoding="utf-8")

def load_skills(skill_paths: list[str]) -> str:
    sections = []
    for path in skill_paths:
        p = BASE_DIR / path
        if not p.exists():
            console.print(f"[yellow]Warning: skill not found: {path}[/yellow]")
            continue
        sections.append(p.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(sections)

def build_system_prompt(manifest: dict) -> str:
    role = load_role(manifest["role"])
    skills = load_skills(manifest["skills"])
    return role + "\n\n---\n\n## Loaded Skills\n\n" + skills

class FileAgent:
    def __init__(self, manifest_path: str = "agent.yaml", mcp_path: str | None = None):
        self.client = openai.OpenAI()
        self.manifest = load_agent_manifest(manifest_path)
        self.model = self.manifest["model"]["name"]
        self.max_iterations = self.manifest["settings"]["max_iterations"]
        # MCP config path: from manifest if set, else override, else default
        resolved_mcp = mcp_path or self.manifest.get("mcp", "mcp.json")
        self.tools, self.tool_registry = load_tools_from_manifest(resolved_mcp)

        self.system_prompt = build_system_prompt(self.manifest)
        # OpenAI includes the system message in the conversation history list
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _add_user_message(self, content: str):
        """Append a user message to history."""
        self.conversation_history.append({"role": "user", "content": content})

    def _call_llm(self):
        """Make an API call with the current conversation history."""
        return self.client.chat.completions.create(
            model=self.model,
            tools=self.tools,
            messages=self.conversation_history,
        )
    
    # agent.py — after tool_loader
    def _execute_tool(self, name: str, tool_input: dict) -> str:
        if name not in self.tool_registry:
            return f"Error: tool '{name}' not available."
        return self.tool_registry[name](**tool_input)

    def _handle_tool_use(self, response) -> bool:
        """
        Process all tool call requests from a response.

        Returns True if tools were called (loop should continue),
        False if no tools were called (we have a final answer).
        """
        message = response.choices[0].message

        # Append the assistant's raw message object to history.
        # IMPORTANT: OpenAI requires this exact object (with tool_calls intact)
        # so the API knows which tool calls the subsequent results belong to.
        self.conversation_history.append(message)

        tool_calls = message.tool_calls
        if not tool_calls:
            return False  # No tools requested, we're done

        # Execute each tool and append results individually as role="tool" messages
        for tool_call in tool_calls:
            name = tool_call.function.name

            # OpenAI returns arguments as a JSON *string* — must parse it
            tool_input = json.loads(tool_call.function.arguments)

            console.print(
                f"  [dim]🔧 Calling tool:[/dim] [cyan]{name}[/cyan] "
                f"[dim]with[/dim] {tool_input}"
            )

            result = self._execute_tool(name, tool_input)

            console.print(
                f"  [dim]✓ Result preview: {result[:120].strip()}...[/dim]\n"
                if len(result) > 120
                else f"  [dim]✓ Result: {result}[/dim]\n"
            )

            # Each tool result is its own role="tool" message linked by tool_call_id
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,  # Must match the tool_call's id
                "content": result,
            })

        return True  # Tools were called, continue the loop

    def run(self, user_input: str) -> str:
        """
        The main agentic loop.

        1. Add user message to history
        2. Call LLM
        3. If LLM wants tools → execute them, add results, go to 2
        4. If LLM has final answer → extract text, return it
        """
        self._add_user_message(user_input)

        max_iterations = 10  # Safety valve — prevents infinite loops

        for iteration in range(max_iterations):
            console.print(f"[dim]  [Iteration {iteration + 1}][/dim]")

            response = self._call_llm()
            choice = response.choices[0]

            if choice.finish_reason == "stop":
                # LLM is done — extract the text response
                final_answer = choice.message.content
                # Save to history for future turns
                self.conversation_history.append(choice.message)
                return final_answer

            elif choice.finish_reason == "tool_calls":
                # LLM wants to call tools
                should_continue = self._handle_tool_use(response)
                if not should_continue:
                    break

            else:
                console.print(
                    f"[yellow]Warning: Unexpected finish_reason: {choice.finish_reason}[/yellow]"
                )
                break

        return "I reached the maximum number of reasoning steps without a final answer. Please try rephrasing."

    def reset(self):
        """Clear conversation history (preserve system message)."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        console.print("[dim]Conversation history cleared.[/dim]")