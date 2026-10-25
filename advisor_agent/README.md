# Agent 2 — EZStore Sales Advisor（業務顧問 Agent）

A second agent built on the same EZStore system. Where the quotation agent *executes* quotation operations, the
sales advisor *checks them against company policy* and explains what to do.

```
Salesperson ──▶ Sales Advisor (ADK LlmAgent + tools, :8502 dev UI)
                   │  okf_list / okf_search / okf_read ──▶ knowledge/ezstore-okf   (OKF v0.2 bundle)
                   │  get_customer_profile ─────────────▶ backend REST (read-only: tier, credit score)
                   │  review_quotation ─┐
                   │  ask_quotation_agent ┴─ A2A JSON-RPC ─▶ quotation_agent (/a2a/quotation_agent) ─▶ MCP ─▶ backend
```

| | Quotation agent (Agent 1) | Sales advisor (Agent 2) |
|---|---|---|
| ADK pattern | Graph `Workflow`, LLM only classifies | `LlmAgent` that plans and calls tools |
| Knowledge | none (tools only) | OKF bundle: policies, entities, metrics, processes, lessons learned |
| Data access | MCP Server (6 tools) | A2A to the quotation agent + read-only customer lookup |
| Writes data | yes (copies, orders) | only through A2A, only after the user confirms (`confirmed=True`, checked in code) |

## What you can ask

| Request | What happens |
|---|---|
| VIP 客戶的報價因子最低可以到多少？ | `okf_search` → `okf_read policies/pricing-factor-by-tier` → answer + 「依據：…」 |
| 利潤率低於多少要主管核准？誰核准？ | reads `policies/minimum-profit-rate`, `policies/approval-matrix` |
| 幫我檢查 QT-20260115-001 是否符合報價政策 | `review_quotation`: A2A get_quotation → policy values from OKF frontmatter → verdict `needs_approval` (利潤率 28.4% < 30%), recommends factor 0.77 |
| 好，幫我套用建議的報價因子 | asks for confirmation → `ask_quotation_agent(..., confirmed=True)` → the quotation agent creates a copy with factor 0.77 |
| 無臉男金融服務可以直接轉訂單嗎？ | `get_customer_profile` → credit 35 → 需總經理核准 (policies/customer-credit-policy) |
| 修改總價時為什麼有時候到不了目標？ | `lessons-learned/ll-001-bisect-total-price` |

Policy thresholds are **custom frontmatter keys** in the OKF concepts (`policy_tiers`, `min_profit_rate`,
`approval_profit_rate`, `credit_rules`), so the same file is readable by people and executed by
`sales_advisor/policy.py`. Change the policy in the markdown, restart, and the review changes.

## Run

With Docker (recommended — A2A goes container to container):

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml -f docker-compose.advisor.yml up -d --build
open "http://localhost:8502/dev-ui/?app=sales_advisor"
```

Locally:

```bash
cd agent && APP_URL=http://localhost:8081 uv run uvicorn quotation_agent.fast_api_app:app --port 8081   # quotation agent + A2A
cd advisor_agent && cp .env.example .env && uv sync --group dev
uv run uvicorn sales_advisor.fast_api_app:app --port 8502      # dev UI: http://localhost:8502/dev-ui/?app=sales_advisor
```

## Tests and OKF tools

```bash
cd advisor_agent
uv run pytest tests -q                         # OKF conformance, policy review, tools with A2A stubbed, tool loop
uv run python scripts/okf_validate.py          # OKF v0.2 conformance report
uv run python scripts/okf_graph.py -o okf-graph.html && open okf-graph.html   # interactive knowledge graph
```
