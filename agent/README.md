# EZStore quotation agent (`agent/`)

ADK 2.x **Graph Workflow** that lets users manage quotations in natural language from the EZStore Chat UI
(http://localhost:3000/agent). Scaffolded with `agents-cli scaffold create … --agent-directory quotation_agent`,
app name `quotation_agent`.

```
quotation_agent/
├── agent.py          # the Workflow graph: nodes + edges, App(name="quotation_agent")
├── intent.py         # Intent schema (LLM output) + all code rules: guardrails, regex extraction, Chinese numerals
├── mcp_client.py     # McpToolset (Streamable HTTP, MCP_URL) + call_tool()
├── messages.py       # fixed replies (clarify / refusal / errors) + Markdown → plain-text cleanup
├── a2a_skills.py     # skills advertised in the A2A agent card
├── fast_api_app.py   # ADK API server (/run_sse for the Chat UI) + A2A routes (/a2a/quotation_agent)
└── app_utils/        # scaffold helpers (A2A routes, shared in-memory session service)
scripts/call_mcp.py   # call one MCP tool directly (stage 4.1)
tests/unit            # intent rules + graph routing with a fake classifier and stubbed MCP (no key, no network)
tests/integration     # real MCP (skipped if unreachable) + HTTP contract of /run_sse and A2A
tests/eval            # agents-cli eval datasets, eval_config.yaml, metric files
```

## 1. Graph design

```
START → load_context ─(classify)→ classify_intent → route ─┬→ get_quotation ────────────┐
            │                                               ├→ list_customer_quotations ─┤
            │                                               ├→ duplicate_quotation ──────┤
            │                                               ├→ update_pricing_factor ────┤
            │                                               ├→ adjust_total_price ───────┼→ respond
            │                                               ├→ convert_to_order ─────────┤
            │                                               ├→ clarify ──────────────────┤
            │                                               ├→ off_topic ────────────────┤
            │                                               └─(direct)───────────────────┤
            └─(direct: no credentials)───────────────────────────────────────────────────┘
```

Why it is shaped like this:

1. **Only `classify_intent` calls Gemini.** It is an `LlmAgent` with `output_schema=Intent` and temperature 0, so it can
   only return structured fields (`intent`, `quotation_number`, `customer_name`, `new_pricing_factor`,
   `target_total_price`). It never writes the reply and never picks a tool.
2. **`route` is plain Python** and has the final say:
   - guardrail regexes (`intent.guardrail_violation`) refuse prompt injection, customer/product/order CRUD and
     delete/publish quotation **even if the LLM says otherwise** (spec 1.10: refusal decided by code);
   - regex extraction (`intent.code_extract`) overrides the LLM for things that are written explicitly
     (QT numbers incl. full-width, factors, totals, Chinese numerals like 一點五 / 八千 / 1.2萬, 打八折);
   - required fields per operation (`REQUIRED_FIELDS`); anything missing → `clarify` and
     `state.pending_intent = {intent, args}`;
   - value checks (factor must be 0 < f < 10, total > 0) → reply without calling MCP, so no copy is created.
3. **Each action node calls exactly one MCP tool** (`mcp_client.call_tool` → `McpToolset.get_tools()` →
   `tool.run_async()`), and emits a `function_call` / `function_response` event pair so the tool call is visible in
   the ADK dev UI and in eval traces. MCP errors (e.g. 找不到報價單編號) are passed on, not raised.
4. **`respond` is the only node that emits user-facing text.** The Chat UI shows events whose `nodeInfo.path` ends
   with `/respond@N` (see `frontend/src/api/agentApi.ts`), and `agents-cli eval` grades the last text event, which is
   always `respond`'s. It also converts any `[text](url)` into a plain URL.
5. **Every message restarts at `START`.** Cross-turn memory is `state.pending_intent`. When state is empty but the
   history shows "user asked for X → assistant asked for a field" (this is how `agents-cli eval` seeds multi-turn
   cases), `load_context` rebuilds the pending operation from those events.
6. **No credentials → still starts.** `load_context` checks `GEMINI_API_KEY` / Vertex settings and replies with a clear
   configuration message; model errors at runtime (bad key, quota) are caught by `on_model_error_callback` and turned
   into a readable reply.

Fixed reply conventions (the grading scripts rely on them): clarifications start with 「請提供」 (or
「請告訴我您要對報價單…」 when the operation is unknown), refusals contain 「只能協助」, not-found replies contain
「找不到」 and no link, invalid values start with 「操作失敗」.

### ADK 2.11 gotchas we hit

- **Edges are chains.** `(a, b, c)` means a→b→c. Conditional routing is a dict:
  `(route, {"clarify": clarify, "off_topic": off_topic, ...})`. Writing `(a, b, "route_name")` fails validation.
  The node emits `Event(output=..., route="clarify")`.
- **No curly braces in `instruction`.** ADK substitutes `{name}` from session state; a literal JSON example in the
  prompt raises a KeyError. The prompt therefore describes fields in words; the schema comes from `output_schema`.
- A single-turn `LlmAgent` node sees only its `node_input` (`include_contents='none'`), so `load_context` passes the
  history and pending operation inside the input text.
- Function-node parameters other than `ctx` / `node_input` are read from `ctx.state` (`route(..., turn_context)`).

## 2. How to add an operation

Example: a new MCP tool `publish_quotation(quotation_number)` (it would have to exist in `mcp_server/` first).

1. `intent.py`: add `"publish_quotation"` to `ACTION_INTENTS`, `IntentName`, `REQUIRED_FIELDS`
   (`("quotation_number",)`), `OPERATION_LABELS`; add a keyword pattern to `_KEYWORD_INTENTS`; remove "發佈" from
   `_UNSUPPORTED_QUOTATION_OP_RE`.
2. `agent.py`: describe the intent in `CLASSIFIER_INSTRUCTION` (no braces), add a node

   ```python
   async def publish_quotation(ctx: Context, node_input: dict[str, Any]):
       async for ev in _run_tool(ctx, "publish_quotation", {"quotation_number": node_input["args"]["quotation_number"]}):
           yield ev
   ```

   and append it to `ACTION_NODES` (edges `route → publish_quotation → respond` are generated from that tuple; the
   route name is the function name).
3. `a2a_skills.py`: add a skill. `messages.SUPPORTED_OPERATIONS`: add the label.
4. Tests: a row in `tests/unit/test_workflow.py::SIX`, an eval case in `tests/eval/datasets/quotation-actions.json`
   with `eval_case_id` = tool name, then run `uv run pytest tests/unit -q` and `agents-cli eval run`.

## 3. Run, test, evaluate

```bash
cp .env.example .env                  # GEMINI_API_KEY=..., MCP_URL=http://localhost:8010/mcp
uv sync --group dev --extra eval
uv run python scripts/call_mcp.py get_quotation quotation_number=QT-20260330-001
agents-cli playground                 # or: agents-cli run "我要查詢報價單，報價單編號：QT-20260330-001"
uv run pytest tests/unit tests/integration -q
agents-cli eval run --dataset tests/eval/datasets/quotation-guardrails.json --config tests/eval/eval_config.yaml --output artifacts/grade_results/guardrails
python3 ../scripts/eval_summary.py artifacts/grade_results/guardrails/results_<timestamp>.json --explain
```

Datasets: `quotation-actions.json` (6 cases, one per tool, **changes data — reseed first**),
`quotation-guardrails.json` (2 off-topic + `clarify_then_complete` multi-turn, plus `not_found_quotation` from the
eval lab), `quotation-multiturn.json` (eval lab §8: ask for the missing factor, then complete; changes data).

## 4. A2A

`fast_api_app.py` also mounts the A2A protocol (a2a-sdk 1.x, ADK `A2aAgentExecutor`) on the same runner:

- Agent card: `GET /a2a/quotation_agent/.well-known/agent-card.json` (6 skills from `a2a_skills.py`)
- JSON-RPC: `POST /a2a/quotation_agent` (`message/send`, streaming supported)

Inside Compose the card advertises `http://agent:8080/a2a/quotation_agent` (`APP_URL`). The sales advisor agent
(`../advisor_agent/`) uses it to delegate quotation operations.
