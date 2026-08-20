import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from app.core.llm import get_embeddings


def format_docs(docs):
    """Format retrieved documents into a readable context string."""

    if not docs:
        return "No relevant context found."

    return "\n\n---\n\n".join(
        f"[Source: {Path(doc.metadata.get('source', '')).name}]\n"
        f"{doc.page_content}"
        for doc in docs
    )


def load_multi_format_documents(data_dir: Path):
    """Load .md, .txt, .pdf and .docx documents."""

    docs = []

    # Markdown and text
    for pattern in ["**/*.md", "**/*.txt"]:

        try:
            loader = DirectoryLoader(
                str(data_dir),
                glob=pattern,
                loader_cls=TextLoader,
                loader_kwargs={
                    "encoding": "utf-8"
                },
            )

            docs.extend(loader.load())

        except Exception as e:
            print(
                f"⚠️ Error loading {pattern}: {e}"
            )

    # PDFs
    for pdf_path in data_dir.glob("**/*.pdf"):

        try:
            loader = PyPDFLoader(str(pdf_path))

            docs.extend(loader.load())

        except Exception as e:
            print(
                f"⚠️ Error loading PDF "
                f"{pdf_path.name}: {e}"
            )

    # DOCX
    for docx_path in data_dir.glob("**/*.docx"):

        try:
            loader = Docx2txtLoader(
                str(docx_path)
            )

            docs.extend(loader.load())

        except Exception as e:
            print(
                f"⚠️ Error loading DOCX "
                f"{docx_path.name}: {e}"
            )

    return docs


def build_vectorstore(
    data_dir: Path | str | None = None,
    persist_dir: Path | str | None = None,
):

    if data_dir is None:

        data_dir = (
            PROJECT_ROOT / "data"
        )

    if persist_dir is None:

        persist_dir = (
            PROJECT_ROOT / "chroma_db"
        )

    data_dir = Path(data_dir)
    persist_dir = Path(persist_dir)

    embeddings = get_embeddings()

    # Load existing database
    if (
        persist_dir.exists()
        and any(persist_dir.iterdir())
    ):

        print(
            f"📦 Loading Chroma database "
            f"from {persist_dir}"
        )

        return Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings,
        )

    # Create database
    print(
        f"📄 Loading documents from "
        f"{data_dir}"
    )

    docs = load_multi_format_documents(
        data_dir
    )

    if not docs:

        raise RuntimeError(
            f"No documents found in {data_dir}"
        )

    print(
        f"📄 Loaded {len(docs)} documents/pages"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(docs)

    print(
        f"✂️ Created {len(chunks)} chunks"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )

    print(
        "✅ Vector database created successfully"
    )

    return vectorstore


def get_retriever(
    vectorstore: Chroma,
    k: int = 3,
):

    return vectorstore.as_retriever(
        search_kwargs={
            "k": k
        }
    )