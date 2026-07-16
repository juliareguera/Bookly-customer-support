import json
from mock_data import CUSTOMERS, ORDERS, RETURNS, POLICIES, PASSWORD_RESET_SENT

# ── Tool schemas (passed to Claude) ────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "get_order_status",
        "description": (
            "Look up the status and details of a specific order by order ID. "
            "Use this to answer questions like 'where is my order?' or 'what is the status of ORD-1001?'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID, e.g. ORD-1001"},
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "list_customer_orders",
        "description": "List all orders associated with a customer's email address.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer's email address"},
            },
            "required": ["email"],
        },
    },
    {
        "name": "request_return",
        "description": (
            "Submit a return or refund request for a delivered order. "
            "Only call this after confirming the customer wants to proceed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID to return"},
                "reason": {
                    "type": "string",
                    "description": "Reason for the return, e.g. 'defective product', 'wrong item shipped', 'changed mind'",
                },
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "get_shipping_info",
        "description": "Get available shipping options, rates, and estimated delivery times for a destination.",
        "input_schema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Destination country or region, e.g. 'US', 'Canada', 'international'",
                },
            },
            "required": ["destination"],
        },
    },
    {
        "name": "get_policy",
        "description": "Retrieve company policy information on a specific topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "enum": ["returns", "shipping", "warranty", "payment", "privacy"],
                    "description": "Policy topic to retrieve",
                },
            },
            "required": ["topic"],
        },
    },
    {
        "name": "reset_password",
        "description": "Send a password reset email to a customer. Always call this when a customer asks to reset their password.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer's email address"},
            },
            "required": ["email"],
        },
    },
]


# ── Tool implementations ────────────────────────────────────────────────────

def get_order_status(order_id: str) -> str:
    order = ORDERS.get(order_id.upper())
    if not order:
        return json.dumps({"error": f"Order '{order_id}' not found. Please double-check the order ID."})

    result: dict = {
        "order_id": order_id.upper(),
        "status": order["status"],
        "items": order["items"],
        "total": order["total"],
        "placed_date": order["placed_date"],
    }
    if order["status"] == "delivered":
        result["delivered_date"] = order.get("delivered_date")
        result["tracking"] = order.get("tracking")
    elif order["status"] == "in_transit":
        result["estimated_delivery"] = order.get("estimated_delivery")
        result["tracking"] = order.get("tracking")

    if order.get("return_requested"):
        result["return_status"] = order.get("return_status")

    return json.dumps(result)


def list_customer_orders(email: str) -> str:
    match = next(
        ((cid, c) for cid, c in CUSTOMERS.items() if c["email"].lower() == email.lower()),
        None,
    )
    if not match:
        return json.dumps({"error": f"No customer found with email '{email}'."})

    customer_id, customer = match
    orders = [
        {
            "order_id": oid,
            "status": o["status"],
            "total": o["total"],
            "placed_date": o["placed_date"],
            "items": [i["name"] for i in o["items"]],
        }
        for oid, o in ORDERS.items()
        if o["customer_id"] == customer_id
    ]
    return json.dumps({"customer": customer["name"], "order_count": len(orders), "orders": orders})


def request_return(order_id: str, reason: str) -> str:
    key = order_id.upper()
    order = ORDERS.get(key)
    if not order:
        return json.dumps({"error": f"Order '{order_id}' not found."})
    if order["status"] != "delivered":
        return json.dumps({
            "error": f"Order {key} cannot be returned because its status is '{order['status']}'. "
                     "Only delivered orders are eligible for returns."
        })
    if order.get("return_requested"):
        return json.dumps({
            "message": f"A return for order {key} is already in progress.",
            "return_status": order.get("return_status"),
        })

    return_id = f"RET-{key}"
    ORDERS[key]["return_requested"] = True
    ORDERS[key]["return_status"] = "approved"
    RETURNS[return_id] = {"order_id": key, "reason": reason, "status": "approved"}

    return json.dumps({
        "success": True,
        "return_id": return_id,
        "message": (
            f"Return approved for order {key}. "
            "A prepaid shipping label will be emailed within 24 hours. "
            "Refunds are processed 5-7 business days after we receive the item."
        ),
    })


def get_shipping_info(destination: str) -> str:
    is_domestic = destination.lower() in {"us", "usa", "united states", "domestic"}
    if is_domestic:
        options = [
            {"service": "Standard (5-7 business days)", "cost": "Free on orders $50+, else $4.99"},
            {"service": "Express (2-3 business days)", "cost": "$12.99"},
            {"service": "Overnight (1 business day)", "cost": "$24.99"},
        ]
    else:
        options = [
            {"service": "International Standard (7-14 business days)", "cost": "From $19.99"},
            {"service": "International Express (3-5 business days)", "cost": "From $39.99"},
        ]
    return json.dumps({"destination": destination, "options": options})


def get_policy(topic: str) -> str:
    text = POLICIES.get(topic.lower())
    if not text:
        return json.dumps({
            "error": f"No policy found for '{topic}'.",
            "available_topics": list(POLICIES.keys()),
        })
    return json.dumps({"topic": topic, "policy": text})


def reset_password(email: str) -> str:
    # Security best practice: never reveal whether the email exists
    if email.lower() not in PASSWORD_RESET_SENT:
        PASSWORD_RESET_SENT.add(email.lower())
        # In a real app this would send an email; here we just log it
        print(f"[MOCK] Password reset email dispatched → {email}")
    return json.dumps({
        "success": True,
        "message": (
            f"If an account exists for {email}, a password reset link has been sent. "
            "Please check your inbox and spam folder. The link expires in 1 hour."
        ),
    })


# ── Dispatcher ──────────────────────────────────────────────────────────────

_DISPATCH = {
    "get_order_status": get_order_status,
    "list_customer_orders": list_customer_orders,
    "request_return": request_return,
    "get_shipping_info": get_shipping_info,
    "get_policy": get_policy,
    "reset_password": reset_password,
}


def execute_tool(name: str, tool_input: dict) -> str:
    fn = _DISPATCH.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: '{name}'"})
    try:
        return fn(**tool_input)
    except TypeError as e:
        return json.dumps({"error": f"Invalid arguments for tool '{name}': {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
