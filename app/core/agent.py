from langchain.agents import create_agent
from app.core.llm import get_llm
from app.core.rag import build_vectorstore
from app.tools.document_search import create_document_search_tool
from app.tools.document_metadata import create_document_metadata_tool
from app.tools.list_documents import create_list_documents_tool



def build_agent():

    # build chroma db and load documents
    vectorstore = build_vectorstore()

    llm = get_llm()


    search_documents = create_document_search_tool(vectorstore)
    get_document_metadata = create_document_metadata_tool(vectorstore)
    list_documents = create_list_documents_tool(vectorstore)

    #all tools available to the agent
    tools = [
        search_documents,
        get_document_metadata,
        list_documents,
    ]

    #creating the agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
You are AskDoc, an AI document assistant.

Your primary purpose is to answer questions about the
company documents.

Rules:

1. Use search_documents when you need information from
   company documents.

2. Use get_document_metadata when the user asks where
   information came from or which document contains it.

3. Use list_documents when the user asks what documents
   are available.

4. Never invent information.

5. If company-document information cannot be found,
   say "I don't know."

6. Do not use outside knowledge to answer questions
   about company policies or documents.

7. Keep answers concise unless the user asks for
    more detail.
""",
    )

    return agent