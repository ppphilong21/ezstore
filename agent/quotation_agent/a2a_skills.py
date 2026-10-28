"""A2A agent card skills: one per quotation operation (shown at /a2a/quotation_agent/.well-known/agent-card.json)."""

from a2a.types import AgentSkill


def _skill(skill_id: str, name: str, description: str, example: str) -> AgentSkill:
    return AgentSkill(
        id=skill_id,
        name=name,
        description=description,
        tags=["ezstore", "quotation"],
        examples=[example],
        input_modes=["text/plain"],
        output_modes=["text/plain"],
    )


QUOTATION_SKILLS: list[AgentSkill] = [
    _skill("get_quotation", "查詢報價單", "依報價單編號回覆報價單詳細資訊、品項與系統連結。",
           "我要查詢報價單，報價單編號：QT-20260330-001"),
    _skill("list_customer_quotations", "查詢客戶的報價單清單", "依客戶名稱列出該客戶所有報價單。",
           "我要查詢客戶的報價單清單，客戶名稱：史塔克工業"),
    _skill("duplicate_quotation", "複製報價單", "複製一張新的草稿報價單，原單不變。",
           "我要複製報價單，報價單編號：QT-20260330-001"),
    _skill("update_pricing_factor", "修改報價因子", "先複製再修改副本的報價因子，原始報價單不會被更動。",
           "我要修改報價單報價因子，報價單編號：QT-20260330-001，報價因子改為 1.5"),
    _skill("adjust_total_price", "修改報價單總價", "先複製，再以二分法調整副本的報價因子逼近目標總價。",
           "我要修改報價單總價，報價單編號：QT-20260330-001，總價改為 8000"),
    _skill("convert_to_order", "報價單轉訂單", "依報價單建立訂單並關聯原單，原始報價單不會被更動。",
           "我要將報價單轉訂單，報價單編號：QT-20260330-001"),
]
