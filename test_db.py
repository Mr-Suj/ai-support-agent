from database.sql_db import init_db, populate_sample_data, get_user_orders, get_order_by_tracking

# Initialize database and add sample data
print("Creating database...")
init_db()

print("\nAdding sample data...")
populate_sample_data()

# Test queries
print("\n" + "="*50)
print("Testing SQL Queries")
print("="*50)

# Test 1: Get orders for a user
print("\n1️⃣ Orders for john@example.com:")
orders = get_user_orders("john@example.com")
if orders:
    for order in orders:
        print(f"   Order ID: {order.id}, Status: {order.status}, Total: ${order.total_amount}")

# Test 2: Get order by tracking number
print("\n2️⃣ Order with tracking TRACK123456:")
order = get_order_by_tracking("TRACK123456")
if order:
    print(f"   Status: {order.status}, Amount: ${order.total_amount}")
    print(f"   Items:")
    for item in order.items:
        print(f"      - {item.product_name} (${item.price})")

print("\n✅ Database test complete!")