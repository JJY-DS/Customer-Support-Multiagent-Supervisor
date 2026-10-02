"""Order & customer lookup tools (used by the order, returns and billing specialists)."""
import json

from langchain_core.tools import tool

from data.loader import CUSTOMER_ORDERS, CUSTOMERS_DB, ORDERS_DB


@tool
def lookup_customer(customer_id: str) -> str:
    """Look up customer information by customer ID.
    Returns customer tier, join date, and ticket history.
    """
    if customer_id not in CUSTOMERS_DB:
        return f"Error: Customer {customer_id} not found in database."
    customer = CUSTOMERS_DB[customer_id]
    return json.dumps({
        "customer_id": customer["customer_id"],
        "name": "[REDACTED]",  # agents only need the tier, never the identity
        "tier": customer["tier"],
        "join_date": customer["join_date"],
        "past_tickets_count": customer["past_tickets_count"],
        "last_contact_date": customer["last_contact_date"],
    }, indent=2)


@tool
def lookup_order(order_id: str) -> str:
    """Look up a specific order by order ID.
    Returns order status, items, total, tracking number, and estimated delivery.
    """
    if order_id not in ORDERS_DB:
        return f"Error: Order {order_id} not found in database."
    order = ORDERS_DB[order_id]
    return json.dumps({
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "order_date": order["order_date"],
        "items": [{"name": i["name"], "quantity": i["quantity"], "price": i["price"]} for i in order["items"]],
        "total": order["total"],
        "status": order["status"],
        "tracking_number": order["tracking_number"],
        "estimated_delivery": order["estimated_delivery"],
    }, indent=2)


@tool
def search_orders_by_customer(customer_id: str) -> str:
    """Find all orders for a given customer.
    Returns a summary list of all their orders with status.
    """
    if customer_id not in CUSTOMER_ORDERS:
        return f"No orders found for customer {customer_id}."
    summary = [{
        "order_id": order["order_id"],
        "order_date": order["order_date"][:10],
        "total": order["total"],
        "status": order["status"],
        "items_count": len(order["items"]),
    } for order in CUSTOMER_ORDERS[customer_id]]
    return json.dumps({"customer_id": customer_id, "order_count": len(summary), "orders": summary}, indent=2)


ORDER_TOOLS = [lookup_order, search_orders_by_customer, lookup_customer]
