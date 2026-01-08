from database.vector_db import init_vector_db

print("="*70)
print("REGENERATING VECTOR DATABASE WITH NEW PRODUCTS")
print("="*70)

init_vector_db()

print("\n✅ Vector database regenerated with 20 products!")
print("="*70)