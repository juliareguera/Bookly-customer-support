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

TOOL_TOPIC_MAP = {
    "get_order_status": "Order Management",
    "list_customer_orders": "Order Management",
    "request_return": "Returns & Refunds",
    "get_shipping_info": "Shipping",
    "get_policy": "Policy",
    "reset_password": "Account",
}

_TOPIC_PRIORITY = ["Returns & Refunds", "Order Management", "Account", "Shipping", "Policy"]

TOPIC_SCOPING = {
    "Order Management": "Use get_order_status or list_customer_orders to look up orders. If an order can't be found, ask the customer to verify the order ID or email address.",
    "Returns & Refunds": "Before submitting a return with request_return, confirm the customer wants to proceed.",
    "Shipping": "Use get_shipping_info for accurate shipping rates and timing. Never invent delivery estimates.",
    "Policy": "Use get_policy to retrieve accurate store policies. Never invent or paraphrase policy details.",
    "Account": "Use reset_password to send a password reset email. Confirm the customer's email before proceeding.",
    "General Inquiry": "If a request is outside your capabilities, politely say so. Be warm and bookish in tone.",
}

TOOL_DESCRIPTIONS = {
    "get_order_status": "Look up order details, status, and tracking",
    "list_customer_orders": "Retrieve all orders for a customer by email",
    "request_return": "Submit a return request for a delivered order",
    "get_shipping_info": "Get shipping options, rates, and timing",
    "get_policy": "Retrieve store policies (returns, shipping, membership, payment, privacy)",
    "reset_password": "Send a password reset email to the customer",
}


class CustomerSupportAgent:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic(
            api_key=_load_api_key(),
            base_url="https://api.anthropic.com",
        )
        self.messages: list[dict] = []
        self.last_tool_calls: list[dict] = []
        self.last_topic: str = "General Inquiry"
        self.last_instructions: str = ""
        self.last_usage: dict = {}

    def chat(self, user_message: str) -> str:
        self.last_tool_calls = []
        self.last_topic = "General Inquiry"
        self.last_instructions = ""
        self.last_usage = {"input_tokens": 0, "output_tokens": 0}
        self.messages.append({"role": "user", "content": user_message})

        while True:
            response = self.client.messages.create(
                model="claude-opus-4-8",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=self.messages,
            )

            self.last_usage["input_tokens"] += response.usage.input_tokens
            self.last_usage["output_tokens"] += response.usage.output_tokens

            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                tools_called = [tc["tool"] for tc in self.last_tool_calls]
                topics_seen = {TOOL_TOPIC_MAP.get(t) for t in tools_called} - {None}
                for prio in _TOPIC_PRIORITY:
                    if prio in topics_seen:
                        self.last_topic = prio
                        break
                self.last_instructions = TOPIC_SCOPING[self.last_topic]
                return next(
                    (block.text for block in response.content if block.type == "text"), ""
                )

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    self.last_tool_calls.append({
                        "tool": block.name,
                        "description": TOOL_DESCRIPTIONS.get(block.name, ""),
                        "input": block.input,
                        "result": result,
                    })
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )

            if not tool_results:
                break

            self.messages.append({"role": "user", "content": tool_results})

        return ""

    def reset(self) -> None:
        self.messages = []
        self.last_tool_calls = []
        self.last_topic = "General Inquiry"
        self.last_instructions = ""
        self.last_usage = {}
