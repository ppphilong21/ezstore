"""Check the EZStore OKF bundle against OKF v0.2 conformance rules and print a summary.

    uv run python scripts/okf_validate.py [../knowledge/ezstore-okf]
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sales_advisor.okf import Bundle, default_bundle_path  # noqa: E402


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else default_bundle_path()
    b = Bundle(root)
    problems = b.validate()
    by_type = collections.Counter(c.type for c in b.concepts.values())
    edges = sum(len(c.links) for c in b.concepts.values())
    print(f"OKF bundle: {root}")
    print(f"  concepts: {len(b.concepts)}   links: {edges}   types: {dict(by_type)}")
    for cid, link in b.broken_links():
        print(f"  ! broken link (allowed by spec): {cid} -> {link}")
    policy = b.policy()
    print(f"  machine-readable policy: tiers={list(policy['tiers'])} min_profit_rate={policy['min_profit_rate']} "
          f"approval_profit_rate={policy['approval_profit_rate']} credit_rules={len(policy['credit_rules'])}")
    if problems:
        print("NOT conformant with OKF v0.2:")
        for p in problems:
            print("  -", p)
        return 1
    print("Conformant with OKF v0.2 ✔  (every concept has frontmatter with a non-empty type; index.md / log.md well-formed)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
