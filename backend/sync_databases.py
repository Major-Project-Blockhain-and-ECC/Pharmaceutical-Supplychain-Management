"""
Sync MongoDB with Blockchain Data
Syncs workers, products, and status from blockchain to MongoDB
"""

from database import get_database
from contract import contract

print("="*70)
print("🔄 Syncing MongoDB with Blockchain")
print("="*70 + "\n")

db = get_database()

# ===========================
# SYNC WORKERS
# ===========================
print("1️⃣  Syncing Workers...")
print("-"*70)

blockchain_workers = []
for i in range(100):  # Check first 100 worker IDs
    try:
        worker = contract.functions.workers(i).call()
        # Worker struct: (workerId, name, role, timestamp, account/walletAddress)
        # Check if worker exists (name not empty)
        if worker[1]:  # worker[1] = name (string)
            blockchain_workers.append({
                "workerId": worker[0],        # uint256 workerId
                "name": worker[1],            # string name
                "role": worker[2],            # WorkerType role (0=MANUFACTURER, 1=DISTRIBUTOR, 2=TRANSPORTER)
                "timestamp": worker[3],       # uint256 timestamp
                "walletAddress": worker[4]    # address account
            })
    except:
        break

print(f"Found {len(blockchain_workers)} workers in blockchain")

# Get existing MongoDB workers
mongo_workers = list(db.workers.find())
mongo_addresses = {w.get('walletAddress') for w in mongo_workers}

print(f"Found {len(mongo_workers)} workers in MongoDB")

# Sync missing workers
synced = 0
for worker in blockchain_workers:
    if worker['walletAddress'] not in mongo_addresses:
        try:
            # Insert into MongoDB
            db.workers.insert_one({
                "workerId": worker["workerId"],
                "name": worker["name"],
                "role": worker["role"],
                "timestamp": worker["timestamp"],
                "walletAddress": worker["walletAddress"]
            })
            print(f"   ✅ Synced: {worker['name']} ({worker['walletAddress']})")
            synced += 1
        except Exception as e:
            print(f"   ❌ Failed to sync {worker['name']}: {e}")

if synced > 0:
    print(f"\n✅ Synced {synced} workers to MongoDB")
else:
    print(f"\n✅ All workers already in sync")

# ===========================
# SYNC PRODUCTS
# ===========================
print("\n2️⃣  Syncing Products...")
print("-"*70)

blockchain_products = []
for i in range(100):  # Check first 100 product IDs
    try:
        product = contract.functions.products(i).call()
        # Check if product exists (name not empty)
        if product[1]:  # product[1] = name
            blockchain_products.append({
                "productId": i,
                "manufacturer": product[0],
                "name": product[1],
                "description": product[2],
                "minTemp": product[3],
                "maxTemp": product[4],
                "minHumidity": product[5],
                "maxHumidity": product[6],
                "quantity": product[7],
                "mfgDate": product[8],
                "currentOwner": product[9]
            })
    except:
        break

print(f"Found {len(blockchain_products)} products in blockchain")

# Get existing MongoDB products
mongo_products = list(db.products.find())
mongo_product_ids = {p.get('productId') for p in mongo_products if 'productId' in p}

print(f"Found {len(mongo_products)} products in MongoDB")

# Sync missing products
synced_products = 0
for product in blockchain_products:
    if product['productId'] not in mongo_product_ids:
        try:
            db.products.insert_one(product)
            print(f"   ✅ Synced: {product['name']} (ID: {product['productId']})")
            synced_products += 1
        except Exception as e:
            print(f"   ❌ Failed to sync {product['name']}: {e}")

if synced_products > 0:
    print(f"\n✅ Synced {synced_products} products to MongoDB")
else:
    print(f"\n✅ All products already in sync")

# ===========================
# SUMMARY
# ===========================
print("\n" + "="*70)
print("📊 Sync Summary:")
print("="*70)
print(f"Workers synced: {synced}")
print(f"Products synced: {synced_products}")
print(f"\nTotal MongoDB workers: {db.workers.count_documents({})}")
print(f"Total MongoDB products: {db.products.count_documents({})}")
print("\n✅ Sync complete!")
print("="*70)
