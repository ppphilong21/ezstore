"""Offline integration tests: real Workflow + real MCP Server, fake classifier (no API key).

Needs the MCP Server reachable at MCP_URL (default http://localhost:8010/mcp), i.e.
`docker compose up -d db backend mcp-server` and the seed loaded. Skipped otherwise.
Read-only operations only, so it never changes data.
"""

from __future__ import annotations

import os
import re

import httpx
import pytest

from tests.conftest import Chat

MCP_URL = os.getenv("MCP_URL", "http://localhost:8010/mcp")


def _mcp_up() -> bool:
    try:
        r = httpx.post(MCP_URL, json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                       headers={"Accept": "application/json, text/event-stream"}, timeout=2)
        return r.status_code < 500
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(not _mcp_up(), reason=f"MCP Server not reachable at {MCP_URL}")


@pytest.mark.asyncio
async def test_get_quotation_via_mcp():
    chat = Chat()
    reply = await chat.send("我要查詢報價單，報價單編號：QT-20260330-001")
    assert "QT-20260330-001" in reply
    assert "A4影印紙" in reply
    assert re.search(r"http://\S+/quotations/\d+", reply)


@pytest.mark.asyncio
async def test_list_customer_quotations_via_mcp():
    chat = Chat()
    reply = await chat.send("我要查詢客戶的報價單清單，客戶名稱：史塔克工業")
    assert "QT-20260115-001" in reply


@pytest.mark.asyncio
async def test_clarify_then_complete_via_mcp():
    chat = Chat()
    assert (await chat.send("我要查詢報價單")).startswith("請提供")
    reply = await chat.send("QT-20260330-001")
    assert "A4影印紙" in reply


@pytest.mark.asyncio
async def test_not_found_via_mcp():
    chat = Chat()
    reply = await chat.send("我要查詢報價單，報價單編號：QT-20990101-001")
    assert "找不到" in reply
    assert not re.search(r"/quotations/\d+", reply)
