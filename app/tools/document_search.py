from pathlib import Path
from langchain_core.tools import tool


def create_document_search_tool(vectorstore):

    @tool
    def search_documents(query: str) -> str:
        """Search company documents for information relevant to a query.

        Args:
            query: The user's question or search query.
        """

        if vectorstore is None:
            return "No documents indexed."

        results = vectorstore.similarity_search(query, k=3)

        if not results:
            return "No relevant documents found."

        formatted_results = []

        for i, doc in enumerate(results, start=1):
            source = Path(
                doc.metadata.get("source", "Unknown document")
            ).name

            formatted_results.append(
                f"""[Document {i}]
Source: {source}

Content:
{doc.page_content}"""
            )

        return "\n\n---\n\n".join(formatted_results)

    return search_documents