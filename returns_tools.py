"""
Returns tools. Business rules (return windows, refund amounts) are encoded in
plain Python so the LLM can't hallucinate a wrong answer about money.
"""
import json
from datetime import datetime

from langchain_core.tools import tool

from data.loader import ORDERS_DB, PRODUCTS_DB

DEFECT_KEYWORDS = ["defective", "damaged", "broken", "wrong item", "incorrect", "buzzing", "not working", "stopped working"]


@tool
def check_return_eligibility(order_id: str) -> str:
    """Check if an order is eligible for return based on ShopSmart's return policy.
    Standard items: 30 days from delivery. Electronics: 15 days.
    """
    if order_id not in ORDERS_DB:
        return f"Error: Order {order_id} not found."
    order = ORDERS_DB[order_id]

    if order["status"] != "delivered":
        return json.dumps({
            "order_id": order_id,
            "eligible": False,
            "reason": f"Order status is '{order['status']}'. Must be 'delivered' to process a return.",
        })

    # estimated_delivery is used as a proxy for the actual delivery date
    delivery_date = datetime.fromisoformat(order["estimated_delivery"])
    days_since_delivery = (datetime.now() - delivery_date).days

    has_electronics = any(
        PRODUCTS_DB.get(item.get("product_id", ""), {}).get("category") == "Electronics"
        for item in order["items"]
    )
    return_window = 15 if has_electronics else 30
    eligible = days_since_delivery <= return_window

    return json.dumps({
        "order_id": order_id,
        "eligible": eligible,
        "days_since_delivery": days_since_delivery,
        "return_window_days": return_window,
        "contains_electronics": has_electronics,
        "reason": "Within return window" if eligible
        else f"Return window of {return_window} days has expired ({days_since_delivery} days since delivery)",
    }, indent=2)


@tool
def calculate_refund(order_id: str, reason: str) -> str:
    """Calculate the refund amount for an order based on the return reason.
    Defective items get full refund including shipping. Other returns exclude shipping.
    """
    if order_id not in ORDERS_DB:
        return f"Error: Order {order_id} not found."
    total = ORDERS_DB[order_id]["total"]
    is_defective = any(word in reason.lower() for word in DEFECT_KEYWORDS)

    if is_defective:
        refund_amount, refund_type = total, "full (defective/damaged item)"
    else:
        shipping_cost = 0.0 if total > 50 else 5.99
        refund_amount, refund_type = total - shipping_cost, "partial (shipping costs excluded)"

    return json.dumps({
        "order_id": order_id,
        "order_total": total,
        "refund_amount": round(refund_amount, 2),
        "refund_type": refund_type,
        "reason": reason,
        "processing_time": "5-7 business days",
    }, indent=2)
