"""ADK API server + dev UI for the sales advisor (http://localhost:8502/dev-ui/?app=sales_advisor in Compose)."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app: FastAPI = get_fast_api_app(agents_dir=AGENT_DIR, web=True, otel_to_cloud=False)
app.title = "ezstore-sales-advisor"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
