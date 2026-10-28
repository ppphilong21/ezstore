"""Function tools of the sales advisor agent.

okf_*                 read the OKF knowledge bundle (progressive disclosure: index → concept → links)
get_customer_profile  read-only customer master (tier, credit score) from the EZStore backend
review_quotation      A2A get_quotation from the quotation agent + deterministic policy review from OKF values
ask_quotation_agent   delegate any quotation operation to the quotation agent over A2A
"""

from __future__ import annotations

import functools
import re
from typing import Any

from . import a2a_client, backend
from .okf import Bundle
from .policy import credit_action, parse_quotation_text, review

_QT = re.compile(r"QT-\d{8}-\d{3}", re.I)
_MODIFYING = re.compile(r"複製|修改|改為|改成|調整|轉訂單|轉成訂單|duplicate|update|adjust|convert", re.I)


@functools.cache
def bundle() -> Bundle:
    return Bundle()


def okf_list(directory: str = "") -> dict[str, Any]:
    """列出知識庫某個目錄的 index（先看目錄再讀概念）。

    Args:
        directory: 目錄名稱，例如 "" (根目錄)、"policies"、"lessons-learned"。

    Returns:
        該目錄 index.md 的內容。
    """
    return {"directory": directory or "/", "index": bundle().index(directory)}


def okf_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """用關鍵字搜尋知識庫概念（標題、描述、標籤、內文）。

    Args:
        query: 關鍵字，例如 "利潤率 核准"、"VIP 報價因子"、"轉訂單 信用"。
        top_k: 最多回傳幾筆。

    Returns:
        依相關度排序的概念清單（id、type、title、description）。
    """
    return {"query": query, "results": bundle().search(query, top_k)}


def okf_read(concept_id: str) -> dict[str, Any]:
    """讀取一個知識概念的完整內容（frontmatter 與內文）以及它連到的其他概念。

    Args:
        concept_id: 概念 ID，也就是檔案路徑去掉 .md，例如 "policies/minimum-profit-rate"。

    Returns:
        概念內容；找不到時回傳 error。
    """
    c = bundle().get(concept_id)
    if c is None:
        hits = bundle().search(concept_id.replace("/", " ").replace("-", " "), 3)
        return {"error": f"知識庫沒有概念 {concept_id}", "did_you_mean": [h["id"] for h in hits]}
    meta = {k: v for k, v in c.meta.items() if k not in ("generated",)}
    return {"id": c.id, "frontmatter": meta, "body": c.body, "links_to": c.links, "linked_from": bundle().backlinks(c.id)}


async def get_customer_profile(customer_name: str) -> dict[str, Any]:
    """查詢客戶主檔（唯讀）：等級、信用分數，以及依信用規則轉訂單時的條件。

    Args:
        customer_name: 客戶名稱，可用部分名稱，例如 "史塔克工業"。

    Returns:
        客戶等級、信用分數與轉訂單條件；找不到時回傳 error。
    """
    try:
        c = await backend.find_customer(customer_name)
    except Exception as e:  # noqa: BLE001
        return {"error": f"無法查詢客戶主檔（{backend.BACKEND_URL}）：{type(e).__name__}"}
    if not c:
        return {"error": f"找不到客戶「{customer_name}」"}
    rules = bundle().policy()["credit_rules"]
    score = c.get("credit_score")
    return {
        "name": c.get("name"),
        "level": c.get("level"),
        "credit_score": score,
        "order_condition": credit_action(score, rules) or "可直接轉訂單",
        "source": "policies/customer-credit-policy",
    }


async def review_quotation(quotation_number: str) -> dict[str, Any]:
    """檢查一張報價單是否符合公司報價政策，並提出建議的報價因子。

    透過 A2A 向報價 Agent 取得報價單，再依知識庫的政策（報價因子區間、利潤率下限、信用規則）逐項檢查。

    Args:
        quotation_number: 報價單編號，例如 "QT-20260330-001"。

    Returns:
        verdict（compliant / warning / needs_approval / violation）、逐項檢查、需要的核准、建議因子與依據的概念 ID。
    """
    m = _QT.search(quotation_number or "")
    if not m:
        return {"error": "請提供報價單編號，格式 QT-YYYYMMDD-NNN"}
    number = m.group(0).upper()
    reply = await a2a_client.ask(f"我要查詢報價單，報價單編號：{number}")
    if not reply.ok or "找不到" in reply.text:
        return {"error": reply.text, "via": "A2A quotation_agent"}
    q = parse_quotation_text(reply.text)
    if "pricing_factor" not in q:
        return {"error": "無法解析報價 Agent 的回覆", "raw": reply.text}
    credit = None
    if q.get("customer"):
        try:
            c = await backend.find_customer(q["customer"])
            credit = c.get("credit_score") if c else None
        except Exception:  # noqa: BLE001
            credit = None
    result = review(q, bundle().policy(), credit)
    result["via"] = {"a2a_agent": "quotation_agent", "a2a_task_id": reply.task_id}
    return result


async def ask_quotation_agent(request: str, confirmed: bool = False) -> dict[str, Any]:
    """透過 A2A 協定請報價 Agent 執行報價單操作，回傳它的回覆。

    報價 Agent 可以：查詢報價單、查詢客戶的報價單清單、複製報價單、修改報價因子、修改總價、報價單轉訂單。
    會改資料的操作（複製、修改、轉訂單）必須先得到使用者明確同意，並傳 confirmed=True。

    Args:
        request: 給報價 Agent 的完整中文指令，例如 "我要修改報價單報價因子，報價單編號：QT-20260330-001，報價因子改為 1.1"。
        confirmed: 使用者是否已明確同意這個會改資料的操作。

    Returns:
        報價 Agent 的回覆文字（含系統連結）。
    """
    if _MODIFYING.search(request) and not confirmed:
        return {"status": "needs_confirmation",
                "message": "這個操作會建立副本或訂單，請先向使用者說明並取得同意，再以 confirmed=True 呼叫。"}
    reply = await a2a_client.ask(request)
    return {"ok": reply.ok, "reply": reply.text, "a2a_task_id": reply.task_id, "a2a_state": reply.state}
