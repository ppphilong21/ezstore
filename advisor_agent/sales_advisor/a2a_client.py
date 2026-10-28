"""A2A client for the EZStore quotation agent (a2a-sdk 1.x, JSON-RPC).

The advisor never touches MCP or the database for quotation operations: it sends a natural-language request to
the quotation agent over the Agent2Agent protocol and reads the text artifact of the completed task.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

import httpx
from a2a.client import ClientConfig, create_client
from a2a.types import Message, Part, Role, SendMessageRequest, TaskState

QUOTATION_AGENT_A2A_URL = os.getenv("QUOTATION_AGENT_A2A_URL", "http://localhost:8080/a2a/quotation_agent")


@dataclass
class A2AReply:
    ok: bool
    text: str
    task_id: str = ""
    state: str = ""


async def fetch_agent_card(url: str | None = None) -> dict:
    base = (url or QUOTATION_AGENT_A2A_URL).rstrip("/")
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{base}/.well-known/agent-card.json")
        r.raise_for_status()
        return r.json()


async def ask(request: str, url: str | None = None, timeout: float = 180.0) -> A2AReply:
    """Send one message to the quotation agent and return the final reply text."""
    base = (url or QUOTATION_AGENT_A2A_URL).rstrip("/")
    try:
        client = await create_client(
            base, ClientConfig(streaming=False, httpx_client=httpx.AsyncClient(timeout=timeout))
        )
        message = Message(message_id=str(uuid.uuid4()), role=Role.ROLE_USER, parts=[Part(text=request)])
        texts: list[str] = []
        task_id, state = "", ""
        async for chunk in client.send_message(SendMessageRequest(message=message)):
            if chunk.HasField("task"):
                task = chunk.task
                task_id = task.id
                state = TaskState.Name(task.status.state)
                for artifact in task.artifacts:
                    texts += [p.text for p in artifact.parts if p.text]
                if not texts and task.status.HasField("message"):
                    texts += [p.text for p in task.status.message.parts if p.text]
            elif chunk.HasField("message"):
                texts += [p.text for p in chunk.message.parts if p.text]
        text = texts[-1].strip() if texts else ""
        ok = bool(text) and state in ("", "TASK_STATE_COMPLETED")
        return A2AReply(ok, text or f"報價 Agent 沒有回覆（task state: {state or 'unknown'}）", task_id, state)
    except Exception as e:  # noqa: BLE001
        return A2AReply(False, f"無法透過 A2A 連線報價 Agent（{base}）：{type(e).__name__}: {e}")
