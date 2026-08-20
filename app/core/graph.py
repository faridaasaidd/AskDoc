import sys
from pathlib import Path
from typing import Annotated, Any

from typing_extensions import TypedDict

from langchain_core.messages import (
    AnyMessage,
    AIMessage,
    SystemMessage,
)

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode

from langgraph.checkpoint.memory import MemorySaver


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.core.llm import get_llm
from app.core.rag import build_vectorstore

from app.core.safety import (
    sanitize_and_validate_input,
    redact_pii,
)

from app.tools.document_search import (
    create_document_search_tool,
)

from app.tools.document_metadata import (
    create_document_metadata_tool,
)

from app.tools.list_documents import (
    create_list_documents_tool,
)


# ==========================================
# State
# ==========================================

class AskDocState(TypedDict):

    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]

    generation: str

    is_safe: bool

    sources: list[str]

    escalated: bool


# ==========================================
# Safety Node
# ==========================================

def safety_guardrail_node(
    state: AskDocState,
) -> dict[str, Any]:

    # Find the latest user message

    user_message = next(
        (
            message
            for message in reversed(
                state["messages"]
            )
            if message.type == "human"
        ),
        None,
    )

    if user_message is None:

        return {
            "is_safe": False,
            "generation": (
                "I could not find a user question."
            ),
        }

    question = str(
        user_message.content
    )

    is_valid, validation_message = (
        sanitize_and_validate_input(
            question
        )
    )

    if not is_valid:

        return {
            "is_safe": False,

            "generation": (
                "I cannot process this request. "
                f"{validation_message}"
            ),

            "escalated": False,
        }

    return {
        "is_safe": True
    }


# ==========================================
# Agent
# ==========================================

def build_askdoc_graph(
    vectorstore=None,
):

    if vectorstore is None:

        vectorstore = (
            build_vectorstore()
        )

    # Create tools

    search_documents = (
        create_document_search_tool(
            vectorstore
        )
    )

    get_document_metadata = (
        create_document_metadata_tool(
            vectorstore
        )
    )

    list_documents = (
        create_list_documents_tool(
            vectorstore
        )
    )

    tools = [

        search_documents,

        get_document_metadata,

        list_documents,

    ]

    # Create LLM

    llm = get_llm(
        temperature=0.0
    )

    llm_with_tools = (
        llm.bind_tools(
            tools
        )
    )


    # ======================================
    # Agent Node
    # ======================================

    def agent_node(
        state: AskDocState,
    ) -> dict[str, Any]:

        system_message = SystemMessage(
            content="""
You are AskDoc, an AI assistant that answers
questions using official company documents.

IMPORTANT RULES:

1. For questions about company policies,
   rules, procedures, benefits, security,
   remote work, leave, or company information,
   use search_documents before answering.

2. Do not answer company-document questions
   from your own knowledge.

3. If search_documents does not contain the
   answer, say exactly:

   "I don't know based on the available
   company documents."

4. Use get_document_metadata when the user
   asks which document contains information
   or asks about document metadata.

5. Use list_documents when the user asks
   what documents are available.

6. Never invent company information.

7. Keep answers concise and professional.

8. When document search results contain
   source names, cite those sources clearly.

"""
        )

        response = (
            llm_with_tools.invoke(
                [system_message]
                + state["messages"]
            )
        )

        generation = ""

        if (
            isinstance(
                response.content,
                str,
            )
        ):

            generation = (
                redact_pii(
                    response.content
                )
            )

        return {

            "messages": [
                response
            ],

            "generation":
                generation,

        }


    # ======================================
    # Routing
    # ======================================

    def route_after_safety(
        state: AskDocState,
    ):

        if state.get(
            "is_safe",
            False,
        ):

            return "agent"

        return END


    def should_continue(
        state: AskDocState,
    ):

        last_message = (
            state["messages"][-1]
        )

        if (
            isinstance(
                last_message,
                AIMessage,
            )
            and last_message.tool_calls
        ):

            return "tools"

        return END


    # ======================================
    # Build Graph
    # ======================================

    builder = StateGraph(
        AskDocState
    )

    tool_node = ToolNode(
        tools
    )

    builder.add_node(
        "safety_guardrail",
        safety_guardrail_node,
    )

    builder.add_node(
        "agent",
        agent_node,
    )

    builder.add_node(
        "tools",
        tool_node,
    )


    builder.add_edge(
        START,
        "safety_guardrail",
    )


    builder.add_conditional_edges(
        "safety_guardrail",

        route_after_safety,

        {
            "agent": "agent",

            END: END,
        },
    )


    builder.add_conditional_edges(
        "agent",

        should_continue,

        {
            "tools": "tools",

            END: END,
        },
    )


    builder.add_edge(
        "tools",
        "agent",
    )


    # ======================================
    # Memory
    # ======================================

    memory = MemorySaver()


    graph = builder.compile(
        checkpointer=memory
    )


    return graph