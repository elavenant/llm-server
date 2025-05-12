from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from logging_config import setup_structlog
from routers import chat

setup_structlog()

app = FastAPI(title="LLM Gateway")

instrumentator = Instrumentator()
instrumentator.instrument(app)

@app.get("/metrics")
def custom_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Routes métier
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    return {"ready": True}
