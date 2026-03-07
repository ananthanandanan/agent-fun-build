# file_agent_mcp/mcp_client.py
#
# Connects to one or more MCP servers defined in mcp.json.
# Uses the official MCP SDK pattern: AsyncExitStack + ClientSession.
#
# Usage in agent.py:
#   self.mcp = MCPClient()
#   await self.mcp.connect_all("mcp.json")
#   self.tools = self.mcp.get_openai_tools()
#   result = await self.mcp.call_tool("read_file", {"path": "..."})

import json
import logging
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent 


class MCPClient:
    """
    Manages connections to all MCP servers declared in mcp.json.

    Lifecycle:
        client = MCPClient()
        await client.connect_all("file_agent/mcp.json")
        tools  = client.get_openai_tools()      # pass to LLM
        result = await client.call_tool(name, args)
        await client.cleanup()
    """

    def __init__(self):
        # AsyncExitStack keeps all server subprocesses alive until cleanup()
        self.exit_stack = AsyncExitStack()

        # List of (session, [tool_names]) — one entry per connected server
        self._sessions: list[tuple[ClientSession, list[str]]] = []

        # Flat cache: tool_name → ClientSession that owns it
        self._tool_owner: dict[str, ClientSession] = {}

        # OpenAI-format tool schemas, populated after connect_all()
        self._openai_tools: list[dict] = []

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    async def connect_all(self, mcp_config_path: str = "mcp.json"):
        """Read mcp.json and connect to every server listed there."""
        with open(BASE_DIR / mcp_config_path) as f:
            config = json.load(f)

        for server in config["servers"]:
            await self._connect_server(server)

        logger.info(
            f"MCP ready — {len(self._sessions)} server(s), "
            f"{len(self._openai_tools)} tool(s) total"
        )

    async def _connect_server(self, server_config: dict):
        """Spawn one MCP server subprocess and fetch its tools."""
        name = server_config["name"]
        command = server_config["command"]        # e.g. "uv"
        args = server_config.get("args", [])     # e.g. ["run", "python", "-m", "file_agent_mcp.mcp_server"]

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=server_config.get("env"),        # optional env vars
        )

        # stdio_client returns (read_stream, write_stream)
        # enter_async_context keeps the subprocess alive for the stack's lifetime
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        ) # this is the transport object that will be used to communicate with the server
        read_stream, write_stream = stdio_transport

        session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        ) # this is the session object that will be used to call the tools
        await session.initialize() ## this is simply the handshake to establish the connection

        # Fetch tool list from this server
        tools_response = await session.list_tools()
        tool_names = [t.name for t in tools_response.tools]

        # Register ownership so call_tool() knows which session to use
        for tool in tools_response.tools:
            self._tool_owner[tool.name] = session

            # Convert MCP tool schema → OpenAI function-calling format
            self._openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    # MCP's inputSchema is already valid JSON Schema
                    "parameters": dict(tool.inputSchema),
                },
            })

        logger.info(f"Connected to '{name}' — tools: {tool_names}")
        self._sessions.append((session, tool_names))

    # ------------------------------------------------------------------
    # Tool access
    # ------------------------------------------------------------------

    def get_openai_tools(self) -> list[dict]:
        """Return all tools in OpenAI function-calling format.
        Pass this directly to tools= in your chat.completions.create() call."""
        return self._openai_tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Execute a tool by name and return the result as a plain string.

        Raises ValueError if no connected server owns the tool.
        """
        session = self._tool_owner.get(name)
        if session is None:
            return f"Error: no MCP server has a tool named '{name}'"

        result = await session.call_tool(name, arguments)

        # MCP returns a list of content blocks; join all text blocks
        parts = []
        for block in result.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts) if parts else "(no output)"

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def cleanup(self):
        """Close all server connections and terminate subprocesses."""
        await self.exit_stack.aclose()
        logger.info("MCP connections closed.")