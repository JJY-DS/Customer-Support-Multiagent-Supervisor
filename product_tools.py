"""Product catalogue tools (used by the product specialist)."""
import json

from langchain_core.tools import tool

from data.loader import PRODUCTS_DB


@tool
def lookup_product(product_id: str) -> str:
    """Look up detailed product information by product ID.
    Returns name, category, price, stock status, specs, and FAQ.
    """
    if product_id not in PRODUCTS_DB:
        return f"Error: Product {product_id} not found."
    return json.dumps(PRODUCTS_DB[product_id], indent=2)


def _normalise(text: str) -> str:
    return text.lower().replace("-", " ").strip()


@tool
def search_products(query: str) -> str:
    """Search products by name or category. Case-insensitive partial matching.
    Use this when the customer asks about a product by name.
    """
    # Hyphen-insensitive, so "self help" matches "Self-Help Guide"
    query_norm = _normalise(query)
    results = [{
        "product_id": p["product_id"],
        "name": p["name"],
        "category": p["category"],
        "price": p["price"],
        "stock_status": p["stock_status"],
    } for p in PRODUCTS_DB.values()
        if query_norm in _normalise(p["name"]) or query_norm in _normalise(p["category"])]

    if not results:
        return f"No products found matching '{query}'."
    return json.dumps({"query": query, "results_count": len(results), "results": results}, indent=2)
