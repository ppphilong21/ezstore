"""Run the real LlmAgent tool loop with a scripted fake model (verifies ADK tool wiring without Gemini)."""

from collections.abc import AsyncGenerator

import pytest
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types

from sales_advisor import agent as advisor_agent
from tests.unit.test_policy_and_tools import stub_a2a  # noqa: F401  (fixture)


class ScriptedLlm(BaseLlm):
    model: str = "scripted"
    seen_tool_results: list = []

    async def generate_content_async(self, llm_request: LlmRequest, stream: bool = False) -> AsyncGenerator[LlmResponse, None]:
        responses = [p.function_response for c in llm_request.contents for p in (c.parts or []) if p.function_response]
        if not responses:
            call = types.FunctionCall(name="review_quotation", args={"quotation_number": "QT-20260115-001"})
            yield LlmResponse(content=types.Content(role="model", parts=[types.Part(function_call=call)]))
            return
        self.seen_tool_results.append(responses[-1].response)
        verdict = responses[-1].response.get("verdict")
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text=f"結論：{verdict}\n依據：policies/minimum-profit-rate")]))


@pytest.mark.asyncio
async def test_tool_loop_review(stub_a2a):  # noqa: F811
    llm = ScriptedLlm()
    agent = LlmAgent(name="sales_advisor", model=llm, instruction=advisor_agent.INSTRUCTION,
                     tools=advisor_agent.root_agent.tools)
    runner = InMemoryRunner(app=App(name="sales_advisor", root_agent=agent))
    s = await runner.session_service.create_session(app_name="sales_advisor", user_id="u")
    texts = []
    async for ev in runner.run_async(user_id="u", session_id=s.id,
                                     new_message=types.Content(role="user", parts=[types.Part(text="幫我檢查 QT-20260115-001 是否合規")])):
        if ev.content and ev.content.parts:
            texts += [p.text for p in ev.content.parts if p.text]
    assert stub_a2a == ["我要查詢報價單，報價單編號：QT-20260115-001"]
    assert llm.seen_tool_results[-1]["verdict"] == "needs_approval"
    assert "needs_approval" in texts[-1]
