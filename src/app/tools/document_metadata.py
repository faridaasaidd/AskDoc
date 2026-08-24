from langchain_core.tools import tool


def create_document_metadata_tool(vectorstore):

    @tool
    def get_document_metadata(query: str) -> str:
        """Find document sources related to a query.

        Args:
            query: Search for documents related to this topic.
        """

        if vectorstore is None:
            return "No documents indexed."

        results = vectorstore.similarity_search(query,k=5)

        if not results:
            return "No relevant documents found."

        output = []
        seen = set()

        for document in results:
            source = document.metadata.get("source", "Unknown source")
            page = document.metadata.get("page")
            key = (source, page)
            if key in seen:
                continue
            seen.add(key)
            if page is not None:
                output.append(f"Document: {source}\n"f"Page: {page}")
            else:
                output.append(f"Document: {source}")

        return "\n\n".join(output)

    return get_document_metadata