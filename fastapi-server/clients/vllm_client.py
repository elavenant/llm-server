from typing import Optional

import os
import httpx
import structlog
from schemas import ChatRequest, ChatResponse
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger()

class VLLMClient:
    """Client for vLLM API"""
    def __init__(self, model="/models"):
        self.model = model
        self.model_display_name = os.getenv("MODEL_DISPLAY_NAME", "unknown")

    @retry(
        reraise=True,
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=15)
    )
    async def chat(self, payload: ChatRequest, session_id: Optional[str] = None, base_url: str = None) -> ChatResponse:
        """Chat with vLLM"""
        data = payload.model_dump()
        data["model"] = self.model
        url = base_url

        headers = {}
        if session_id:
            headers["X-Session-Id"] = session_id
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{url}/v1/chat/completions", json=data, headers=headers)
                resp.raise_for_status()

                logger.info(
                    "vLLM request successful",
                    session_id=session_id,
                    status=resp.status_code
                )

                raw = resp.json()
                raw["model"] = self.model_display_name

                return ChatResponse(**raw)
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "vLLM request failed",
                session_id=session_id,
                status_code=e.response.status_code,
                content=e.response.content
            )
            raise

        except httpx.RequestError as e:
            logger.error(
                "Network error while requesting vLLM",
                session_id=session_id,
                error=str(e),
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error while requesting vLLM",
                session_id=session_id,
                error=str(e),
                exc_info=True
            )
            raise
