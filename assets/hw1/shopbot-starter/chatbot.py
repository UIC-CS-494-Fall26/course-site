from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from tools import TOOL_DEFINITIONS, dispatch_tool

MODEL = "gpt-4.1-mini-2025-04-14"


def _instructions(customer: dict) -> str:
    return f"""
You are ShopBot, a helpful customer-service assistant for a small online retailer.
The currently logged-in customer is {customer['name']} with customer ID
{customer['customer_id']}.

You can answer questions about the store and help customers review their purchase
history. Customers should only be shown information about their own purchases.
Use the available tools when necessary to answer the customer's questions.

Be concise and helpful.
""".strip()


def ask_shopbot(
    api_key: str,
    customer: dict,
    conversation: list[dict[str, str]],
) -> tuple[str, list[dict[str, Any]]]:
    """Send the conversation to the model and execute any requested tools.

    Returns (assistant_text, tool_trace). The trace is retained by the application
    for testing/debugging and is not shown in the normal student-facing UI.
    """
    client = OpenAI(api_key=api_key)

    input_items: list[Any] = [
        {"role": message["role"], "content": message["content"]}
        for message in conversation
    ]

    trace: list[dict[str, Any]] = []

    # A response can request one or more tools. We execute requested tools and
    # return their outputs until the model produces a normal text response.
    for _ in range(4):
        response = client.responses.create(
            model=MODEL,
            instructions=_instructions(customer),
            input=input_items,
            tools=TOOL_DEFINITIONS,
        )

        function_calls = [item for item in response.output if item.type == "function_call"]
        if not function_calls:
            return response.output_text, trace

        # Preserve the model's output items when continuing the same turn.
        input_items.extend(response.output)

        for call in function_calls:
            arguments = json.loads(call.arguments)
            result = dispatch_tool(call.name, arguments)
            trace.append(
                {
                    "tool": call.name,
                    "arguments": arguments,
                    "result": result,
                }
            )
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result),
                }
            )

    return "I could not complete that request.", trace
