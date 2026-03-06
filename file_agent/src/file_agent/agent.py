# src/file_agent/agent.py
import json
import openai
from rich.console import Console
from rich.panel import Panel

from .tools import execute_tool
from .tool_schemas import TOOLS

console = Console()

SYSTEM_PROMPT = """You are a helpful CLI assistant that can navigate and read the local filesystem to answer questions.

You have access to tools that let you:
- Find out your current working directory
- List directory contents
- Read file contents
- Search for files by name pattern

When a user asks about files or directories:
1. Start by getting your bearings (working directory) if you don't know where you are
2. Navigate step by step — list directories before trying to read files inside them
3. If you can't find something, try searching with a pattern
4. Always report what you actually found, not what you expect to find
5. Be concise in your final answer

Important: Only use tools when you need filesystem information. For general questions, answer directly.

{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The file is located in the current directory.",
        "tool_calls": [
          {
            "function": {
              "name": "list_directory",
              "arguments": "{\"path\": \"/home/user/documents\"}"
            },
            "id": "tool-call-1"
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "tool_calls": [
    {
      "function": {
        "name": "list_directory",
        "arguments": "{\"path\": \"/home/user/documents\"}"
      },
      "id": "tool-call-1"
    }
  ]
}

"""


class FileAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI()
        self.model = model
        # OpenAI includes the system message in the conversation history list
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def _add_user_message(self, content: str):
        """Append a user message to history."""
        self.conversation_history.append({"role": "user", "content": content})

    def _call_llm(self):
        """Make an API call with the current conversation history."""
        return self.client.chat.completions.create(
            model=self.model,
            tools=TOOLS,
            messages=self.conversation_history,
        )

    def _handle_tool_use(self, response) -> bool:
        """
        Process all tool call requests from a response.

        Returns True if tools were called (loop should continue),
        False if no tools were called (we have a final answer).
        """
        message = response.choices[0].message
        print( "message:", message)
        print( "response:", response)

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

            result = execute_tool(name, tool_input)

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
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        console.print("[dim]Conversation history cleared.[/dim]")