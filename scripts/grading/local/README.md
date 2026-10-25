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
| `link_present` | `../link_presence.py` (used directly) | — |

Weights, checks, backend post-checks and `grade_agent.py` are unchanged.

```bash
# agent/.env must contain GEMINI_API_KEY, MCP_URL=http://localhost:8010/mcp,
# GOOGLE_CLOUD_PROJECT=local-only and GOOGLE_APPLICATION_CREDENTIALS=tests/eval/adc-placeholder.json
python3 scripts/grading/grade_agent.py --suite scripts/grading/local/student-suite.json
```
