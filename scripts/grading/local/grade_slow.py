"""Run ../grade_agent.py in slow mode for the AI Studio free tier.

Same suite, same datasets, same scoring. The only differences:
- agents-cli runs one eval case at a time (--concurrency 1) instead of one per CPU core,
- metric computations are dispatched slowly (--qps), and the local LLM judges are spaced out,
so the agent and the judges stay under the free tier's requests-per-minute limit
(429 RESOURCE_EXHAUSTED otherwise). The instructor's grade_agent.py is not modified.

Usage (from the repo root), with the same arguments as grade_agent.py:
    uv run --no-project python scripts/grading/local/grade_slow.py --suite scripts/grading/local/student-suite.json

Tuning (environment variables):
    EVAL_CONCURRENCY    eval cases run in parallel          (default 1)
    EVAL_QPS            metric computations per second      (default 0.1 = 6 per minute)
    JUDGE_MIN_INTERVAL  seconds between two judge calls     (default 12)
    JUDGE_MODEL         model for the LLM judges            (default: AGENT_MODEL from agent/.env)
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("grade_agent", HERE.parent / "grade_agent.py")
grade_agent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(grade_agent)

CONCURRENCY = os.environ.get("EVAL_CONCURRENCY", "1")
QPS = os.environ.get("EVAL_QPS", "0.1")
# Inherited by the agents-cli subprocess, where the judges read it.
os.environ.setdefault("JUDGE_MIN_INTERVAL", "12")


def run_eval(agent_dir: Path, dataset: Path, config: Path, output: Path) -> tuple[bool, str]:
    """grade_agent.run_eval plus --concurrency / --qps."""
    cmd = [
        "agents-cli", "eval", "run",
        "--dataset", str(dataset),
        "--config", str(config),
        "--output", str(output),
        "--concurrency", CONCURRENCY,
        "--qps", QPS,
    ]
    proc = subprocess.run(cmd, cwd=agent_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = "\n".join((proc.stdout + "\n" + proc.stderr).strip().splitlines()[-30:])
    return proc.returncode == 0, tail


grade_agent.run_eval = run_eval

if __name__ == "__main__":
    grade_agent.log(
        f"慢速模式：--concurrency {CONCURRENCY} --qps {QPS}，"
        f"評審間隔 {os.environ['JUDGE_MIN_INTERVAL']} 秒（AI Studio 免費額度）"
    )
    sys.exit(grade_agent.main())
