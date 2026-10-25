"""Read-only access to the EZStore backend customer master (credit score is not exposed by the MCP tools)."""

from __future__ import annotations

import os
from typing import Any

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


async def find_customer(name: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(base_url=f"{BACKEND_URL}/api/v1", timeout=10) as client:
        r = await client.get("/customers", params={"search": name, "page_size": 100})
        r.raise_for_status()
        rows = r.json().get("data") or []
    if not rows:
        return None
    exact = [c for c in rows if c.get("name") == name]
    return (exact or rows)[0]
