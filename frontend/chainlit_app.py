import chainlit as cl
import httpx


API_URL = "http://localhost:8000"


@cl.on_chat_start
async def on_chat_start():

    # Store the thread ID for this Chainlit conversation.
    # It will be created by your FastAPI backend on the first message.
    cl.user_session.set(
        "thread_id",
        None,
    )

    await cl.Message(
        content=(
            "👋 **Welcome to AskDoc!**\n\n"
            "Ask me anything about your documents."
        )
    ).send()


@cl.on_message
async def on_message(
    message: cl.Message,
):

    thread_id = cl.user_session.get(
        "thread_id"
    )

    payload = {
        "message": message.content,
        "thread_id": thread_id,
    }

    try:

        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{API_URL}/chat",
                json=payload,
                timeout=35.0,
            )

            response.raise_for_status()

            data = response.json()


    except httpx.TimeoutException:

        await cl.Message(
            content=(
                "⏳ The request took too long. "
                "Please try again."
            )
        ).send()

        return


    except httpx.HTTPStatusError as error:

        await cl.Message(
            content=(
                f"❌ API error: "
                f"{error.response.status_code}"
            )
        ).send()

        return


    except httpx.RequestError:

        await cl.Message(
            content=(
                "❌ Could not connect to the AskDoc API."
            )
        ).send()

        return


    # Save the thread ID returned by FastAPI.
    # This keeps conversation memory between messages.
    cl.user_session.set(
        "thread_id",
        data["thread_id"],
    )


    answer = data.get(
        "response",
        "I couldn't generate a response.",
    )


    sources = data.get(
        "sources",
        [],
    )


    escalated = data.get(
        "escalated",
        False,
    )


    # Build the final response.
    content = answer


    if sources:

        content += "\n\n### 📚 Sources\n"

        for source in sources:

            content += f"- {source}\n"


    if escalated:

        content += (
            "\n\n⚠️ **This question has been escalated "
            "for additional review.**"
        )


    await cl.Message(
        content=content,
    ).send()