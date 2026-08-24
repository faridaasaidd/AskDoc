import sys
from pathlib import Path

# Add project root directory to sys.path across the app
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8")


# pyrefly: ignore [missing-import]
from app.core.imports import check_dependencies


# Run silent dependency check on core module load
check_dependencies(verbose=False)

__all__ = ["check_dependencies"]
