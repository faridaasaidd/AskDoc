import asyncio
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from app.core.graph import build_askdoc_graph


router = APIRouter()
graph = build_askdoc_graph()


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    escalated: bool = False
    thread_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "question": request.message,
        "original_question": request.message,
        "documents": [],
        "generation": "",
        "is_safe": True,
        "is_relevant": False,
        "is_grounded": False,
        "retry_count": 0,
        "sources": [],
        "escalated": False,
    }

    try:
        # Enforce 30-second total execution timeout for graph invocation
        result = await asyncio.wait_for(
            graph.ainvoke(initial_state, config=config, recursion_limit=10),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="The request timed out while waiting for a response. Please try again."
        )

    return ChatResponse(
        response=result.get("generation", ""),
        sources=result.get("sources", []),
        escalated=result.get("escalated", False),
        thread_id=thread_id,
    )
