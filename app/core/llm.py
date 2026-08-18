import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, AzureChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


load_dotenv()


provider = None


if os.getenv("AZURE_OPENAI_API_KEY"):
    provider = "azure"

elif os.getenv("OPENAI_API_KEY"):
    provider = "openai"

elif os.getenv("GOOGLE_API_KEY"):
    provider = "gemini"


def get_llm(temperature: float = 0.0):
    if provider == "openai":
        pass
    elif provider == "azure":
        return AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "2024-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=temperature
        )

    elif provider == "gemini":
        pass
    else:
        raise ValueError("No provider configured.")


def get_embeddings():
    if provider == "openai":
        pass
    elif provider == "azure":
        return AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large-v1"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
    elif provider == "gemini":
        pass
    else:
            raise ValueError("No provider configured.")