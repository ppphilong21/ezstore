"""Stage 4.1 helper: call one EZStore MCP tool directly and print the text it returns.

Usage (from agent/):
    uv run python scripts/call_mcp.py                       # list the 6 tools
    uv run python scripts/call_mcp.py get_quotation quotation_number=QT-20260330-001
    MCP_URL=http://localhost:8010/mcp uv run python scripts/call_mcp.py list_customer_quotations customer_name=史塔克工業
"""

from __future__ import annotations

import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCP_URL = os.getenv("MCP_URL", "http://localhost:8010/mcp")


def _parse(pairs: list[str]) -> dict:
    args: dict = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        try:
            args[key] = float(value) if key in ("new_pricing_factor", "target_total_price") else value
        except ValueError:
            args[key] = value
    return args


async def main(argv: list[str]) -> int:
    async with streamable_http_client(MCP_URL) as streams:
        read, write = streams[0], streams[1]
        async with ClientSession(read, write) as session:
            await session.initialize()
            if not argv:
                tools = await session.list_tools()
                print(f"MCP Server {MCP_URL} — {len(tools.tools)} tools:")
                for t in tools.tools:
                    print(f"  - {t.name}: {(t.description or '').splitlines()[0]}")
                return 0
            name, args = argv[0], _parse(argv[1:])
            print(f">>> {name}({args})  @ {MCP_URL}\n")
            result = await session.call_tool(name, args)
            for part in result.content:
                print(getattr(part, "text", part))
            return 1 if getattr(result, "is_error", getattr(result, "isError", False)) else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
