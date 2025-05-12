from pydantic import BaseModel
from typing import List, Optional, Any

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.7
    top_p: float = 1.0
    tools: Optional[List[dict[str, Any]]] = None
    max_tokens: int = 100
    top_k: int = 50
    repetition_penalty: float = 1.0
    length_penalty: float = 1.0
    stop: Optional[List[str]] = None

class ChatResponseChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class ChatResponseUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    object: str
    created: int
    model: str
    choices: List[ChatResponseChoice]
    usage: Optional[ChatResponseUsage] = None
