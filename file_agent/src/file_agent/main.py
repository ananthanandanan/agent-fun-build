
import sys
import openai
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule

from .agent import FileAgent

console = Console()

from dotenv import load_dotenv
load_dotenv()


HELP_TEXT = """
[bold]Available commands:[/bold]
  [cyan]reset[/cyan]    — Clear conversation history and start fresh
  [cyan]history[/cyan]  — Show how many messages are in the current context
  [cyan]exit[/cyan]     — Quit the agent
  [cyan]help[/cyan]     — Show this message

[dim]Tip: Ask things like:[/dim]
  "What Python files are in my current directory?"
  "Read the README in this project"
  "Find all .env files in my home directory"
  "What does the pyproject.toml say about dependencies?"
"""


def main():
    console.print(Panel.fit(
        "[bold cyan]Context-Aware File Agent[/bold cyan]\n"
        "[dim]Powered by OpenAI + Manual Orchestration[/dim]",
        border_style="cyan"
    ))
    console.print(HELP_TEXT)
    
    agent = FileAgent()
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            sys.exit(0)
        
        if not user_input:
            continue
        
        # Handle meta-commands
        if user_input.lower() == "exit":
            console.print("[dim]Goodbye![/dim]")
            sys.exit(0)
        
        elif user_input.lower() == "reset":
            agent.reset()
            continue
        
        elif user_input.lower() == "history":
            n = len(agent.conversation_history)
            console.print(f"[dim]Conversation history: {n} message(s)[/dim]")
            continue
        
        elif user_input.lower() == "help":
            console.print(HELP_TEXT)
            continue
        
        # Run the agent
        console.print(Rule("[dim]Agent thinking...[/dim]", style="dim"))
        
        try:
            answer = agent.run(user_input)
        except openai.APIError as e:
            console.print(f"[red]API Error: {e}[/red]")
            continue
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            raise
        
        console.print(Rule(style="dim"))
        console.print(Panel(
            answer,
            title="[bold blue]Agent[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        ))


if __name__ == "__main__":
    main()