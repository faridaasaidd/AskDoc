import os
import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, AzureChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8")
load_dotenv()



provider = None
if os.getenv("AZURE_OPENAI_API_KEY"):
    provider = "azure"
elif os.getenv("OPENAI_API_KEY"):
    provider = "openai"
elif os.getenv("GOOGLE_API_KEY"):
    provider = "gemini"

if provider:
    print(f"✅ Detected provider: {provider}")
else:
    print("❌ No API keys found. Edit .env")

def get_llm(temperature: float = 0.0):
    """Return a chat model for the configured provider with explicit timeout."""
    if provider == "openai":
        return ChatOpenAI(model="gpt-4o", temperature=temperature, timeout=30.0)
    elif provider == "azure":
        return AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            temperature=temperature,
            timeout=30.0,
        )
    elif provider == "gemini":
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, max_retries=3, timeout=30.0)
    else:
        raise ValueError("No provider configured.")


def get_embeddings():
    """Return an embedding model for the configured provider."""
    if provider == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif provider == "azure":
        return AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"), 
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
    elif provider == "gemini":
        return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    else:
        raise ValueError("No provider configured.")

# Test your setup
if __name__ == "__main__":
    try:
        # pyrefly: ignore [missing-import]
        from app.core.imports import check_dependencies

        check_dependencies(verbose=False)
    except ImportError:
        pass

    llm = get_llm()
    response = llm.invoke("Say 'Hello, AI Path!' and nothing else.")
    print(f"LLM: {response.content}")

    embeddings = get_embeddings()
    vector = embeddings.embed_query("test")
    print(f"Embedding dimensions: {len(vector)}")
    print("✅ Setup complete!")
