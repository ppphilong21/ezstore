# Trustworthiness report: EZStore quotation agent

> One page for a manager who has never seen the code (eval-lab.md §9).

**Date:** 2026-10-28 · **Agent:** `agent/` on branch `feature/ezstore-agent-develop` (PR #1) · **Student:** M11509803

**Models.** The agent is configured with `AGENT_MODEL` (default `gemini-3.8-flash`, temperature 0). The Agent 1 demos
(26/10) ran on `gemini-3.8-flash`. On 27–28/10 `gemini-3.8-flash` returned 503 (overloaded) and then 429 (daily free-tier
limit), so the graded run below used `AGENT_MODEL=gemini-3.1-flash-lite`. Judges: `refusal_or_action` on
`gemini-3.5-flash-lite`, `custom_response_quality` on `gemini-3.1-flash-lite`. Only environment settings changed, not code.

## 1. What was evaluated

| Dataset | Cases | Behaviour checked | Changes data |
|---|---|---|---|
| `quotation-guardrails.json` | 4 | 2 off-topic refusals (weather, add a customer), 1 multi-turn clarification, 1 not-found | no |
| `quotation-actions.json` | 6 | One per operation: lookup, list by customer, duplicate, change factor, change total, convert to order | yes |
| `scripts/grading/student-extra.json` | 2 | Not-found quotation, user asks for Markdown links | no |
| `quotation-multiturn.json` | 1 | Ask for the missing factor, then complete with "0.8" | yes |
| `quotation-edge-cases.json` | 6 | Unreachable total, factor 0, prompt injection, English request, Chinese numeral, Markdown request | yes |

The first three datasets plus 4 backend checks form the self-grading suite
(`scripts/grading/local/student-suite.json`, 0–100). The last two were written but **not run** in this round (see §7).

## 2. How it was evaluated

| Metric | Judged by | Guards |
|---|---|---|
| `custom_response_quality` (1–5) | LLM judge | Overall correctness and clarity against a reference description |
| `link_present` (0/1) | Code | Plain-text `/quotations/<id>` or `/orders/<id>` link; Markdown link = 0 |
| `refusal_or_action` (0/1) | LLM judge | Off-topic refused without tools; operations completed; honest about missing data |
| `agent_turn_count` | Code | Confirms multi-turn cases really ran 2 turns |
| Backend checks | Code (`grade_agent.py`) | Original QT-20260330-001 unchanged, ≥3 copies, a copy with factor 1.5, an order linked to the original |

Code checks cover the hard rules; LLM judges cover meaning. We read the judge's reason for each case (`eval_summary.py --explain`), not only the averages.

## 3. Results

Graded run 2026-10-28 16:02 (`artifacts/grading/20261028_160252/report.md`):

| Group | custom_response_quality | link_present | refusal_or_action | agent_turn_count | Lowest case |
|---|---|---|---|---|---|
| guardrails (4) | 5.00 | 1.00 | 1.00 | 1.25 (`clarify_then_complete` = 2) | all 100 % |
| actions (6) | 5.00 | 1.00 | 1.00 | 1.00 | all 100 % |
| extra (2) | 3.20 (5, 1) | 1.00 | 1.00 | 1.00 | `markdown_request` 88 % (quality 1/5) |

Backend checks: original unchanged **10/10** · ≥3 copies **5/5** · copy with factor 1.5 (QT-20261028-002) **5/5** ·
order ORD-20261028-001 linked to QT-20260330-001 **5/5**.

**Self-grading: 98.8 / 100** — guardrails 30.0/30, actions 50.0/50 (incl. backend 25/25), extra 18.8/20.

The only deduction is `markdown_request`: the user asks for Markdown links, the agent keeps plain-text links because
spec 1.8 requires them. Our own rules (`link_present`, `refusal_or_action`) score it 1; the generic quality judge gives 1/5.
We keep the spec behaviour on purpose.

## 4. Problems found and fixed

1. **Not-found replies were marked as failures.** "找不到報價單編號 QT-20990101-001" is the correct answer, but `link_present`
   demanded a link and the judge demanded a completed operation. Both rules now accept not-found, refusal, clarification
   and honest failure without a link.
2. **The judge expected the LLM to call tools.** In a graph Workflow the nodes call MCP, not the LLM. The judge prompt now
   says so and judges completion from the reply (new quotation/order number, link, 「未修改」).
3. **Agent-side fixes found while testing:** a bare answer such as "0.8" or "八千" to a clarification fills the missing
   field; tool error prefixes are removed from replies; invalid factors/totals are rejected before any copy is created.
4. **Grading needed a Google Cloud project.** The course judge was a `prompt_template` metric, sent to the Vertex Eval
   Service. The same rules now run as a local judge with the AI Studio key (`scripts/grading/local/`).
5. **Free-tier limits broke whole runs.** Default parallelism burst past 5 requests/minute and every reply became
   「操作失敗…429」 (score 37.7). Fixed with slow mode (`grade_slow.py`: one case at a time, spaced judges), retries on
   429/5xx, and a separate model per judge (`REFUSAL_JUDGE_MODEL`, `QUALITY_JUDGE_MODEL`).
6. **A judge model was not available.** `gemini-2.5-flash-lite` returns 404 for new projects, so `refusal_or_action`
   scored 0 everywhere (score 81.8 although all answers were right). Reading the judge's reason found it; switching the
   judge model gave 98.8.
7. **`AGENT_MODEL` in `agent/.env` was ignored by local runs.** The package was imported before `.env` was loaded, so the
   default model was used. Fixed by loading `.env` before the model is read (commit "Read AGENT_MODEL after loading
   agent/.env"). Docker was not affected (Compose passes the variable directly).

## 5. Stability

Not measured this round (no repeated identical run, because of the daily free-tier limit). The earlier runs (15.0, 37.7,
81.8) differed from 98.8 only because of infrastructure faults listed in §4 (credentials, 429/503, a missing judge model),
not because the agent's answers changed. Next step: `--runs 2` on the guardrails set and compare with `eval_summary.py A.json B.json`.

## 6. Break test

Not run this round (free-tier quota). Planned: switch every link in `respond` to Markdown `[查看](url)` and confirm that
`link_present` and `refusal_or_action` drop to 0 on the actions set while `custom_response_quality` barely moves.

## 7. Risks not yet covered

- `quotation-multiturn.json` and `quotation-edge-cases.json` (prompt injection, factor 0, unreachable total, English,
  Chinese numerals) were not run in this round.
- Similar customer names: the MCP tool takes the first fuzzy match, so 「工業」 could pick the wrong customer.
- Several operations in one message ("複製後再轉訂單") — only one is executed; no test yet.
- Model dependence: the graded run used `gemini-3.1-flash-lite`, the demos `gemini-3.8-flash`; results on other models are not measured.
- Free-tier quota and model overload (429/503) make runs fail; production needs a paid quota.
- The LLM judges can drift; code checks carry more than half of the weight.
