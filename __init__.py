"""Tool registry -- the 10 tools available to the specialist agents."""
from tools.billing_tools import check_billing_status, escalate_to_manager
from tools.order_tools import lookup_customer, lookup_order, search_orders_by_customer
from tools.policy_lookup import policy_lookup
from tools.product_tools import lookup_product, search_products
from tools.returns_tools import calculate_refund, check_return_eligibility

ALL_TOOLS = [
    lookup_customer, lookup_order, search_orders_by_customer,
    check_return_eligibility, lookup_product, search_products,
    policy_lookup, calculate_refund, check_billing_status, escalate_to_manager,
]
