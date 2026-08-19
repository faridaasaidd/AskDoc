from langchain_core.tools import tool


def create_document_search_tool(vectorstore):

    @tool
    def search_documents(query: str) -> str:
        """Search company documents for information.

        Args:
            query: The search query.
        """

        if vectorstore is None:
            return "No documents indexed."

        results = vectorstore.similarity_search(query, k=2)
        return "\n".join(r.page_content for r in results)
    
    return search_documents