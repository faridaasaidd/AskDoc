from fastapi import FastAPI
from app.core.imports import check_dependencies
from app.api.routes import router


# Verify all required dependencies on application startup
check_dependencies(verbose=True)

app = FastAPI(
    title="AskDoc API",
    description="AI-powered document assistant",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "AskDoc",
        "status": "running",
    }


app.include_router(router)
