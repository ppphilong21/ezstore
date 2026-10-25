# EZStore

> A lightweight B2B quotation and order management system.

[中文版](README.zh-TW.md)

---

## Part 1 — For Developers

### Overview

EZStore provides four core modules for managing the B2B sales pipeline:

| Module | Description |
|--------|-------------|
| **Customer Management** | CRUD for companies — name, tax ID, contacts, address, customer level (VIP / Standard / New), credit score |
| **Product Management** | CRUD for products — product number, name, description, cost, list price, inventory, supplier |
| **Quotation Management** | Create, edit, publish, and delete quotations. Pricing is computed from a *pricing factor* applied to list prices. Published quotations become immutable. |
| **Order Management** | CRUD for orders — optionally linked to a published quotation |
| **AI Agent** | Natural language quotation assistant — query, duplicate, adjust pricing factor/total price, convert to order. Google ADK 2.x graph Workflow + Gemini 3.8 Flash + MCP Server, scaffolded with google-agents-cli. |

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Go 1.25 · Gin · GORM · Swagger (swaggo) · Testify |
| Frontend | React 19 · TypeScript · Tailwind CSS 4 · Vite 8 · TanStack React Query · React Hook Form · React Router |
| Database | PostgreSQL 16 |
| AI Agent | Python 3.12 · Google ADK 2.10+ (graph Workflow API) · google-agents-cli 1.7 · Gemini 3.8 Flash · MCP Python SDK 2.x (Streamable HTTP) · uv |
| Build & Deploy | Docker · Docker Compose · Bun (frontend) · Nginx (frontend serving & API proxy) |

### Project Structure

```
ezstore/
├── docker-compose.yml          # Orchestrates all services
├── scripts/
│   └── seed-test-data.sql      # Idempotent test dataset (TRUNCATE + INSERT)
├── .env.example                # GEMINI_API_KEY and agent settings (copy to .env)
├── agent/                      # ★ LAB deliverable: ADK 2.x graph Workflow quotation agent (built from agent-spec-prompt.md)
│   ├── quotation_agent/        #   agent.py (Workflow), intent.py (Intent + code rules), mcp_client.py, messages.py, fast_api_app.py (+A2A)
│   ├── tests/                  #   unit/, integration/, eval/ (datasets + eval_config.yaml)
│   └── scripts/call_mcp.py     #   call one MCP tool directly (stage 4.1)
├── mcp_server/
│   ├── Dockerfile
│   ├── pyproject.toml           # mcp>=2.2, httpx (+ uv.lock)
│   └── server.py                # MCPServer (Streamable HTTP) with 6 quotation tools
├── backend/
│   ├── Dockerfile
│   ├── main.go                 # Entry point — Gin + GORM + Swagger init
│   ├── config/config.go        # Database connection (env vars)
│   ├── models/                 # GORM models (Customer, Product, Quotation, Order + items)
│   ├── repositories/           # Data access layer (CRUD, pagination, search)
│   ├── services/               # Business logic (pricing engine, validation)
│   ├── handlers/               # Gin HTTP handlers + Swagger annotations
│   ├── middleware/              # CORS, error handling
│   ├── routes/routes.go        # Route registration
│   └── docs/                   # Auto-generated Swagger files
└── frontend/
    ├── Dockerfile
    ├── nginx.conf              # Reverse proxy /api → backend, SPA fallback
    ├── vite.config.ts
    ├── src/
    │   ├── api/                # Axios API clients
    │   ├── pages/              # Route-level page components
    │   ├── components/         # Shared UI (DataTable, Pagination, StatusBadge, etc.)
    │   ├── types/index.ts      # TypeScript type definitions
    │   ├── App.tsx             # Router + QueryClientProvider
    │   └── main.tsx            # React entry point
    └── e2e/                    # Playwright E2E tests (planned)
```

### Prerequisites

The following tools must be installed before developing or running EZStore:

| Tool | Version | Purpose |
|------|---------|---------|
| **Docker** | ≥ 24.0 | Container runtime for all services |
| **Docker Compose** | ≥ 2.20 (included with Docker Desktop) | Multi-container orchestration |
| **Go** | ≥ 1.24 | Backend compilation and development |
| **Bun** | ≥ 1.0 | Frontend package manager and build tool |
| **swag** (Go CLI) | latest | Swagger documentation generation |

