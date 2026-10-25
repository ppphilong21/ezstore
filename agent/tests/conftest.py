"""Shared fixtures: run the real Workflow with a fake classifier (no API key needed)."""

from __future__ import annotations

import os
import uuid
from typing import Any

import pytest
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.runners import InMemoryRunner
from google.genai import types

from quotation_agent.agent import build_workflow, make_classifier
from tests.support.fake_llm import FakeLlm

os.environ.setdefault("GOOGLE_API_USE_CLIENT_CERTIFICATE", "false")


class Chat:
    """Drives one session of the workflow and returns what the Chat UI would show."""

    def __init__(self, llm: FakeLlm | None = None):
        self.llm = llm or FakeLlm()
        self.app = App(
            name="quotation_agent",
            root_agent=build_workflow(make_classifier(self.llm), check_credentials=False),
        )
        self.runner = InMemoryRunner(app=self.app)
        self.session_id: str | None = None
        self.events: list[Event] = []

    async def _session(self) -> str:
        if self.session_id is None:
            s = await self.runner.session_service.create_session(app_name="quotation_agent", user_id="u")
            self.session_id = s.id
        return self.session_id

    async def seed(self, user: str, agent: str) -> None:
        """Add a prior turn as plain events (like agents-cli eval does), without session state."""
        sid = await self._session()
        session = await self.runner.session_service.get_session(app_name="quotation_agent", user_id="u", session_id=sid)
        for author, role, text in (("user", "user", user), ("agent", "model", agent)):
            await self.runner.session_service.append_event(
                session,
                Event(author=author, invocation_id=f"seed-{uuid.uuid4().hex[:6]}",
                      content=types.Content(role=role, parts=[types.Part(text=text)])),
            )

    async def send(self, text: str) -> str:
        sid = await self._session()
        reply = ""
        self.events = []
        async for ev in self.runner.run_async(
            user_id="u", session_id=sid,
            new_message=types.Content(role="user", parts=[types.Part(text=text)]),
        ):
            self.events.append(ev)
            path = ev.node_info.path if ev.node_info else ""
            if path.split("/")[-1].startswith("respond@") and ev.content and ev.content.parts:
                reply = "".join(p.text or "" for p in ev.content.parts)
        return reply

    def tool_calls(self) -> list[str]:
        return [fc.name for ev in self.events for fc in ev.get_function_calls()]

    async def state(self) -> dict[str, Any]:
        s = await self.runner.session_service.get_session(app_name="quotation_agent", user_id="u", session_id=self.session_id)
        return dict(s.state)


@pytest.fixture
def chat() -> Chat:
    return Chat()
