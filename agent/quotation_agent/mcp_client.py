"""連接 EZStore MCP Server（Streamable HTTP）並呼叫單一工具。

每個操作節點只呼叫一個 MCP 工具：McpToolset.get_tools() → tool.run_async()。
MCP 回傳 isError（例如找不到報價單）時，把錯誤文字原樣交給 respond 節點，不丟例外。
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

logger = logging.getLogger(__name__)

MCP_URL = os.getenv("MCP_URL", "http://localhost:8010/mcp")

_toolset: McpToolset | None = None


def get_toolset() -> McpToolset:
    """Process-wide toolset（連線與工具清單會被重用）。"""
    global _toolset
    if _toolset is None:
        _toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_URL,
                timeout=10.0,
                # adjust_total_price 最多 20 次 PUT，讀取逾時放寬
                sse_read_timeout=180.0,
            ),
            tool_list_cache_ttl_seconds=300,
        )
    return _toolset


@dataclass
class ToolResult:
    ok: bool
    text: str


def _result_text(result: Any) -> str:
    if isinstance(result, dict):
        parts = result.get("content") or []
        texts = [p.get("text", "") for p in parts if isinstance(p, dict) and p.get("type") == "text"]
        if texts:
            return "\n".join(t for t in texts if t)
        if "structuredContent" in result and isinstance(result["structuredContent"], dict):
            inner = result["structuredContent"].get("result")
            if isinstance(inner, str):
                return inner
        if "error" in result:
            return str(result["error"])
    return str(result)


async def call_tool(name: str, args: dict[str, Any], tool_context: Any) -> ToolResult:
    """呼叫 MCP 工具；連線失敗也回傳 ToolResult(ok=False)，讓 respond 節點給清楚的訊息。"""
    try:
        tools = {t.name: t for t in await get_toolset().get_tools()}
    except Exception as e:  # noqa: BLE001
        logger.exception("MCP get_tools failed")
        return ToolResult(False, f"操作失敗：無法連線 MCP Server（{MCP_URL}），請確認 mcp-server 服務已啟動。（{type(e).__name__}）")
    tool = tools.get(name)
    if tool is None:
        return ToolResult(False, f"操作失敗：MCP Server 沒有提供 {name} 工具。")
    try:
        result = await tool.run_async(args=args, tool_context=tool_context)
    except Exception as e:  # noqa: BLE001
        logger.exception("MCP tool %s failed", name)
        return ToolResult(False, f"操作失敗：呼叫 {name} 時發生錯誤（{type(e).__name__}: {e}）。")
    is_error = isinstance(result, dict) and bool(result.get("isError") or result.get("is_error"))
    return ToolResult(not is_error, _result_text(result).strip())
