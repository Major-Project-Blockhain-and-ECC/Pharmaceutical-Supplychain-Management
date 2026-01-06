"""
Test Product and Status Sync
"""

from database import get_database
from contract import contract
import json

print("="*70)
print("🧪 Testing Product and Status Sync")
print("="*70 + "\n")

db = get_database()

# ===========================
# TEST 1: Check Blockchain Products
# ===========================
print("Test 1: Checking Blockchain Products...")
print("-"*70)

blockchain_products = []
for i in range(100):
    try:
        product = contract.functions.products(i).call()
        if product[1]:  # name field
            blockchain_products.append({
                "productId": product[0],
                "name": product[1],
                "description": product[2],
                "minTemp": product[3],
                "maxTemp": product[4],
                "minHumidity": product[5],
                "maxHumidity": product[6],
                "quantity": product[7],
                "mfgDate": product[8],
                "timestamp": product[9],
                "currentOwner": product[10],
                "isSpoiled": product[11]
            })
    except Exception as e:
        break

print(f"Found {len(blockchain_products)} products in blockchain")
if blockchain_products:
    for p in blockchain_products:
        print(f"  - {p['name']} (ID: {p['productId']}, Qty: {p['quantity']}, Temp: {p['minTemp']}°C to {p['maxTemp']}°C)")
else:
    print("  ℹ️  No products in blockchain yet")

# ===========================
# TEST 2: Check MongoDB Products
# ===========================
print("\nTest 2: Checking MongoDB Products...")
print("-"*70)

mongo_products = list(db.products.find())
print(f"Found {len(mongo_products)} products in MongoDB")
if mongo_products:
    for p in mongo_products:
        print(f"  - {p.get('name', 'Unknown')} (ID: {p.get('productId', '?')}, Qty: {p.get('quantity', '?')})")
else:
    print("  ℹ️  No products in MongoDB yet")

# ===========================
# TEST 3: Check Product Sync Status
# ===========================
print("\nTest 3: Product Sync Status...")
print("-"*70)

blockchain_product_ids = {p['productId'] for p in blockchain_products}
mongo_product_ids = {p.get('productId') for p in mongo_products if 'productId' in p}

if blockchain_product_ids == mongo_product_ids:
    print("✅ Products are synchronized!")
else:
    print("⚠️  Products out of sync!")
    missing_in_mongo = blockchain_product_ids - mongo_product_ids
    if missing_in_mongo:
        print(f"  Missing in MongoDB: {missing_in_mongo}")
    extra_in_mongo = mongo_product_ids - blockchain_product_ids
    if extra_in_mongo:
        print(f"  Extra in MongoDB: {extra_in_mongo}")

# ===========================
# TEST 4: Check Product History (Status Updates)
# ===========================
print("\nTest 4: Checking Product Status History...")
print("-"*70)

if blockchain_products:
    for product in blockchain_products[:3]:  # Check first 3 products
        product_id = product['productId']
        try:
            history = contract.functions.getProductHistory(product_id).call()
            print(f"\nProduct ID {product_id} ({product['name']}):")
            print(f"  Blockchain history entries: {len(history)}")
            
            if history:
                for idx, status in enumerate(history, 1):
                    print(f"    {idx}. Location: {status[0]}, Temp: {status[1]}, Humidity: {status[2]}, Qty: {status[6]}")
            
            # Check MongoDB status
            mongo_status = list(db.status.find({"productId": product_id}))
            print(f"  MongoDB status entries: {len(mongo_status)}")
            
        except Exception as e:
            print(f"  Error checking product {product_id}: {e}")
else:
    print("  ℹ️  No products to check history")

# ===========================
# TEST 5: Check MongoDB Status Collection
# ===========================
print("\nTest 5: Checking MongoDB Status Collection...")
print("-"*70)

mongo_statuses = list(db.status.find())
print(f"Found {len(mongo_statuses)} status entries in MongoDB")

if mongo_statuses:
    for status in mongo_statuses[:5]:  # Show first 5
        print(f"  - Product {status.get('productId', '?')}: {status.get('location', '?')} @ {status.get('temperature', '?')}°C")
else:
    print("  ℹ️  No status entries in MongoDB yet")

# ===========================
# TEST 6: Run Auto-Sync
# ===========================
print("\nTest 6: Running Auto-Sync...")
print("-"*70)

from auto_sync import auto_sync_all

sync_results = auto_sync_all(silent=False)

print(f"\nSync Results:")
print(f"  Workers synced: {sync_results['workers_synced']}")
print(f"  Products synced: {sync_results['products_synced']}")
if sync_results['errors']:
    print(f"  Errors: {sync_results['errors']}")

# ===========================
# FINAL SUMMARY
# ===========================
print("\n" + "="*70)
print("📊 FINAL STATUS:")
print("="*70)

print(f"Blockchain: {len(blockchain_products)} products")
print(f"MongoDB:    {db.products.count_documents({})} products")
print(f"Status:     {db.status.count_documents({})} entries")

if len(blockchain_products) == db.products.count_documents({}):
    print("\n✅ Products are synchronized!")
else:
    print("\n⚠️  Products need synchronization")
    print("Run: python sync_databases.py")

print("\n💡 To test product addition:")
print("1. Add a product via frontend or API")
print("2. Check sync status: curl http://localhost:8000/sync/status")
print("3. Manual sync if needed: curl -X POST http://localhost:8000/sync")
print("="*70)
