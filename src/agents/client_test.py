import os
import traceback
from typing import Any
from uuid import uuid4

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    SendMessageResponse,
    GetTaskResponse,
    SendMessageSuccessResponse,
    Task,
    TaskState,
    SendMessageRequest,
    MessageSendParams,
    GetTaskRequest,
    TaskQueryParams,
)
import httpx

AGENT_URL = os.getenv("AGENT_URL", "http://localhost:10000")


def create_send_message_payload(
        text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """Helper function to create the payload for sending a message."""
    payload: dict[str, Any] = {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": text}],
            "messageId": uuid4().hex,
        },
    }

    if task_id:
        payload["message"]["taskId"] = task_id

    if context_id:
        payload["message"]["contextId"] = context_id
    return payload


def print_json_response(response: Any, description: str) -> None:
    """Helper function to print the JSON representation of a response."""
    print(f"--- {description} ---")
    if hasattr(response, "root"):
        print(f"{response.root.model_dump_json(exclude_none=True)}\n")
    else:
        print(f"{response.model_dump(mode='json', exclude_none=True)}\n")


async def run_single_turn_test(client: A2AClient) -> None:
    """Runs a single-turn non-streaming test for the BugFixer agent."""

    prompt = (
        "Analyse l'échec du build pour :\n"
        "- Job: springboot-user-service\n"
        "- Build: 42\n"
        "- Commit: 5e74bcd7995c1e8dba8c6be0ef2c329b99ada436"
    )
    send_message_payload = create_send_message_payload(text=prompt)
    request = SendMessageRequest(
        id=str(uuid4()), params=MessageSendParams(**send_message_payload)
    )

    print("--- ✉️  Single Turn Request ---")
    # Send Message
    response: SendMessageResponse = await client.send_message(request)
    print_json_response(response, "📥 Single Turn Request Response")
    if not isinstance(response.root, SendMessageSuccessResponse):
        print("received non-success response. Aborting get task ")
        return

    if not isinstance(response.root.result, Task):
        print("received non-task response. Aborting get task ")
        return

    task_id: str = response.root.result.id
    print("--- ❔ Query Task ---")
    # query the task
    get_request = GetTaskRequest(id=str(uuid4()), params=TaskQueryParams(id=task_id))
    get_response: GetTaskResponse = await client.get_task(get_request)
    print_json_response(get_response, "📥 Query Task Response")


async def main() -> None:
    """Main function to run the tests."""
    print(f"--- 🔄 Connecting to agent at {AGENT_URL}... ---")
    try:
        async with httpx.AsyncClient() as httpx_client:
            # Create a resolver to fetch the agent card
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=AGENT_URL,
            )
            agent_card = await resolver.get_agent_card()
            # Create a client to interact with the agent
            client = A2AClient(
                httpx_client=httpx_client,
                agent_card=agent_card,
            )
            print("--- ✅ Connection successful. ---")

            await run_single_turn_test(client)

    except Exception as e:
        traceback.print_exc()
        print(f"--- ❌ An error occurred: {e} ---")
        print("Ensure the agent server is running.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())