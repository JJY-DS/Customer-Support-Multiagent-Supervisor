"""Billing tools + the manager-escalation flag tool."""
import json
import uuid

from langchain_core.tools import tool

from data.loader import CUSTOMER_ORDERS


@tool
def check_billing_status(customer_id: str) -> str:
    """Check recent billing and payment information for a customer.
    Returns summary of recent orders and their payment status.
    """
    if customer_id not in CUSTOMER_ORDERS:
        return f"No billing records found for customer {customer_id}."

    recent_orders = sorted(CUSTOMER_ORDERS[customer_id], key=lambda o: o["order_date"], reverse=True)[:5]
    billing_records = [{
        "order_id": order["order_id"],
        "order_date": order["order_date"][:10],
        "total": order["total"],
        "status": order["status"],
        "payment_status": "charged" if order["status"] != "cancelled" else "refunded",
    } for order in recent_orders]

    return json.dumps({
        "customer_id": customer_id,
        "recent_billing": billing_records,
        "total_recent_charges": round(sum(r["total"] for r in billing_records if r["payment_status"] == "charged"), 2),
    }, indent=2)


@tool
def escalate_to_manager(reason: str) -> str:
    """Flag a ticket for escalation to a human support manager.
    Use when the issue is beyond automated handling capabilities.
    """
    # Separate from the graph-level HITL node: an agent can call this mid-conversation
    # to flag something, while the HITL node is what actually pauses the graph.
    return json.dumps({
        "escalation_id": f"ESC-{uuid.uuid4().hex[:8].upper()}",
        "status": "escalated",
        "reason": reason,
        "message": "Ticket has been flagged for human manager review. Expected response within 2 hours.",
    }, indent=2)