> **Docker-only mode:** If you only need to *run* EZStore (not develop), Docker and Docker Compose are sufficient. Go, Bun, and swag are only needed for local development.

#### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Docker Desktop (includes Docker Compose)
brew install --cask docker

# Go
brew install go

# Bun
brew install oven-sh/bun/bun

# swag (Swagger CLI) — requires Go to be installed first
go install github.com/swaggo/swag/cmd/swag@latest
```

After installing Docker Desktop, launch it from Applications and ensure it is running (whale icon in the menu bar).

#### Windows

```powershell
# Install winget (comes with Windows 11; for Windows 10 install "App Installer" from Microsoft Store)

# Docker Desktop (includes Docker Compose)
winget install Docker.DockerDesktop

# Go
winget install GoLang.Go

# Bun
powershell -c "irm bun.sh/install.ps1 | iex"

# swag (Swagger CLI) — requires Go to be installed first; restart terminal after Go install
go install github.com/swaggo/swag/cmd/swag@latest
```

After installing Docker Desktop, launch it and ensure **WSL 2 backend** is enabled (Settings → General → Use the WSL 2 based engine). You may need to restart your computer.

> **Note for Windows users:** All shell commands in this README use Unix-style syntax. Use **Git Bash**, **WSL 2**, or **PowerShell** to run them. If using PowerShell, replace `export VAR=value` with `$env:VAR="value"`.

#### Verify Installation

```bash
docker --version          # Docker version 24.x+
docker compose version    # Docker Compose version v2.x+
go version                # go1.24+
bun --version             # 1.x+
swag --version            # swag version v1.x+
```

### Quick Start (Docker Compose)

**API key (required for the AI Agent, everything else runs without it):**

```bash
cp .env.example .env      # then fill in GEMINI_API_KEY from https://aistudio.google.com/apikey
```

**Option A — Use pre-built images from GHCR (default, no build required):**

```bash
docker compose up -d
```

**Option B — Build from local source code:**

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

**Load test data:**

```bash
docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8080/api/v1 |
| Swagger UI | http://localhost:8080/swagger/index.html |
| Health Check | http://localhost:8080/health |

**Run E2E tests (verify the deployment is working):**

```bash
docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql
docker compose run --rm e2e
```

### Development Mode

```bash
# 1. Start PostgreSQL
docker compose up db -d

# 2. Start backend (hot reload with go run)
cd backend
export DB_HOST=localhost DB_PORT=5432 DB_USER=ezstore DB_PASSWORD=ezstore DB_NAME=ezstore
go run .

# 3. Start frontend (Vite dev server with API proxy)
cd frontend
bun install
bun run dev          # http://localhost:5173
```

### API Documentation

All endpoints are documented with Swagger annotations. Once the backend is running, visit:

```
http://localhost:8080/swagger/index.html
```

### Testing

**Backend unit tests:**

```bash
cd backend
go test ./... -v -cover
```

**Load test dataset** (idempotent — safe to run repeatedly):

```bash
docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql
```

The seed data includes: 15 customers (5 VIP + 6 Standard + 4 New), 20 products, 12 quotations (8 published + 4 draft), 10 orders (3 pending + 3 confirmed + 2 completed + 2 cancelled).

**Regenerate Swagger docs:**

```bash
cd backend
$(go env GOPATH)/bin/swag init -g main.go --parseDependency --parseInternal
```

### Core Business Logic

**Pricing Factor** — Determines how list prices are adjusted per customer level:

| Customer Level | Default Factor | Effect |
|---------------|----------------|--------|
| VIP | 0.80 | 20% discount |
| Standard | 0.90 | 10% discount |
| New | 1.00 | Full price |

The factor can be manually adjusted per quotation.

**Computation Formulas:**

```
unit_price   = list_price × pricing_factor
subtotal     = unit_price × quantity
total_price  = Σ(subtotal)
profit       = Σ((unit_price − cost) × quantity)
profit_rate  = profit ÷ total_price
```

**Publish Immutability** — Once a quotation is published:
- It cannot be edited (HTTP 403)
- It cannot be deleted (HTTP 403)
- It cannot be published again (HTTP 400)

