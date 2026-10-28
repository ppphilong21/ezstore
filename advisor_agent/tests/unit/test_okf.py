"""The EZStore bundle must stay OKF v0.2 conformant and machine-readable."""

from pathlib import Path

from sales_advisor.okf import Bundle, resolve_link, split_frontmatter


def test_bundle_is_conformant():
    b = Bundle()
    assert b.validate() == []
    assert b.broken_links() == []
    assert len(b.concepts) >= 20


def test_every_concept_has_type_title_description():
    for c in Bundle().concepts.values():
        assert c.type and c.meta.get("title") and c.description, c.id


def test_policy_values_match_backend_defaults():
    p = Bundle().policy()
    assert {k: v["default"] for k, v in p["tiers"].items()} == {"vip": 0.8, "standard": 0.9, "new": 1.0}
    assert p["min_profit_rate"] == 0.25 and p["approval_profit_rate"] == 0.30
    assert [r["below"] for r in p["credit_rules"]] == [40, 50]


def test_search_finds_relevant_concepts():
    b = Bundle()
    assert b.search("利潤率", 1)[0]["id"] == "policies/minimum-profit-rate"
    assert b.search("VIP 報價因子", 1)[0]["id"] == "policies/pricing-factor-by-tier"
    assert "lessons-learned/ll-001-bisect-total-price" in [r["id"] for r in b.search("二分法", 3)]


def test_index_and_links():
    b = Bundle()
    assert "policies/" in b.index("")
    assert "利潤率下限" in b.index("policies")
    assert "policies/approval-matrix" in b.get("policies/minimum-profit-rate").links
    assert "policies/minimum-profit-rate" in b.backlinks("metrics/profit-rate")


def test_validator_catches_problems(tmp_path: Path):
    (tmp_path / "a.md").write_text("no frontmatter", encoding="utf-8")
    (tmp_path / "b.md").write_text("---\ntitle: x\n---\nbody", encoding="utf-8")
    (tmp_path / "log.md").write_text("# Log\n\n## 2026-01-01\n* a\n\n## 2026-02-01\n* b\n", encoding="utf-8")
    problems = Bundle(tmp_path).validate()
    assert any("a.md" in p for p in problems)
    assert any("b.md" in p and "type" in p for p in problems)
    assert any("newest first" in p for p in problems)


def test_link_resolution():
    assert resolve_link("policies/x", "/metrics/profit-rate.md") == "metrics/profit-rate"
    assert resolve_link("policies/x", "./approval-matrix.md") == "policies/approval-matrix"
    assert resolve_link("policies/x", "../entities/order.md") == "entities/order"
    assert resolve_link("policies/x", "https://example.com/a.md") is None
    assert split_frontmatter("---\ntype: T\n---\nhi")[0] == {"type": "T"}
