from database.sql_db import get_user_orders, get_order_by_tracking, get_recent_order_products
from database.vector_db import search_products, get_product_by_id, search_products_by_ids


def retrieve_order_details(query: str, entities: dict, user_email: str = "john@example.com") -> dict:
    """
    Retrieve order information from SQL database.
    
    Args:
        query: Original user query
        entities: Extracted entities (tracking_number, etc.)
        user_email: User's email (in production, this comes from auth)
    
    Returns:
        {
            "data_source": "SQL",
            "results": [...],
            "context": "formatted text for LLM"
        }
    """
    
    # Check if tracking number is mentioned
    tracking_number = entities.get("tracking_number")
    
    if tracking_number:
        # Get specific order by tracking
        order = get_order_by_tracking(tracking_number)
        
        if not order:
            return {
                "data_source": "SQL",
                "results": [],
                "context": f"No order found with tracking number {tracking_number}"
            }
        
        # Format order details
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
    
    else:
        # Get all orders for user
        orders = get_user_orders(user_email)
        
        if not orders:
            return {
                "data_source": "SQL",
                "results": [],
                "context": f"No orders found for {user_email}"
            }
        
        # Format all orders
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
    """
    Retrieve product information from Vector database.
    
    Args:
        query: Original user query
        entities: Extracted entities (product_name, etc.)
    
    Returns:
        {
            "data_source": "VECTOR",
            "results": [...],
            "context": "formatted text for LLM"
        }
    """
    
    # Search products using semantic similarity
    results = search_products(query, top_k=3)
    
    if not results:
        return {
            "data_source": "VECTOR",
            "results": [],
            "context": "No products found matching your query."
        }
    
    # Format product details
    context = "Here are the relevant products:\n\n"
    
    for i, result in enumerate(results, 1):
        product = result['product']
        score = result['similarity_score']
        
        context += f"""
Product {i}: {product['name']}
- Category: {product['category']}
- Price: ${product['price']}
- Description: {product['description']}
- Key Features: {', '.join(product['features'][:5])}
- Relevance Score: {score:.2f}

"""
    
    return {
        "data_source": "VECTOR",
        "results": results,
        "context": context.strip()
    }


def retrieve_order_product_details(query: str, entities: dict, user_email: str = "john@example.com") -> dict:
    """
    HYBRID RETRIEVAL: Combine SQL + Vector DB.
    
    Used when user asks about products they previously ordered.
    
    Args:
        query: Original user query
        entities: Extracted entities
        user_email: User's email
    
    Returns:
        {
            "data_source": "HYBRID",
            "results": {...},
            "context": "formatted text for LLM"
        }
    """
    
    # Step 1: Get product IDs from recent orders (SQL)
    product_ids = get_recent_order_products(user_email)
    
    if not product_ids:
        return {
            "data_source": "HYBRID",
            "results": {},
            "context": f"No recent orders found for {user_email}. Cannot answer questions about past purchases."
        }
    
    # Step 2: Get product details from Vector DB
    products = search_products_by_ids(product_ids, query=query)
    
    if not products:
        return {
            "data_source": "HYBRID",
            "results": {},
            "context": f"Product information not found for recent orders."
        }
    
    # Step 3: Also get order details
    orders = get_user_orders(user_email)
    recent_order = orders[-1] if orders else None  # Most recent order
    
    # Format context
    context = f"Based on your recent order:\n\n"
    
    if recent_order:
        context += f"""
Your Recent Order (Order #{recent_order.id}):
- Date: {recent_order.order_date.strftime('%Y-%m-%d')}
- Status: {recent_order.status}
- Items purchased:
"""
        for item in recent_order.items:
            context += f"  - {item.product_name} (${item.price})\n"
        
        context += "\n"
    
    context += "Current Product Information:\n\n"
    
    for product in products:
        context += f"""
{product['name']}:
- Current Price: ${product['price']}
- Category: {product['category']}
- Description: {product['description']}
- Features: {', '.join(product['features'])}

"""
    
    return {
        "data_source": "HYBRID",
        "results": {
            "orders": orders,
            "products": products
        },
        "context": context.strip()
    }


def retrieve(intent: str, query: str, entities: dict, user_email: str = "john@example.com") -> dict:
    """
    Main retrieval function - routes to appropriate retriever based on intent.
    
    Args:
        intent: Classification result (ORDER_DETAILS, PRODUCT_DETAILS, ORDER_PRODUCT_DETAILS)
        query: User's original query
        entities: Extracted entities from intent classifier
        user_email: User's email (from auth in production)
    
    Returns:
        Retrieved data with context for RAG
    """
    
    if intent == "ORDER_DETAILS":
        return retrieve_order_details(query, entities, user_email)
    
    elif intent == "PRODUCT_DETAILS":
        return retrieve_product_details(query, entities)
    
    elif intent == "ORDER_PRODUCT_DETAILS":
        return retrieve_order_product_details(query, entities, user_email)
    
    else:
        # Fallback
        return {
            "data_source": "UNKNOWN",
            "results": [],
            "context": "I couldn't understand your query. Please rephrase."
        }