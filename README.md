# Bookly Customer Support Agent

An AI-powered customer support agent for a fictional online bookstore, built with the Anthropic Python SDK. The agent handles order lookups, returns, shipping questions, policy inquiries, and password resets via Claude's tool use feature.

**Live demo:** [web-production-6ea4d.up.railway.app](https://web-production-6ea4d.up.railway.app/)

## How it works

The agent runs a manual agentic loop: each user message is sent to `claude-opus-4-8` with six tool definitions. If Claude decides to call a tool, the result is fed back into the conversation and the request is retried — repeating until Claude returns a plain text response (`stop_reason == "end_turn"`). Conversation history is stored in memory per session.

```
Customer → FastAPI → CustomerSupportAgent → Claude Opus 4.8
                              ↑                      ↓
                              └── tool results ←── tool_use
```

## Try it

Open the live site and click the gold chat button in the bottom-right corner:

**[https://web-production-6ea4d.up.railway.app/](https://web-production-6ea4d.up.railway.app/)**

Things to ask:
- *"What's the status of order ORD-1002?"*
- *"I'd like to return ORD-1001 — wrong item."*
- *"What are your shipping rates to Canada?"*
- *"Can you reset the password for alice@example.com?"*
  

### Agent Inspector

A real-time debug panel (visible on desktop, ≥1080px) that shows exactly what the agent is doing on every turn — similar to Salesforce Agentforce's debug view. For each message it displays the classified **topic**, the **scoping instruction** from the system prompt that governed the response, and each **tool call** made — numbered, with its description, inputs, and raw result. Token usage (input / output) is shown per turn. The full system prompt is always visible at the top. Click ⤢ in the chat header to expand both panels.

## Demo script

### 1. Order lookup
```
You: what's the status of order ORD-1001?
```
Inspector: **Topic → Order Management** · `get_order_status()` fires with `order_id: "ORD-1001"` · result shows two books, status, tracking number, and delivery date.

### 2. Return request
```
You: I want to return it
```
The agent confirms before acting (the scoping instruction says so). Reply `yes` and `request_return()` fires — a return ID is created live.

### 3. Vague question
```
You: where is my order?
```
No order ID given — Claude asks for one, no tool runs. The inspector still shows **Order Management** (classified from message keywords, not tool calls).

### 4. Policy question
```
You: what's your return policy?
```
Topic switches to **Policy** · `get_policy()` fires · the agent quotes the policy verbatim from the data store. Never guesses.

### 5. Out of scope
```
You: can you recommend a book?
```
**Topic → General Inquiry** · no actions · the agent politely declines. The system prompt guardrail holds.

---

The mock database includes two customers and three orders:

| Customer | Email | Orders |
|----------|-------|--------|
| Alice Johnson | alice@example.com | ORD-1001 (delivered), ORD-1002 (in transit) |
| Bob Smith | bob@example.com | ORD-1003 (processing) |

## Running locally

### Prerequisites

- Python 3.11+
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

### Setup

```bash
cd customer_support

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Web server

```bash
uvicorn api:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

### Terminal CLI

```bash
python3 cli.py
```

Commands: `/reset` to clear history, `/quit` to exit.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/sessions` | Create a new chat session → returns `session_id` |
| `POST` | `/chat` | Send a message: `{"session_id": "...", "message": "..."}` |
| `POST` | `/sessions/{id}/reset` | Clear conversation history for a session |
| `DELETE` | `/sessions/{id}` | Delete a session |
| `GET` | `/sessions` | List active sessions |

API docs (local): [http://localhost:8000/docs](http://localhost:8000/docs)

## Available tools

| Tool | What it does |
|------|-------------|
| `get_order_status` | Look up an order by ID (e.g. `ORD-1001`) |
| `list_customer_orders` | List all orders for an email address |
| `request_return` | Submit a return/refund for a delivered order |
| `get_shipping_info` | Shipping options and rates for a destination |
| `get_policy` | Return, shipping, warranty, payment, or privacy policy |
| `reset_password` | Send a password reset email |

## Project structure

```
customer_support/
├── agent.py        # CustomerSupportAgent — the agentic loop
├── tools.py        # Tool schemas + implementations
├── mock_data.py    # In-memory mock database
├── api.py          # FastAPI server + session management
├── cli.py          # Terminal chat interface
├── demo.py         # Scripted demo conversation (local only)
├── static/
│   └── index.html  # Bookstore UI with chat widget
└── requirements.txt
```