### AI Agent

EZStore includes a natural-language quotation assistant built with Google ADK 2.x (`agent/`, scaffolded with google-agents-cli). The agent is a **graph Workflow**: only one node calls the LLM (intent classification); tool selection, arguments, clarification and refusal are all deterministic program logic.

**Architecture:**

```
User → React Chat UI → nginx /agent-api → Agent (ADK FastAPI, agent:8080) → MCP Server (mcp-server:8000) → Backend REST API
                                               │   │                            Streamable HTTP
                                    Gemini 3.8 Flash  └─ /a2a/quotation_agent   (mcp Python SDK 2.x)
                                  (AI Studio / Vertex)   A2A JSON-RPC for other agents
```

**Workflow graph** (`agent/quotation_agent/agent.py`):

```
START → load_context ─(classify)→ classify_intent (LLM → Intent) → route ─┬→ get_quotation ────────────┐
            │                                                              ├→ list_customer_quotations ─┤
            │                                                              ├→ duplicate_quotation ──────┤
            │                                                              ├→ update_pricing_factor ────┤  each calls
            │                                                              ├→ adjust_total_price ───────┤  ONE MCP tool
            │                                                              ├→ convert_to_order ─────────┼→ respond
            │                                                              ├→ clarify   (ask, keep state.pending_intent)
            │                                                              ├→ off_topic (fixed refusal, decided by code)
            │                                                              └─(direct)  invalid value / model error
            └─(direct) no model credentials ─────────────────────────────────────────────────────→ respond
```

| Node | Kind | What it does |
|---|---|---|
| `load_context` | code | Current message + last 6 messages + `state.pending_intent` (rebuilt from history when state is empty, e.g. in eval). Short-circuits to `respond` when no credentials are configured. |
| `classify_intent` | **LLM** (`LlmAgent`, `output_schema=Intent`, temperature 0) | Natural language → `{intent, quotation_number, customer_name, new_pricing_factor, target_total_price}` |
| `route` | code | Guardrail regexes (prompt injection, customer/product/order CRUD, delete/publish quotation) → refuse; merges LLM fields with regex extraction (QT numbers, factors, totals, Chinese numerals) and pending args; missing field → `clarify`; invalid value (factor ≤ 0, total ≤ 0) → reply without calling any tool |
| 6 action nodes | code | Each calls one MCP tool via `McpToolset.get_tools() → tool.run_async()` and records a function_call/function_response pair in the trace |
| `clarify` / `off_topic` | code | Fixed replies: clarification starts with 「請提供」, refusal contains 「只能協助」 |
| `respond` | code | The only node whose text is shown in the Chat UI (`nodeInfo.path` ends with `/respond@N`); strips any Markdown link to plain text |

**Capabilities:**

| Operation | Example | Description |
|-----------|---------|-------------|
| Query quotation | 我要查詢報價單，報價單編號：QT-20260330-001 | Details and items by quotation number |
| List customer quotations | 我要查詢客戶的報價單清單，客戶名稱：史塔克工業 | All quotations for a customer |
| Duplicate quotation | 我要複製報價單，報價單編號：QT-20260330-001 | New draft copy |
| Modify pricing factor | …報價因子改為 1.5 | Copy first, then change the factor on the copy |
| Modify total price | …總價改為 8000 | Copy first, then bisect the factor (≤ 20 iterations) |
| Convert to order | 我要將報價單轉訂單，報價單編號：QT-20260330-001 | New order linked via `quotation_id`; quotation untouched |

**Key design:** copy-on-write (original never changes, the reply says 「未修改」) · plain-text links only · off-topic refused by code · missing data → clarification, next message continues · runs without an API key (chat replies with a clear configuration error).

**Environment variables:**

| Variable | Where | Default | Purpose |
|---|---|---|---|
| `GEMINI_API_KEY` | root `.env` (Compose) / `agent/.env` (local) | — | Google AI Studio key |
| `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` | same | `false`, —, `global` | Vertex AI instead of AI Studio (`gcloud auth application-default login`) |
| `AGENT_MODEL` | same | `gemini-3.8-flash` | Model for `classify_intent` and the eval judge |
| `MCP_URL` | Compose: fixed / local: `agent/.env` | `http://mcp-server:8000/mcp` (Compose), `http://localhost:8010/mcp` (local) | MCP Server endpoint |
| `APP_URL` | Compose | `http://agent:8080` | URL advertised in the A2A agent card |
| `ALLOW_ORIGINS` | root `.env` | `http://localhost:3000` | CORS for the ADK API |

