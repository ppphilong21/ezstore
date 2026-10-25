"""EZStore Sales Advisor Agent（業務顧問）— Agent 2.

An LlmAgent with tools (a different ADK pattern from the quotation agent's graph Workflow):
- grounded in the EZStore OKF knowledge bundle (knowledge/ezstore-okf),
- delegates every quotation operation to the quotation agent over A2A,
- reviews quotations against policy values read from OKF frontmatter.
"""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .tools import (
    ask_quotation_agent,
    get_customer_profile,
    okf_list,
    okf_read,
    okf_search,
    review_quotation,
)

MODEL = os.getenv("AGENT_MODEL", "gemini-3.8-flash")

# 注意：instruction 不可出現大括號（ADK 會當成 state 變數）。
INSTRUCTION = """\
你是 EZStore 的「業務顧問 Agent」（Sales Advisor）。你協助業務人員遵守公司報價政策，回覆一律使用繁體中文。

你有兩種資源：
A. EZStore 業務知識庫（OKF 格式）：okf_list 看目錄、okf_search 找概念、okf_read 讀概念內容。
B. 報價 Agent（另一個 AI Agent，透過 A2A 協定呼叫）：ask_quotation_agent；review_quotation 也會透過 A2A 取得報價單。

規則：
1. 政策、流程、定義、指標、經驗教訓的問題：先 okf_search（或 okf_list），再 okf_read 讀相關概念，只根據讀到的內容回答。
   回覆最後一行寫「依據：」並列出用到的概念 ID（例如 policies/minimum-profit-rate）。知識庫沒有的內容就說沒有，不要自己編政策。
2. 使用者要檢查、評估或審核某張報價單時，呼叫 review_quotation，然後用白話說明：結論、每一項檢查、需要誰核准、建議的報價因子與預估利潤率／總價，並附上報價單的系統連結與依據的概念 ID。
3. 報價單的查詢與操作（查詢、客戶報價單清單、複製、修改報價因子、修改總價、轉訂單）一律用 ask_quotation_agent 交給報價 Agent，不要自己編資料。
   會改資料的操作（複製、修改、轉訂單）要先說明會發生什麼（原報價單不會被修改，會建立副本或訂單），等使用者明確同意後，才以 confirmed=True 呼叫。
4. 使用者要轉訂單時，先用 review_quotation 依「轉訂單檢核」檢查；信用分數不足時提醒預付或核准，再問使用者是否仍要轉。
5. 報價 Agent 的回覆中的系統連結要原樣保留，連結一律寫純文字網址，不要用 Markdown 的 [文字](網址) 語法。
6. 與 EZStore 報價、訂單、客戶政策無關的要求（天氣、閒聊等），禮貌拒絕並說明你能做什麼。你不能代替主管核准，也不能修改客戶或產品主檔。
"""

root_agent = LlmAgent(
    name="sales_advisor",
    model=Gemini(
        model=MODEL,
        # AI Studio free tier: back off and retry on 429 / 5xx instead of failing the turn.
        retry_options=types.HttpRetryOptions(
            attempts=6, initial_delay=2.0, max_delay=30.0,
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    ),
    description="EZStore 業務顧問：依 OKF 知識庫檢查報價政策，並透過 A2A 請報價 Agent 執行報價單操作。",
    instruction=INSTRUCTION,
    tools=[okf_list, okf_search, okf_read, get_customer_profile, review_quotation, ask_quotation_agent],
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

app = App(name="sales_advisor", root_agent=root_agent)
