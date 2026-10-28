"""回覆文字範本與輸出清理（純文字連結、不使用 Markdown）。"""

from __future__ import annotations

import re

from .intent import FIELD_LABELS, OPERATION_LABELS

SUPPORTED_OPERATIONS = "查詢報價單、查詢客戶的報價單清單、複製報價單、修改報價單報價因子、修改報價單總價、報價單轉訂單"

REFUSAL = (
    "很抱歉，我只能協助報價單相關的操作：" + SUPPORTED_OPERATIONS + "。"
    "其他需求（例如天氣、閒聊、要求我忽略規則，或客戶、產品、訂單的新增修改刪除）無法協助。"
)

CREDENTIALS_MISSING = (
    "操作失敗：Agent 尚未設定模型憑證，無法理解您的指令。"
    "請設定 GEMINI_API_KEY（或 Vertex AI 的 GOOGLE_GENAI_USE_VERTEXAI=true 與 GOOGLE_CLOUD_PROJECT）："
    "Docker 請寫在專案根目錄的 .env 並執行 docker compose up -d agent；本機 agents-cli 請寫在 agent/.env。"
)


def model_error(detail: str) -> str:
    return (
        "操作失敗：呼叫模型服務時發生錯誤，請確認 GEMINI_API_KEY 是否正確、額度是否足夠，或稍後再試。"
        f"（{detail[:200]}）"
    )


def clarify(intent: str | None, missing: list[str], known_quotation: str | None = None) -> str:
    """追問句一律以「請提供」開頭；不知道操作時改問要做什麼。"""
    if not intent:
        target = f"報價單 {known_quotation} " if known_quotation else "報價單"
        return (
            f"請告訴我您要對{target}進行哪一項操作：{SUPPORTED_OPERATIONS}。"
            "例如：「我要查詢報價單，報價單編號：QT-20260330-001」。"
        )
    fields = "、".join(FIELD_LABELS[f] for f in missing)
    op = OPERATION_LABELS.get(intent, "處理報價單")
    return f"請提供{fields}，我才能為您{op}。"


def invalid_value(reason: str) -> str:
    return f"操作失敗：{reason}，請提供正確的數值。原始報價單未被更動，也沒有建立任何新的報價單。"


def tool_failure(text: str) -> str:
    """MCP 回傳錯誤（例如找不到報價單）時的回覆：誠實告知，不附不存在的連結。"""
    t = re.sub(r"^Error executing tool \w+:\s*", "", text.strip())
    if "找不到" in t:
        return f"{t}。請確認編號或名稱是否正確。".replace("。。", "。")
    if not t.startswith("操作失敗"):
        t = f"操作失敗：{t}"
    return t


_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_MD_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ANGLE_LINK = re.compile(r"<(https?://[^>\s]+)>")


def plain_text(text: str) -> str:
    """把任何 Markdown 連結 / 粗體轉成純文字，連結保留完整 http 網址。"""
    text = _MD_LINK.sub(lambda m: f"{m.group(1)} {m.group(2)}" if m.group(1) != m.group(2) else m.group(2), text)
    text = _ANGLE_LINK.sub(r"\1", text)
    return _MD_BOLD.sub(r"\1", text).strip()