**Run with Docker (builds your local `agent/`):**

```bash
cp .env.example .env                     # put GEMINI_API_KEY=...
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql
docker compose ps                        # db, backend, mcp-server, agent, frontend running/healthy
open http://localhost:3000/agent
```

**Local development & tests:**

```bash
docker compose up -d db backend mcp-server            # MCP exposed on localhost:8010
cd agent && cp .env.example .env                      # GEMINI_API_KEY, MCP_URL=http://localhost:8010/mcp
uv sync --group dev --extra eval
uv run python scripts/call_mcp.py get_quotation quotation_number=QT-20260330-001   # stage 4.1: call MCP directly
agents-cli playground                                 # ADK web UI, app quotation_agent
agents-cli run "我要查詢報價單，報價單編號：QT-20260330-001"

uv run pytest tests/unit tests/integration -q         # no API key needed; integration uses the MCP server if reachable
agents-cli eval run --dataset tests/eval/datasets/quotation-guardrails.json --config tests/eval/eval_config.yaml
docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql   # reseed before the actions set
agents-cli eval run --dataset tests/eval/datasets/quotation-actions.json --config tests/eval/eval_config.yaml
cd .. && python3 scripts/grading/grade_agent.py --suite scripts/grading/student-suite.json   # 0–100 self-grading
```

Eval metrics (`agent/tests/eval/eval_config.yaml`): `custom_response_quality` (LLM judge 1–5), `link_present` (code 0/1), `refusal_or_action` (LLM judge 0/1), `agent_turn_count`. Design notes and how to add an operation: [agent/README.md](agent/README.md). Trustworthiness labs: [eval-lab-quick.md](eval-lab-quick.md) (25 min) and [eval-lab.md](eval-lab.md) (60–90 min).

**A2A:** the same service exposes the agent over the Agent2Agent protocol — card at `http://agent:8080/a2a/quotation_agent/.well-known/agent-card.json` (one skill per operation), JSON-RPC at `/a2a/quotation_agent`.

### Agent 2: Sales Advisor (A2A + OKF)

