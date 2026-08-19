import importlib as imp
import sys

if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8")


REQUIRED_PACKAGES = [
    "langchain",
    "langchain_openai",
    "langchain_google_genai",
    "langgraph",
    "chromadb",
    "dotenv",
    "tiktoken",
    "pydantic",
    "rich",
]


def check_dependencies(verbose: bool = True) -> bool:
    """
        Checks whether all required dependencies are installed.
        Returns True if all packages are installed, False otherwise.
    """
    if verbose:
        print("Checking dependencies...")

    all_ok = True
    for pkg in REQUIRED_PACKAGES:
        try:
            mod = imp.import_module(pkg)
            ver = getattr(mod, "__version__", "ok")
            if verbose:
                print(f"    ✅ {pkg} - {ver}")
        except ImportError:
            all_ok = False
            if verbose:
                print(f"    ❌ {pkg} - NOT FOUND")

    if not all_ok and verbose:
        print("\nIf something has ❌, run: uv sync")

    return all_ok


if __name__ == "__main__":
    check_dependencies()
