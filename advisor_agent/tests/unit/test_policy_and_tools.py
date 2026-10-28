"""Policy review + tools with the A2A call and backend stubbed (no network, no API key)."""

import pytest

from sales_advisor import a2a_client, backend, tools
from sales_advisor.okf import Bundle
from sales_advisor.policy import parse_quotation_text, review

QT_TEXT = """報價單編號: QT-20260115-001
客戶: 史塔克工業股份有限公司
客戶等級: vip
報價因子: 0.75
總價: 253500
利潤: 72000 (利潤率: 0.2840)
狀態: published
備註: VIP年度辦公設備採購案
品項:
  1. 商用雷射印表機 LJ-5200 — 單價: 16500, 數量: 5, 小計: 82500
系統連結: http://localhost:3000/quotations/1"""


def test_parse_quotation_text():
    q = parse_quotation_text(QT_TEXT)
    assert q["quotation_number"] == "QT-20260115-001"
    assert q["customer_level"] == "vip" and q["pricing_factor"] == 0.75 and q["profit_rate"] == 0.284
    assert q["link"] == "http://localhost:3000/quotations/1" and q["status"] == "published"


@pytest.mark.parametrize(
    "level,factor,rate,credit,verdict,rec",
    [
        ("new", 0.95, 0.3846, 50, "compliant", None),
        ("vip", 0.75, 0.284, 95, "needs_approval", 0.77),
        ("new", 1.5, 0.61, 50, "warning", 1.10),
        ("standard", 0.70, 0.10, 70, "violation", 0.90),
        ("new", 1.0, 0.40, 35, "needs_approval", None),
    ],
)
def test_review(level, factor, rate, credit, verdict, rec):
    q = {"quotation_number": "QT-X", "customer_level": level, "pricing_factor": factor, "total_price": 1000,
         "profit_rate": rate, "status": "draft"}
    r = review(q, Bundle().policy(), credit)
    assert r["verdict"] == verdict
    assert (r["recommendation"] or {}).get("new_pricing_factor") == rec
    assert all(s.startswith(("policies/", "processes/")) for s in r["sources"])


@pytest.fixture
def stub_a2a(monkeypatch):
    sent = []

    async def fake_ask(request, url=None, timeout=180.0):
        sent.append(request)
        if "QT-20990101-001" in request:
            return a2a_client.A2AReply(True, "找不到報價單編號 QT-20990101-001。", "t0", "TASK_STATE_COMPLETED")
        return a2a_client.A2AReply(True, QT_TEXT, "t1", "TASK_STATE_COMPLETED")

    async def fake_customer(name):
        return {"name": "史塔克工業股份有限公司", "level": "vip", "credit_score": 95}

    monkeypatch.setattr(a2a_client, "ask", fake_ask)
    monkeypatch.setattr(backend, "find_customer", fake_customer)
    return sent


@pytest.mark.asyncio
async def test_review_quotation_tool_uses_a2a(stub_a2a):
    r = await tools.review_quotation("請幫我看 qt-20260115-001")
    assert stub_a2a == ["我要查詢報價單，報價單編號：QT-20260115-001"]
    assert r["verdict"] == "needs_approval" and r["recommendation"]["new_pricing_factor"] == 0.77
    assert r["via"]["a2a_agent"] == "quotation_agent"


@pytest.mark.asyncio
async def test_review_quotation_not_found(stub_a2a):
    r = await tools.review_quotation("QT-20990101-001")
    assert "找不到" in r["error"]


@pytest.mark.asyncio
async def test_modifying_request_needs_confirmation(stub_a2a):
    r = await tools.ask_quotation_agent("我要將報價單轉訂單，報價單編號：QT-20260115-001")
    assert r["status"] == "needs_confirmation" and stub_a2a == []
    r = await tools.ask_quotation_agent("我要將報價單轉訂單，報價單編號：QT-20260115-001", confirmed=True)
    assert r["ok"] and len(stub_a2a) == 1


@pytest.mark.asyncio
async def test_read_only_request_goes_straight_through(stub_a2a):
    r = await tools.ask_quotation_agent("我要查詢客戶的報價單清單，客戶名稱：史塔克工業")
    assert r["ok"] and stub_a2a


@pytest.mark.asyncio
async def test_customer_profile(stub_a2a):
    r = await tools.get_customer_profile("史塔克工業")
    assert r["credit_score"] == 95 and r["order_condition"] == "可直接轉訂單"


def test_okf_tools():
    assert "policies/" in tools.okf_list("")["index"]
    assert tools.okf_search("核准")["results"]
    c = tools.okf_read("policies/minimum-profit-rate")
    assert c["frontmatter"]["min_profit_rate"] == 0.25 and "policies/approval-matrix" in c["links_to"]
    assert "error" in tools.okf_read("policies/does-not-exist")


def test_agent_wiring():
    import sales_advisor

    assert sales_advisor.app.name == "sales_advisor"
    assert "{" not in sales_advisor.root_agent.instruction
    assert len(sales_advisor.root_agent.tools) == 6
