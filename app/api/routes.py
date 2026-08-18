from fastapi import APIRouter
from pydantic import BaseModel
from app.core.llm import get_llm


router = APIRouter()

class ChatRequest(BaseModel):
    message: str
class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    llm = get_llm()
    response = llm.invoke(request.message)
    return ChatResponse(response=response.content)