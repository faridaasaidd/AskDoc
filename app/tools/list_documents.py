from langchain_core.tools import tool


def create_list_documents_tool(vectorstore):

    @tool
    def list_documents() -> str:
        """List all documents currently indexed in AskDoc."""

        if vectorstore is None:
            return "No documents indexed."

        try:
            data = vectorstore.get()
            metadatas = data.get("metadatas", [])
            if not metadatas:
                return "No documents indexed."
            documents = set()
            for metadata in metadatas:
                if not metadata:
                    continue
                source = metadata.get("source","Unknown source")
                documents.add(source)

            if not documents:
                return "No documents indexed."

            return "Available documents:\n\n" + "\n".join(f"- {document}"for document in sorted(documents))

        except Exception as e:
            return f"Unable to list documents: {e}"

    return list_documents