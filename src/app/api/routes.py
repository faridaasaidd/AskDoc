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


router = APIRouter()


# Build graph once

graph = build_askdoc_graph()


# Request/Response model

class ChatRequest(BaseModel):

    message: str

    thread_id: Optional[str] = None


class ChatResponse(BaseModel):

    response: str

    sources: list[str] = []

    escalated: bool = False

    thread_id: str


#Chat Endpoint

@router.post(
    "/chat",
    response_model=ChatResponse,
)

async def chat(
    request: ChatRequest,
):

    thread_id = (
        request.thread_id
        or str(uuid.uuid4())
    )


    config: RunnableConfig = {

        "configurable": {

            "thread_id":
                thread_id

        }

    }


    initial_state: AskDocState = {

        "messages": [

            HumanMessage(
                content=request.message
            )

        ],

        "generation": "",

        "is_safe": True,

        "sources": [],

        "escalated": False,

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

            detail=(
                "The request timed out. "
                "Please try again."
            ),

        )


    return ChatResponse(

        response=result.get(
            "generation",
            "",
        ),

        sources=result.get(
            "sources",
            [],
        ),

        escalated=result.get(
            "escalated",
            False,
        ),

        thread_id=thread_id,

    )