# Coding Agent Guide

## Prerequisites

Install the CLI (one-time):
```bash
uv tool install google-agents-cli
```

---

## Development Phases

### Phase 1: Understand Requirements
Before writing any code, understand the project's requirements, constraints, and success criteria.

### Phase 2: Build and Implement
Implement agent logic in `quotation_agent/`. Use `agents-cli playground` for interactive testing. Iterate based on user feedback.

### Phase 3: The Evaluation Loop (Main Iteration Phase)
Start with 1-2 eval cases, run `agents-cli eval run`, iterate by making changes and rerunning it until satisfied. Expect 5-10+ iterations. Once you have a baseline, reach for `agents-cli eval compare` (regression diffs), `agents-cli eval analyze` (cluster failure modes), and `agents-cli eval optimize` (auto-tune prompts). See the **Evaluation Guide** for metrics, dataset schema, LLM-as-judge config, and common gotchas.

### Phase 4: Pre-Deployment Tests
Run `uv run pytest tests/unit tests/integration`. Fix issues until all tests pass.

### Phase 5: Deploy to Dev
**Requires explicit human approval.** Run `agents-cli deploy` only after user confirms. See the **Deployment Guide** for details.

### Phase 6: Production Deployment
Ask the user: Option A (simple single-project) or Option B (full CI/CD pipeline with `agents-cli infra cicd`).

## Development Commands

| Command | Purpose |
|---------|---------|
| `agents-cli playground` | Interactive local testing |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests |
| `agents-cli eval dataset synthesize` | Synthesize multi-turn eval scenarios for your agent |
| `agents-cli eval run` | Run the agent over the eval dataset and grade the traces |
| `agents-cli eval generate` / `agents-cli eval grade` | Decoupled form: produce traces, then grade them |
| `agents-cli eval compare` | Compare two grade-results files (regression check) |
| `agents-cli eval analyze` | Cluster failure modes from grade results |
| `agents-cli eval metric list` | List built-in metrics available in the SDK |
| `agents-cli eval optimize` | Auto-tune agent prompts using eval data |
| `agents-cli lint` | Check code quality |
| `agents-cli infra single-project` | Set up project infrastructure (Terraform) |
| `agents-cli deploy` | Deploy to dev |
| `agents-cli scaffold enhance` | Add deployment target or CI/CD to project |
| `agents-cli scaffold upgrade` | Upgrade project to latest version |

---

## Operational Guidelines for Coding Agents

- **Code preservation**: Only modify code directly targeted by the user's request. Preserve all surrounding code, config values (e.g., `model`), comments, and formatting.
- **NEVER change the model** unless explicitly asked.
- **Model 404 errors**: Fix `GOOGLE_CLOUD_LOCATION` (e.g., `global` instead of `us-east1`), not the model name.
- **ADK tool imports**: Import the tool instance, not the module: `from google.adk.tools.load_web_page import load_web_page`
- **Run Python with `uv`**: `uv run python script.py`. Run `agents-cli install` first.
- **Stop on repeated errors**: If the same error appears 3+ times, fix the root cause instead of retrying.
- **Terraform conflicts** (Error 409): Use `terraform import` instead of retrying creation.

---

## EZStore-specific notes (read before changing the agent)

- Spec: `../agent-spec-prompt.md`. Do **not** modify `../mcp_server/`, `../frontend/`, `../backend/`.
- ADK app name must stay `quotation_agent` and the graph must keep a node named `respond`: the Chat UI only shows
  events whose `nodeInfo.path` ends with `/respond@N`, and `scripts/grading/grade_agent.py` looks for
  `agent/quotation_agent/`.
- Only `classify_intent` calls the LLM. Tool choice, arguments, clarification and refusal live in `route`
  (`quotation_agent/intent.py` holds the rules). Keep it that way.
- ADK 2.11 edges are chains; conditional edges are dicts: `(route, {"clarify": clarify, ...})`, never
  `(a, b, "route")`.
- Never put `{` or `}` in an `instruction` string — ADK treats them as state placeholders.
- Fixed reply prefixes are part of the contract with the graders: clarify → 「請提供」, refuse → 「只能協助」,
  not found → 「找不到」 (no link), invalid value → 「操作失敗」. Links are always plain text.
- Local runs reach MCP at `http://localhost:8010/mcp` (Compose maps 8010→8000). Reseed before every actions eval:
  `docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql`.
- Tests need no API key: `uv run pytest tests/unit tests/integration -q` (fake classifier in `tests/support/fake_llm.py`).