`advisor_agent/` is a second agent on the same system: an ADK `LlmAgent` that checks quotations against company policy.
It reads the **OKF knowledge bundle** in `knowledge/ezstore-okf/` (policies, entities, metrics, processes, lessons learned)
and delegates every quotation operation to the quotation agent over **A2A** (`http://agent:8080/a2a/quotation_agent`).

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml -f docker-compose.advisor.yml up -d --build
open "http://localhost:8502/dev-ui/?app=sales_advisor"
```

Details: [advisor_agent/README.md](advisor_agent/README.md) · [knowledge/README.md](knowledge/README.md).


### License

This project is licensed under the [MIT License](LICENSE).

---

## Part 2 — For AI Coding Agents

> This section is written for AI coding assistants (Claude Code, Gemini CLI, GitHub Copilot, Antigravity, Cursor, Aider, etc.). It provides structured, machine-friendly context to help you work effectively in this codebase.

### Project Identity

- **Name:** EZStore
- **Purpose:** B2B quotation and order management system
- **Language:** Go (backend), TypeScript/React (frontend), Python 3.12 (agent + MCP server)
- **Database:** PostgreSQL 16
- **Deployment:** Docker Compose (5 services: db, backend, frontend, agent, mcp-server)

### Architecture Pattern

The backend follows a **3-layer architecture**:

```
HTTP Request → Handler (Gin) → Service (business logic) → Repository (GORM/DB)
```

- **Handlers** parse HTTP input, call services, return JSON. Include Swagger annotations.
- **Services** contain validation and business logic. Never access `*gin.Context`.
- **Repositories** wrap GORM queries. Return models or errors, never HTTP concepts.

### Key File Paths

| Concern | Path |
|---------|------|
| Backend entry point | `backend/main.go` |
| Database config | `backend/config/config.go` |
| All models | `backend/models/*.go` |
| All repositories | `backend/repositories/*.go` |
| All services | `backend/services/*.go` |
| All handlers | `backend/handlers/*.go` |
| Route registration | `backend/routes/routes.go` |
| CORS middleware | `backend/middleware/cors.go` |
| Error response helper | `backend/middleware/error_handler.go` |
| Pricing factor defaults | `backend/models/customer.go` → `DefaultPricingFactor()` |
| Quotation calculation | `backend/services/quotation_service.go` → `computeTotals()`, `buildItems()` |
| Frontend entry | `frontend/src/main.tsx` |
| React router | `frontend/src/App.tsx` |
| TypeScript types | `frontend/src/types/index.ts` |
| API clients | `frontend/src/api/*.ts` |
| Page components | `frontend/src/pages/*.tsx` |
| Shared components | `frontend/src/components/shared/*.tsx` |
| Agent workflow graph | `agent/quotation_agent/agent.py` (`Workflow`, `Intent`, node functions) |
| Agent intent schema + code rules | `agent/quotation_agent/intent.py` |
| Agent fixed replies | `agent/quotation_agent/messages.py` |
| Agent MCP client | `agent/quotation_agent/mcp_client.py` |
| Agent FastAPI app | `agent/quotation_agent/fast_api_app.py` |
| Agent eval | `agent/tests/eval/eval_config.yaml`, `agent/tests/eval/datasets/*.json` |
| MCP Server (6 tools, mcp 2.x `MCPServer`) | `mcp_server/server.py` |
| Agent Chat UI | `frontend/src/pages/AgentChatPage.tsx` |
| Agent API client | `frontend/src/api/agentApi.ts` |
| Docker orchestration | `docker-compose.yml` |
| Test dataset | `scripts/seed-test-data.sql` |

### Database Schema Summary

6 tables. All main entities use GORM soft-delete (`deleted_at`). Item tables use hard delete.

```
customers         → id, name, tax_id (unique, 8 digits), contact_name, contact_phone,
                    contact_email, address, level (vip|standard|new), credit_score (0-100)

products          → id, product_number (unique), name, description, cost, list_price,
                    inventory, supplier

quotations        → id, quotation_number (unique, auto: QT-YYYYMMDD-NNN),
                    customer_id (FK), customer_level (snapshot), pricing_factor,
                    total_price, profit_amount, profit_rate,
                    status (draft|published), notes

quotation_items   → id, quotation_id (FK, CASCADE), product_id (FK),
                    product_name (snapshot), product_cost (snapshot), list_price (snapshot),
                    unit_price, quantity, subtotal

orders            → id, order_number (unique, auto: ORD-YYYYMMDD-NNN),
                    customer_id (FK), quotation_id (FK, nullable),
                    total_price, status (pending|confirmed|completed|cancelled), notes

order_items       → id, order_id (FK, CASCADE), product_id (FK),
                    product_name (snapshot), unit_price, quantity, subtotal
```

**Important:** Quotation/order items store *snapshots* of product data (name, cost, list_price) at creation time. This ensures historical accuracy if product data changes later.

### REST API Endpoints

Base path: `/api/v1`

```
GET    /health                        → { status: "ok" }
GET    /api/v1/pricing-factor/:level  → { level, pricing_factor }

# Customers
GET    /api/v1/customers              → paginated list (?page, ?page_size, ?search)
GET    /api/v1/customers/:id
POST   /api/v1/customers
PUT    /api/v1/customers/:id
DELETE /api/v1/customers/:id          → soft delete

# Products
GET    /api/v1/products               → paginated list (?page, ?page_size, ?search)
GET    /api/v1/products/:id
POST   /api/v1/products
PUT    /api/v1/products/:id
DELETE /api/v1/products/:id           → soft delete

# Quotations
GET    /api/v1/quotations             → paginated list (?page, ?page_size, ?status, ?customer_id, ?quotation_number)
GET    /api/v1/quotations/:id         → includes items[] and customer
POST   /api/v1/quotations             → body: { customer_id, pricing_factor, notes, items: [{product_id, quantity}] }
PUT    /api/v1/quotations/:id         → draft only; same body as POST
POST   /api/v1/quotations/:id/publish → sets status to published (irreversible)
DELETE /api/v1/quotations/:id         → draft only; soft delete

# Orders
GET    /api/v1/orders                 → paginated list (?page, ?page_size, ?status, ?customer_id)
GET    /api/v1/orders/:id             → includes items[] and customer
POST   /api/v1/orders                 → body: { customer_id, quotation_id?, notes, items: [{product_id, unit_price, quantity}] }
PUT    /api/v1/orders/:id
DELETE /api/v1/orders/:id             → soft delete
```

### Pricing Computation Rules

When a quotation is created or updated, the backend:

1. Fetches the customer → snapshots `customer_level`
2. For each item: fetches the product → snapshots `product_name`, `product_cost`, `list_price`
3. Computes `unit_price = list_price × pricing_factor`
4. Computes `subtotal = unit_price × quantity`
5. Computes `total_price = Σ(subtotal)`
6. Computes `profit_amount = Σ((unit_price − cost) × quantity)`
7. Computes `profit_rate = profit_amount ÷ total_price` (guarded: returns 0 if total is 0)

Default pricing factors: VIP → 0.80, Standard → 0.90, New → 1.00 (defined in `backend/models/customer.go`).

### Business Rules and Constraints

- **Tax ID**: must be exactly 8 digits (`^\d{8}$`)
- **Customer level**: must be one of `vip`, `standard`, `new`
- **Credit score**: integer 0–100
- **Product cost and list_price**: must be ≥ 0 (Decimal, never float)
- **Quantity**: must be > 0
- **Published quotation**: cannot be edited, deleted, or re-published
- **Quotation/Order numbers**: auto-generated as `QT-YYYYMMDD-NNN` / `ORD-YYYYMMDD-NNN`
- **Soft delete**: customers, products, quotations, orders use `deleted_at`
- **Hard delete**: quotation_items and order_items are physically deleted on parent update

### Common Developer Commands

```bash
# Full stack (Docker)
docker compose up --build -d
docker compose down -v                    # stop and remove volumes
docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql

# Backend
cd backend
go run .                                  # start API server (port 8080)
go test ./... -v -cover                   # run all tests
go build -o ezstore-api .                 # build binary
$(go env GOPATH)/bin/swag init -g main.go --parseDependency --parseInternal  # regenerate swagger

# Frontend
cd frontend
bun install                               # install dependencies
bun run dev                               # dev server (port 5173, proxies /api to :8080)
bun run build                             # production build → dist/

# MCP Server
cd mcp_server
uv sync && BACKEND_URL=http://localhost:8080 MCP_PORT=8010 uv run python server.py

# Agent (reads agent/.env: GEMINI_API_KEY, MCP_URL, AGENT_MODEL)
cd agent
uv sync --group dev
agents-cli playground                     # local web UI
agents-cli run "我要查詢報價單，報價單編號：QT-20260330-001"
uv run pytest tests/unit tests/integration -q
agents-cli eval run                       # LLM-judged eval over tests/eval/datasets
```

### Common Modification Scenarios

**Adding a new field to an existing entity (e.g., adding `fax` to Customer):**
1. Add the field to the model in `backend/models/customer.go` (with GORM + JSON tags)
2. GORM AutoMigrate in `main.go` handles the schema change automatically
3. Update validation in `backend/services/customer_service.go` if needed
4. Update the handler's Swagger annotations in `backend/handlers/customer_handler.go`
5. Add the field to `frontend/src/types/index.ts`
6. Update the form in `frontend/src/pages/CustomerFormPage.tsx`
7. Update the table columns in `frontend/src/pages/CustomerListPage.tsx`
8. Regenerate Swagger docs

**Adding a new API endpoint:**
1. Create or update handler function in `backend/handlers/` with Swagger annotations
2. Add business logic in `backend/services/`
3. Add data access in `backend/repositories/` if needed
4. Register the route in `backend/routes/routes.go`
5. Add frontend API function in `frontend/src/api/`
6. Regenerate Swagger docs

**Adding a new entity:**
Follow the existing pattern: model → repository → service → handler → route. Each entity has its own file in each layer. Reference `customer` as the simplest complete example.
