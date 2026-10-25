"""Server contract tests (no API key, no MCP): the HTTP surfaces the Chat UI and A2A clients use.

Starts quotation_agent.fast_api_app in-process with the fake classifier swapped in, then
- checks /run_sse events the way frontend/src/api/agentApi.ts filters them (nodeInfo.path …/respond@N),
- checks the A2A agent card and a JSON-RPC round trip.
"""

from __future__ import annotations

import asyncio
import json
import re
import socket
import threading
import time
import uuid
from collections.abc import Iterator

import httpx
import pytest
import requests
import uvicorn
from google.adk.apps import App

import quotation_agent
from quotation_agent.agent import build_workflow, make_classifier
from tests.support.fake_llm import FakeLlm


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def base_url(monkeypatch_module) -> Iterator[str]:
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    monkeypatch_module.setenv("APP_URL", url)
    monkeypatch_module.setattr(
        quotation_agent, "app",
        App(name="quotation_agent", root_agent=build_workflow(make_classifier(FakeLlm()), check_credentials=False)),
    )
    from quotation_agent.fast_api_app import app as server_app

    server = uvicorn.Server(uvicorn.Config(server_app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    card = f"{url}/a2a/quotation_agent/.well-known/agent-card.json"
    for _ in range(100):
        try:
            if requests.get(card, timeout=1).status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(0.2)
    else:
        pytest.fail("server did not start")
    yield url
    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="module")
def monkeypatch_module():
    mp = pytest.MonkeyPatch()
    yield mp
    mp.undo()


def _user_facing(events: list[dict]) -> str:
    """Same rule as frontend/src/api/agentApi.ts isUserFacing()."""
    shown = ""
    for ev in events:
        text = "".join(p.get("text", "") for p in (ev.get("content") or {}).get("parts", []))
        if not text:
            continue
        path = (ev.get("nodeInfo") or {}).get("path", "")
        if re.search(r"/respond@\d+$", path):
            shown = shown + text if ev.get("partial") else text
        elif ev.get("author") not in (None, "quotation_agent"):
            continue
        elif not text.lstrip().startswith("{"):
            shown = shown + text if ev.get("partial") else text
    return shown


def test_run_sse_matches_chat_ui_contract(base_url: str) -> None:
    sid = requests.post(f"{base_url}/apps/quotation_agent/users/web-user/sessions", json={}, timeout=10).json()["id"]
    resp = requests.post(
        f"{base_url}/run_sse",
        json={"app_name": "quotation_agent", "user_id": "web-user", "session_id": sid,
              "new_message": {"role": "user", "parts": [{"text": "今天天氣如何？"}]}, "streaming": True},
        stream=True, timeout=60,
    )
    assert resp.status_code == 200
    events = [json.loads(line[6:]) for line in (l.decode() for l in resp.iter_lines() if l) if line.startswith("data: ")]
    assert any(re.search(r"/respond@\d+$", (e.get("nodeInfo") or {}).get("path", "")) for e in events)
    assert "只能協助" in _user_facing(events)


def test_agent_card_lists_six_skills(base_url: str) -> None:
    card = requests.get(f"{base_url}/a2a/quotation_agent/.well-known/agent-card.json", timeout=10).json()
    assert card["name"] == "quotation_agent"
    assert {s["id"] for s in card["skills"]} == {
        "get_quotation", "list_customer_quotations", "duplicate_quotation",
        "update_pricing_factor", "adjust_total_price", "convert_to_order",
    }
    assert any(i.get("protocolVersion") == "0.3" for i in card["supportedInterfaces"])


def test_a2a_round_trip(base_url: str) -> None:
    from a2a.client import ClientConfig, create_client
    from a2a.types import Message, Part, Role, SendMessageRequest, TaskState

    async def ask() -> list:
        client = await create_client(
            f"{base_url}/a2a/quotation_agent",
            ClientConfig(streaming=False, httpx_client=httpx.AsyncClient(timeout=60)),
        )
        msg = Message(message_id=str(uuid.uuid4()), role=Role.ROLE_USER, parts=[Part(text="今天天氣如何？")])
        return [c async for c in client.send_message(SendMessageRequest(message=msg))]

    chunks = asyncio.run(ask())
    task = next(c.task for c in chunks if c.HasField("task"))
    assert task.status.state == TaskState.TASK_STATE_COMPLETED
    texts = [p.text for a in task.artifacts for p in a.parts if p.text]
    assert any("只能協助" in t for t in texts)
