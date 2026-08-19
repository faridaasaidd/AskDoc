import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8")


from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from app.core.imports import check_dependencies
# pyrefly: ignore [missing-import]
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