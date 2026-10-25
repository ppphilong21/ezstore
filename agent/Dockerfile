# EZStore quotation agent (ADK 2.x Graph Workflow) — served by uvicorn on :8080
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.20 /uv /uvx /bin/

WORKDIR /code

# Dependencies first (cached layer), then the agent package
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY quotation_agent ./quotation_agent
RUN uv sync --frozen --no-dev

ARG AGENT_VERSION=0.1.0
ENV AGENT_VERSION=${AGENT_VERSION} \
    PYTHONUNBUFFERED=1 \
    MCP_URL=http://mcp-server:8000/mcp \
    APP_URL=http://agent:8080

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=10 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).status == 200 else 1)"

CMD ["uv", "run", "--no-sync", "uvicorn", "quotation_agent.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
