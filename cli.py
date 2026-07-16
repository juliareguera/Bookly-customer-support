"""
Interactive CLI for the Customer Support Agent.

Usage:
    python3 cli.py

Commands during chat:
    /reset  — clear conversation history
    /quit   — exit
"""

import textwrap
from agent import CustomerSupportAgent

WRAP_WIDTH = 80


def print_agent(text: str) -> None:
    prefix = "Agent: "
    wrapped = textwrap.fill(text, width=WRAP_WIDTH, subsequent_indent=" " * len(prefix))
    print(f"\n{prefix}{wrapped}")


def main() -> None:
    print("=" * WRAP_WIDTH)
    print(" Customer Support Agent")
    print("=" * WRAP_WIDTH)
    print(" Commands:  /reset — clear conversation   /quit — exit")
    print("=" * WRAP_WIDTH)

    agent = CustomerSupportAgent()
    print_agent("Hello! How can I help you today?")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("Goodbye!")
            break

        if user_input.lower() == "/reset":
            agent.reset()
            print("\nConversation cleared.")
            print_agent("Conversation reset. How can I help you?")
            continue

        response = agent.chat(user_input)
        print_agent(response)


if __name__ == "__main__":
    main()
