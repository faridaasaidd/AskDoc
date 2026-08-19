import os
import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
# pyrefly: ignore [missing-import]
from app.core.llm import get_llm, get_embeddings



if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8")


ASKDOC_SYSTEM_PROMPT = """You are AskDoc agent, a document assistant. Answer only based on given context. If the answer is not in the context say "I don't know". Cite the answer from context. Never cite information from other sources except the context. Answer shortly and to the point unless the user states otherwise. Include all necessary details related to context."""

askdoc_template = ChatPromptTemplate.from_messages([
    ("system", ASKDOC_SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])


def format_docs(docs):
    """Format list of retrieved documents into a single context string."""
    return "\n\n---\n\n".join(
        f"[Source: {Path(doc.metadata.get('source', '')).name}]\n{doc.page_content}"
        for doc in docs
    )


def build_rag_chain(data_dir: Path | str | None = None):

    """Load documents from data_dir, build Chroma vectorstore, and return a RAG chain."""
    if data_dir is None:
        # Default to /data in the project root
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"

    data_dir = Path(data_dir)
    print(f"📄 Loading documents from: {data_dir}")

    # 1. Load documents
    loader = DirectoryLoader(
        str(data_dir),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    print(f"    Loaded {len(docs)} document(s).")

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"    Created {len(chunks)} text chunk(s).")

    # 3. Create VectorStore and Retriever
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 4. Construct RAG chain
    llm = get_llm()
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | askdoc_template
        | llm
        | StrOutputParser()
    )

    return rag_chain


if __name__ == "__main__":
    rag_chain = build_rag_chain()

    questions = [
        "What is the remote work policy?",
        "What are the security guidelines for passwords?",
        "What is the company's revenue?",
    ]

    print("\n--- RAG Test Queries ---")
    for q in questions:
        print(f"\n❓ Question: {q}")
        response = rag_chain.invoke(q)
        print(f"💡 Answer: {response}")

