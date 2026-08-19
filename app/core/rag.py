import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
#from langchain_core.output_parsers import StrOutputParser
#from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.runnables import RunnablePassthrough
#from app.core.llm import get_llm, get_embeddings
from app.core.llm import get_embeddings



if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8")


#ASKDOC_SYSTEM_PROMPT = """You are AskDoc agent, a document assistant. Answer only based on given context. If the answer is not in the context say "I don't know". Cite the answer from context. Never cite information from other sources except the context. Answer shortly and to the point unless the user states otherwise. Include all necessary details related to context."""

#askdoc_template = ChatPromptTemplate.from_messages([
#    ("system", ASKDOC_SYSTEM_PROMPT),
#    ("human", "Context:\n{context}\n\nQuestion: {question}")
#])


def format_docs(docs):
    """Format list of retrieved documents into a single context string with sources."""
    if not docs:
        return "No relevant context found."
    return "\n\n---\n\n".join(
        f"[Source: {Path(doc.metadata.get('source', '')).name}]\n{doc.page_content}"
        for doc in docs
    )


from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader


def load_multi_format_documents(data_dir: Path) -> list:
    """Load Markdown (*.md), Text (*.txt), PDF (*.pdf), and Word (*.docx) files from data_dir."""
    docs = []

    # 1. Load Markdown and Text files
    for glob_pattern in ["**/*.md", "**/*.txt"]:
        try:
            loader = DirectoryLoader(
                str(data_dir),
                glob=glob_pattern,
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
            )
            loaded = loader.load()
            docs.extend(loaded)
        except Exception as e:
            print(f"⚠️ Warning loading {glob_pattern}: {e}")

    # 2. Load PDF files (*.pdf)
    for pdf_path in data_dir.glob("**/*.pdf"):
        try:
            pdf_loader = PyPDFLoader(str(pdf_path))
            docs.extend(pdf_loader.load())
        except Exception as e:
            print(f"⚠️ Warning loading PDF '{pdf_path.name}': {e}")

    # 3. Load DOCX files (*.docx)
    for docx_path in data_dir.glob("**/*.docx"):
        try:
            docx_loader = Docx2txtLoader(str(docx_path))
            docs.extend(docx_loader.load())
        except Exception as e:
            print(f"⚠️ Warning loading DOCX '{docx_path.name}': {e}")

    return docs


def build_vectorstore(data_dir: Path | str | None = None, persist_dir: Path | str | None = None):
    """Load and chunk multi-format documents ONCE. Subsequent calls load from disk persistence."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    if persist_dir is None:
        persist_dir = Path(__file__).resolve().parent.parent.parent / "chroma_db"

    data_dir = Path(data_dir)
    persist_dir = Path(persist_dir)
    embeddings = get_embeddings()

    # 1. If vector DB already exists on disk, load directly (NO re-chunking)
    if persist_dir.exists() and any(persist_dir.iterdir()):
        print(f"📦 Loading persisted Chroma vectorstore from disk: {persist_dir}")
        vectorstore = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings,
        )
        return vectorstore

    # 2. First-time setup: Load multi-format documents, split, embed, and persist to disk
    print(f"📄 First-time setup: Loading multi-format documents (.md, .txt, .pdf, .docx) from: {data_dir}")
    docs = load_multi_format_documents(data_dir)
    print(f"    Loaded {len(docs)} document(s)/page(s).")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"    Created {len(chunks)} text chunk(s).")

    # Create VectorStore and persist to disk
    print(f"💾 Saving embedded chunks to disk: {persist_dir}")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )
    print("✅ Chroma vectorstore persisted successfully.")
    return vectorstore


def get_retriever(vectorstore: Chroma, k: int = 3):
    """Return a retriever for the vectorstore."""
    return vectorstore.as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    vectorstore = build_vectorstore()
    retriever = get_retriever(vectorstore)
    sample_docs = retriever.invoke("What is the remote work policy?")
    print(f"\nSample Retrieval Result ({len(sample_docs)} docs):")
    print(format_docs(sample_docs))
