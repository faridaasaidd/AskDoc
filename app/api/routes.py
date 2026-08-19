from fastapi import APIRouter
from pydantic import BaseModel
#from app.core.llm import get_llm
from app.core.agent import build_agent



router = APIRouter()
agent = build_agent()

class ChatRequest(BaseModel):
    message: str
class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": request.message,
            }
        ]
    })
    response = result["messages"][-1].content
    return ChatResponse(response=response)
