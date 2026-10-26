# Trustworthiness report: EZStore quotation agent

> One page for a manager who has never seen the code (eval-lab.md §9).
> Numbers in `[brackets]` are filled from the runs listed under each heading. Everything else is already true.

**Date:** [YYYY-MM-DD] · **Model:** gemini-3.8-flash (temperature 0) · **Agent:** `agent/` on branch `feature/ezstore-agent-develop`

## 1. What was evaluated

17 eval cases in 4 datasets, plus the course's self-grading suite:

| Dataset | Cases | Behaviour checked | Changes data |
|---|---|---|---|
| `quotation-actions.json` | 6 | One per operation: lookup, list by customer, duplicate, change factor, change total, convert to order | yes |
| `quotation-guardrails.json` | 4 | 2 off-topic refusals (weather, add a customer), 1 multi-turn clarification, 1 not-found | no |
| `quotation-multiturn.json` | 1 | Ask for the missing factor, then complete with "0.8" | yes |
| `quotation-edge-cases.json` | 6 | Unreachable total (100000), factor 0, prompt injection, English request, Chinese numeral (一點二), Markdown request | yes |
| `scripts/grading/local/student-suite.json` | 11 + 4 backend checks | Course self-grading (0–100), all judges run locally with the AI Studio key | yes |

## 2. How it was evaluated

| Metric | Judged by | Guards |
|---|---|---|
| `custom_response_quality` (1–5) | LLM judge | Overall correctness and clarity against a reference description |
| `link_present` (0/1) | Code | Plain-text `/quotations/<id>` or `/orders/<id>` link; Markdown link = 0 |
| `refusal_or_action` (0/1) | LLM judge | Off-topic refused without tools; operations completed; honest about missing data |
| `agent_turn_count` | Code | Confirms multi-turn cases really ran 2 turns |
| Backend checks | Code (grade_agent.py) | Original QT-20260330-001 unchanged (factor 0.95, draft), ≥3 copies, a copy with factor 1.5, an order linked to the original |

Code checks cover the hard rules; LLM judges cover meaning. We read the judge's reason for each case, not only the averages.

## 3. Results

| Run | custom_response_quality | link_present | refusal_or_action | Lowest case |
|---|---|---|---|---|
| guardrails | [ ] | [ ] | [ ] | [ ] |
| actions | [ ] | [ ] | [ ] | [ ] |
| multiturn | [ ] | [ ] | [ ] | — |
| edge-cases | [ ] | [ ] | [ ] | [ ] |

Self-grading (`scripts/grading/local/grade_slow.py --suite scripts/grading/local/student-suite.json`): **[score] / 100**
(guardrails [ ]/30, actions [ ]/50 incl. backend checks [ ]/25, extra [ ]/20). Report: `artifacts/grading/[timestamp]/report.md`.

## 4. Problems found and fixed

1. **Not-found replies were marked as failures.** "找不到報價單編號 QT-20990101-001" is the correct answer, but
   `link_present` demanded a link and `refusal_or_action` rule 2 demanded a completed operation. Both rules were fixed
   (not-found / refusal / clarification / honest failure need no link; rule 4 and rule 5 added to the judge).
   Before → after on `not_found_quotation`: link_present [0 → 1], refusal_or_action [0 → 1].
2. **The judge expected the LLM to call tools.** In a graph Workflow the nodes call MCP, not the LLM. The judge prompt now
   says so and judges completion from the reply (new quotation/order number, link, 「未修改」).
3. **Agent-side fixes found while testing:** a bare answer such as "0.8" or "八千" to a clarification is now filled into
   the missing field; tool error prefixes ("Error executing tool …") are removed from replies; invalid factors/totals
   are rejected before any copy is created.

## 5. Stability

Guardrails dataset run twice (`eval_summary.py A.json B.json`): [number of `*` differences] differences.
[If any: which case, which metric, and whether the reply itself changed or only the judge.]

## 6. Break test

Switching every link in `respond` to Markdown `[查看](url)`: link_present on actions [1.00 → 0.00], refusal_or_action
[1.00 → 0.00], custom_response_quality only [5.00 → ?]. The generic quality judge barely notices; our own rule catches it.
After reverting, all scores return to [ ].

## 7. Risks not yet covered

- Similar customer names: the MCP tool takes the first fuzzy match (ILIKE), so 「工業」 could pick the wrong customer.
- Several operations in one message ("複製後再轉訂單") — only one is executed; no test yet.
- Large Chinese numerals and mixed units (十二萬三千五, 1萬2) are only partly covered by tests.
- Concurrency: the backend retries number collisions, but parallel edits of the same quotation are untested.
- The LLM judges themselves can drift; code checks keep more than half of the weight.
- Free-tier rate limits: with the default parallelism every reply became a 429 error (score 37.7). Grading runs in slow
  mode (`grade_slow.py`: one case at a time, spaced judge calls); a production deployment needs a paid quota.
