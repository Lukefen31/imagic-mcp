"""Introspection-only stdio MCP server for the imagic MCP server.

The real imagic MCP server ships inside the imagic desktop app and drives the
app's local photo library. It cannot run in a container. This stand-in exists
so MCP directories (for example Glama) can start a process and read the real
tool catalogue. It answers `initialize` and `tools/list` with the real tool
names, descriptions and input schemas (snapshotted in tools.json from the
shipping server). Every `tools/call` returns an error saying the imagic
desktop app is required. No tool does any work here.
"""

import asyncio
import json
from pathlib import Path

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

TOOLS = json.loads((Path(__file__).with_name("tools.json")).read_text(encoding="utf-8"))

NOT_AVAILABLE = (
    "The imagic MCP server runs inside the imagic desktop app and works on "
    "your local photo library, so this tool is not available in this container "
    "or listing stub. Install imagic from https://imagic.ink/desktop (free "
    "trial) and start it with: imagic --mcp. Setup: https://imagic.ink/mcp"
)

server = Server("imagic", version="1.4.4")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [types.Tool(**t) for t in TOOLS]


@server.call_tool(validate_input=False)
async def call_tool(name: str, arguments: dict):
    raise RuntimeError(NOT_AVAILABLE)


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
