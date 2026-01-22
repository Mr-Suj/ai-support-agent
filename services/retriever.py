from database.sql_db import get_user_orders, get_order_by_tracking, get_recent_order_products
from database.vector_db import search_products, get_product_by_id, search_products_by_ids


def retrieve_order_details(query: str, entities: dict, user_email: str = "john@example.com") -> dict:
    tracking_number = entities.get("tracking_number")

    if tracking_number:
        order = get_order_by_tracking(tracking_number)

        if not order:
            return {
                "data_source": "SQL",
                "results": [],
                "context": f"No order found with tracking number {tracking_number}"
            }

        context = f"""
Order Details:
- Order ID: {order.id}
- Status: {order.status}
- Order Date: {order.order_date.strftime('%Y-%m-%d')}
- Total Amount: ${order.total_amount}
- Tracking Number: {order.tracking_number}

Items in this order:
"""

        for item in order.items:
            context += f"- {item.product_name} (Quantity: {item.quantity}, Price: ${item.price})\n"

        return {
            "data_source": "SQL",
            "results": [order],
            "context": context.strip()
        }

    orders = get_user_orders(user_email)

    if not orders:
        return {
            "data_source": "SQL",
            "results": [],
            "context": f"No orders found for {user_email}"
        }

    context = f"Orders for {user_email}:\n\n"

    for order in orders:
        context += f"""
Order #{order.id}:
- Status: {order.status}
- Date: {order.order_date.strftime('%Y-%m-%d')}
- Total: ${order.total_amount}
- Tracking: {order.tracking_number}
- Items: {', '.join([item.product_name for item in order.items])}
"""

    return {
        "data_source": "SQL",
        "results": orders,
        "context": context.strip()
    }


def retrieve_product_details(query: str, entities: dict) -> dict:
    results = search_products(query, top_k=3)

    if not results:
        return {
            "data_source": "VECTOR",
            "results": [],
            "context": "No products found matching your query."
        }

    context = "Here are the relevant products:\n\n"

    for i, result in enumerate(results, 1):
        product = result.get('product', result)
        context += f"""
Product {i}: {product.get('name')}
- Category: {product.get('category')}
- Price: ${product.get('price')}
- Description: {product.get('description')}
"""

    return {
        "data_source": "VECTOR",
        "results": results,
        "context": context.strip()
    }


def retrieve_order_product_details(query: str, entities: dict, user_email: str = "john@example.com") -> dict:
    product_ids = get_recent_order_products(user_email)

    if not product_ids:
        return {
            "data_source": "HYBRID",
            "results": {},
            "context": "No recent orders found."
        }

    products = search_products_by_ids(product_ids, query=query)

    if not products:
        return {
            "data_source": "HYBRID",
            "results": {},
            "context": "No product info found."
        }

    orders = get_user_orders(user_email)
    recent_order = orders[-1] if orders else None

    context = f"Based on your recent order:\n\n"

    if recent_order:
        context += f"""
Recent Order #{recent_order.id}:
- Date: {recent_order.order_date.strftime('%Y-%m-%d')}
- Status: {recent_order.status}
"""

    context += "\nCurrent Product Info:\n\n"

    for product in products:
        context += f"""
{product.get('name')}:
- Current Price: ${product.get('price')}
- Category: {product.get('category')}
- Description: {product.get('description')}
"""

    return {
        "data_source": "HYBRID",
        "results": {"orders": orders, "products": products},
        "context": context.strip()
    }


def retrieve(intent: str, query: str, entities: dict, user_email: str = "john@example.com") -> dict:
    if intent == "ORDER_DETAILS":
        return retrieve_order_details(query, entities, user_email)

    elif intent == "PRODUCT_DETAILS":
        return retrieve_product_details(query, entities)

    elif intent == "ORDER_PRODUCT_DETAILS":
        return retrieve_order_product_details(query, entities, user_email)

    return {
        "data_source": "UNKNOWN",
        "results": [],
        "context": "Could not understand your request."
    }
