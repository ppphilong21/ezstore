"""Deterministic policy review of one quotation against the OKF policy concepts."""

from __future__ import annotations

import math
import re
from typing import Any

_FIELDS = {
    "quotation_number": r"報價單編號:\s*(\S+)",
    "customer": r"客戶:\s*(.+)",
    "customer_level": r"客戶等級:\s*(\w+)",
    "pricing_factor": r"報價因子:\s*([\d.]+)",
    "total_price": r"總價:\s*([\d.]+)",
    "profit_amount": r"利潤:\s*([\d.\-]+)",
    "profit_rate": r"利潤率:\s*([\d.\-]+)",
    "status": r"狀態:\s*(\w+)",
    "link": r"系統連結:\s*(http\S+)",
}
_NUMERIC = {"pricing_factor", "total_price", "profit_amount", "profit_rate"}


def parse_quotation_text(text: str) -> dict[str, Any]:
    """Parse the quotation agent's get_quotation reply (MCP text format) into fields."""
    out: dict[str, Any] = {}
    for key, pattern in _FIELDS.items():
        m = re.search(pattern, text)
        if m:
            value = m.group(1).strip()
            out[key] = float(value) if key in _NUMERIC else value
    return out


def _ceil2(x: float) -> float:
    return math.ceil(round(x * 100, 6)) / 100


def credit_action(credit_score: int | None, rules: list[dict[str, Any]]) -> str | None:
    if credit_score is None:
        return None
    for rule in sorted(rules, key=lambda r: r["below"]):
        if credit_score < rule["below"]:
            return str(rule["action"])
    return None


def review(q: dict[str, Any], policy: dict[str, Any], credit_score: int | None = None) -> dict[str, Any]:
    level = str(q.get("customer_level", "")).lower()
    f0 = float(q["pricing_factor"])
    r0 = float(q.get("profit_rate", 0))
    tier = policy["tiers"].get(level)
    r_min, r_appr = policy["min_profit_rate"], policy["approval_profit_rate"]
    checks: list[dict[str, Any]] = []
    approvals: list[str] = []
    rec: float | None = None

    # 1) pricing factor range
    if tier is None:
        checks.append({"rule": "policies/pricing-factor-by-tier", "result": "unknown",
                       "detail": f"知識庫沒有客戶等級 {level} 的報價因子區間"})
        lo, hi = 0.0, 99.0
    else:
        lo, hi = float(tier["min"]), float(tier["max"])
        if f0 < lo:
            checks.append({"rule": "policies/pricing-factor-by-tier", "result": "violation",
                           "detail": f"{level} 允許 {lo:.2f}–{hi:.2f}，目前 {f0:g} 低於下限，需業務主管核准"})
            approvals.append("業務主管（報價因子低於等級下限）")
            rec = lo
        elif f0 > hi:
            checks.append({"rule": "policies/pricing-factor-by-tier", "result": "warning",
                           "detail": f"{level} 允許 {lo:.2f}–{hi:.2f}，目前 {f0:g} 高於上限，有流失客戶的風險"})
            rec = hi
        else:
            checks.append({"rule": "policies/pricing-factor-by-tier", "result": "pass",
                           "detail": f"{level} 允許 {lo:.2f}–{hi:.2f}，目前 {f0:g}"})

    # 2) profit rate (recompute for the recommended factor if we already have one)
    def rate_at(f: float) -> float:
        return 1 - f0 * (1 - r0) / f if f > 0 else 0.0

    f_for_appr = _ceil2(f0 * (1 - r0) / (1 - r_appr))
    f_for_min = _ceil2(f0 * (1 - r0) / (1 - r_min))
    if r0 < r_min:
        checks.append({"rule": "policies/minimum-profit-rate", "result": "violation",
                       "detail": f"利潤率 {r0:.2%} 低於下限 {r_min:.0%}，不得送出（或需總經理特批）"})
        approvals.append("總經理（利潤率低於 25%）")
        target = f_for_appr if f_for_appr <= hi else f_for_min
        rec = max(rec or 0, min(target, hi))
    elif r0 < r_appr:
        checks.append({"rule": "policies/minimum-profit-rate", "result": "needs_approval",
                       "detail": f"利潤率 {r0:.2%} 介於 {r_min:.0%}–{r_appr:.0%}，需業務主管核准"})
        approvals.append("業務主管（利潤率低於 30%）")
        if f_for_appr <= hi:
            rec = max(rec or 0, f_for_appr)
    else:
        checks.append({"rule": "policies/minimum-profit-rate", "result": "pass",
                       "detail": f"利潤率 {r0:.2%} ≥ {r_appr:.0%}"})

    # 3) credit (affects order conversion only)
    action = credit_action(credit_score, policy.get("credit_rules", []))
    if credit_score is not None:
        checks.append({"rule": "policies/customer-credit-policy",
                       "result": "warning" if action else "pass",
                       "detail": f"信用分數 {credit_score}：" + (action or "可直接轉訂單")})
        if action and "總經理" in action:
            approvals.append("總經理（轉訂單：信用分數低於 40）")

    if q.get("status") == "published":
        checks.append({"rule": "processes/quotation-lifecycle", "result": "info",
                       "detail": "已發佈的報價單不可修改；任何調整都會先複製再改副本"})

    results = {c["result"] for c in checks}
    if "violation" in results:
        verdict = "violation"
    elif approvals:
        verdict = "needs_approval"
    elif "warning" in results:
        verdict = "warning"
    else:
        verdict = "compliant"
    recommendation = None
    if rec is not None and abs(rec - f0) > 1e-9:
        recommendation = {
            "new_pricing_factor": round(rec, 2),
            "expected_profit_rate": round(rate_at(rec), 4),
            "expected_total_price": round(float(q.get("total_price", 0)) * rec / f0, 2) if f0 else None,
            "why": "回到等級區間內並讓利潤率達到 30%（免核准）" if rec >= f_for_appr else "回到等級區間內",
        }
    return {
        "quotation": q,
        "verdict": verdict,
        "checks": checks,
        "approvals_needed": approvals,
        "recommendation": recommendation,
        "sources": sorted({c["rule"] for c in checks}),
    }
