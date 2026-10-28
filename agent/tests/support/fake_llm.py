"""離線測試用的假模型：不呼叫 Gemini，用規則把分類器 prompt 轉成 Intent JSON。

讓 unit / integration 測試能在沒有 API key 的情況下跑完整個 Workflow
（LlmAgent 包裝、output_schema 驗證、路由、MCP 呼叫、respond 都是真的）。
"""

from __future__ import annotations

import json
import re
from collections.abc import AsyncGenerator

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from quotation_agent.intent import code_extract, keyword_intent

OFF_TOPIC = re.compile(r"天氣|笑話|股票|weather|joke|新增客戶|刪除產品|翻譯")


def classify(prompt: str) -> dict:
    message = prompt.split("【本次使用者訊息】", 1)[-1].strip()
    pending = re.search(r"【待補資料的操作】\n(.+?)\n", prompt + "\n")
    pending_intent = None
    if pending:
        m = re.search(r"（(\w+)）", pending.group(1))
        pending_intent = m.group(1) if m else None
    fields = code_extract(message)
    if OFF_TOPIC.search(message):
        intent = "off_topic"
    else:
        intent = keyword_intent(message) or pending_intent or "unclear"
    return {"intent": intent, **fields}


class FakeLlm(BaseLlm):
    model: str = "fake-classifier"
    calls: int = 0
    fail_with: str | None = None

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        self.calls += 1
        if self.fail_with:
            raise RuntimeError(self.fail_with)
        prompt = "".join(
            p.text or "" for c in llm_request.contents for p in (c.parts or []) if c.role == "user"
        )
        payload = json.dumps(classify(prompt), ensure_ascii=False)
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text=payload)]))
