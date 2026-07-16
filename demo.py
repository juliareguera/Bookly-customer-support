"""
Bookly support agent demo — runs through a scripted conversation
showing the main features. No web server needed.

Usage:
    python3 demo.py
"""

import time
from agent import CustomerSupportAgent

DEMO_MESSAGES = [
    "Hi! What's the status of my order ORD-1002?",
    "What's your return policy?",
    "I'd like to return order ORD-1001.",
    "Yes, please go ahead with the return. The reason is I already have a copy.",
    "Can you reset the password for alice@example.com?",
]

DIVIDER = "─" * 60


def slow_print(text: str, delay: float = 0.012) -> None:
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def main() -> None:
    print(DIVIDER)
    print("  bookly — Customer Support Agent Demo")
    print(DIVIDER)

    agent = CustomerSupportAgent()

    for message in DEMO_MESSAGES:
        print(f"\nCustomer: {message}")
        print("Agent:    ", end="", flush=True)
        response = agent.chat(message)
        slow_print(response)
        print()
        time.sleep(0.5)

    print(DIVIDER)
    print("  Demo complete.")
    print(DIVIDER)


if __name__ == "__main__":
    main()
