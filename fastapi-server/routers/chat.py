from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse
import structlog
import uuid

from schemas import ChatRequest
from clients import VLLMClient
from utils import resolve_vllm_backends, pick_backend

router = APIRouter()
logger = structlog.get_logger()
vllm_client = VLLMClient()

@router.post("/chat")
async def chat(
    request: Request,
    body: ChatRequest,
    x_session_id: str = Header(default=None, alias="X-Session-ID"),
):
    session_id = x_session_id or str(uuid.uuid4())
    logger.info("Received chat request", session_id=session_id)

    try:
        backends = resolve_vllm_backends()
        if not backends:
            raise RuntimeError("No vLLM backends available")

        target_url = pick_backend(session_id, backends)
        logger.info("Routing to vLLM backend", session_id=session_id, backend=target_url)

        response = await vllm_client.chat(payload=body, session_id=session_id, base_url=target_url)

        return JSONResponse(content=response.model_dump(), headers={"X-Session-ID": session_id})

    except Exception as e:
        logger.exception("Chat request failed", session_id=session_id)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
