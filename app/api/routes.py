import asyncio
import uuid

from typing import Optional

from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import BaseModel

from langchain_core.runnables import (
    RunnableConfig,
)

from langchain_core.messages import (
    HumanMessage,
)

from app.core.graph import (
    build_askdoc_graph,
    AskDocState,
)

from app.core.safety import SafetyLayer


router = APIRouter()

# Build graph once
graph = build_askdoc_graph()

# Initialize safety layer once
safety_layer = SafetyLayer()


# ==========================================
# Request / Response Models
# ==========================================

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
    escalated: bool = False
    thread_id: str


# ==========================================
# Chat Endpoint
# ==========================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
):
    thread_id = request.thread_id or str(uuid.uuid4())

    # 1. Input Guardrail
    is_safe, reason = safety_layer.check_input(request.message)
    if not is_safe:
        return ChatResponse(
            response=reason,
            sources=[],
            escalated=False,
            thread_id=thread_id,
        )

    # 2. Execute Graph
    config: RunnableConfig = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state: AskDocState = {
        "messages": [
            HumanMessage(content=request.message)
        ],
    }

    try:
        result = await asyncio.wait_for(
            graph.ainvoke(
                initial_state,
                config=config,
                recursion_limit=10,
            ),
            timeout=30.0,
        )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="The request timed out. Please try again.",
        )

    # 3. Post-Process Graph Output
    output = result["messages"][-1].content
    
    if isinstance(output, list):
        # Extract text from multimodal/safety chunk list
        extracted = []
        for block in output:
            if isinstance(block, dict) and "text" in block:
                extracted.append(block["text"])
            elif isinstance(block, str):
                extracted.append(block)
        output = " ".join(extracted)

    if not isinstance(output, str):
        output = str(output)

    # 4. Output Guardrail (PII Redaction)
    generation = safety_layer.sanitize_output(output)

    # Note: sources and escalated logic can be added later if needed.
    # For now, matching the previous behavior where they are empty/False.

    return ChatResponse(
        response=generation,
        sources=[],
        escalated=False,
        thread_id=thread_id,
    )