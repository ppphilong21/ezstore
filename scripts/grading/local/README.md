# Local-judge grading variant (AI Studio key only)

`../student-suite.json` uses `../eval_config.yaml`, whose `refusal_or_action` metric is a `prompt_template`.
agents-cli sends that kind of metric to the Gemini platform Eval Service, which needs a real Google Cloud
project and Application Default Credentials. With only an AI Studio key (`GEMINI_API_KEY`), grading
stops with `Authentication failed using Compute Engine authentication`.

This folder is the same suite with every metric executed locally:

| File | Same as | Difference |
|---|---|---|
| `student-suite.json` | `../student-suite.json` | dataset paths one level deeper; `config` points here |
| `eval_config.yaml` | `../eval_config.yaml` | `refusal_or_action` is a local judge file instead of a `prompt_template` |
| `refusal_or_action.py` | rules 1–6 of `../eval_config.yaml`, verbatim | runs with google-genai + `GEMINI_API_KEY`, retries on 429, spaced calls |
| `response_quality.py` | `../response_quality.py` | retries on 429, spaced calls (`JUDGE_MIN_INTERVAL`, default 5 s) |
| `grade_slow.py` | `../grade_agent.py` (imported, not copied) | adds `--concurrency 1 --qps 0.1` and 12 s between judge calls |
| `link_present` | `../link_presence.py` (used directly) | — |

Weights, checks, backend post-checks and `grade_agent.py` are unchanged.

```bash
# agent/.env must contain GEMINI_API_KEY, MCP_URL=http://localhost:8010/mcp,
# GOOGLE_CLOUD_PROJECT=local-only and GOOGLE_APPLICATION_CREDENTIALS=tests/eval/adc-placeholder.json
python3 scripts/grading/grade_agent.py --suite scripts/grading/local/student-suite.json
```

## Free tier: `429 RESOURCE_EXHAUSTED`

agents-cli runs one eval case per CPU core by default, which bursts past the AI Studio free tier's
requests-per-minute limit: every agent reply becomes 「操作失敗：呼叫模型服務時發生錯誤…（_ResourceExhaustedError…）」
and the judges fail too. Run the same suite in slow mode instead (about 20–30 minutes):

```bash
python3 scripts/grading/local/grade_slow.py --suite scripts/grading/local/student-suite.json
# one group at a time if needed:  ... --only guardrails   /  --only actions  /  --only extra
```

Optional: set `JUDGE_MODEL` in `agent/.env` to another model so the judges use a separate quota. If that model's daily
limit is below the ~22 judge calls of one run, split them: `REFUSAL_JUDGE_MODEL` and `QUALITY_JUDGE_MODEL` (about 11 each).
A daily quota (`...PerDay...` in the 429 details) is not fixed by going slower: wait for the reset,
or use a key from a new Google Cloud project.

