import os
import anthropic
from tools import TOOL_SCHEMAS, execute_tool


def _load_api_key() -> str:
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are a friendly and knowledgeable customer support agent for Bookly, a cozy online bookstore.

You help customers with:
- Order status and tracking
- Return and refund requests
- Shipping questions and options
- Policy questions (returns, shipping, membership, payment, privacy)
- Password resets

Guidelines:
- Always use the available tools to look up accurate information. Never invent order details, tracking numbers, or policies.
- When asked about an order, use get_order_status or list_customer_orders.
- Before submitting a return with request_return, confirm the customer wants to proceed.
- If an order can't be found, ask the customer to verify the order ID or email address.
- Be warm and bookish in tone — mention book titles naturally when referencing orders.
- Keep responses concise and helpful. Empathize when customers are frustrated.
- If a request is outside your capabilities, politely say so.
"""


class CustomerSupportAgent:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic(
            api_key=_load_api_key(),
            base_url="https://api.anthropic.com",
        )
        self.messages: list[dict] = []

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        while True:
            response = self.client.messages.create(
                model="claude-opus-4-8",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=self.messages,
            )

            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                return next(
                    (block.text for block in response.content if block.type == "text"), ""
                )

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )

            if not tool_results:
                break

            self.messages.append({"role": "user", "content": tool_results})

        return ""

    def reset(self) -> None:
        self.messages = []
