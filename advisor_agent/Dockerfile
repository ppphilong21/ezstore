# EZStore sales advisor agent (Agent 2). Build context = repository root:
#   docker build -f advisor_agent/Dockerfile .
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.20 /uv /uvx /bin/

WORKDIR /app

COPY advisor_agent/pyproject.toml advisor_agent/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY advisor_agent/sales_advisor ./sales_advisor
COPY knowledge ./knowledge
RUN uv sync --frozen --no-dev

ENV PYTHONUNBUFFERED=1 \
    OKF_BUNDLE=/app/knowledge/ezstore-okf \
    QUOTATION_AGENT_A2A_URL=http://agent:8080/a2a/quotation_agent \
    BACKEND_URL=http://backend:8080

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=10 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).status == 200 else 1)"

CMD ["uv", "run", "--no-sync", "uvicorn", "sales_advisor.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
