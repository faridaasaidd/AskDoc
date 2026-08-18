from fastapi import FastAPI
from app.api.routes import router


app = FastAPI(
    title="AskDoc API",
    description="AI-powered document assistant",
    version="0.1.0",
)

@app.get("/")
def root():
    return {"name": "AskDoc","status": "running",}


app.include_router(router)