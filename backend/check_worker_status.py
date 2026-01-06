"""
Check Worker Registration Status
Identifies the mismatch between blockchain and MongoDB
"""

from database import get_database
from contract import contract

print("="*70)
print("🔍 Worker Registration Status Check")
print("="*70 + "\n")

# Check MongoDB
print("📊 MongoDB Workers:")
print("-"*70)
db = get_database()
mongo_workers = list(db.workers.find())
print(f"Total workers in MongoDB: {len(mongo_workers)}\n")

if mongo_workers:
    for idx, worker in enumerate(mongo_workers, 1):
        print(f"{idx}. {worker['name']} (Role: {worker['role']})")
        print(f"   Address: {worker['walletAddress']}\n")
else:
    print("❌ No workers in MongoDB\n")

# Check Blockchain
print("⛓️  Blockchain Workers:")
print("-"*70)

blockchain_workers = []
try:
    # Try to get worker count
    try:
        worker_count = contract.functions.workerCounter().call()
        print(f"Total workers in blockchain: {worker_count}\n")
    except:
        print("ℹ️  Contract doesn't have workerCounter(), scanning...\n")
        worker_count = 10  # Try first 10
    
    for i in range(worker_count):
        try:
            worker = contract.functions.workers(i).call()
            if worker[0]:  # name field not empty
                blockchain_workers.append({
                    "index": i,
                    "name": worker[0],
                    "role": worker[1],
                    "registered": worker[2],
                    "walletAddress": worker[3]
                })
        except:
            break
    
    if blockchain_workers:
        for worker in blockchain_workers:
            print(f"{worker['index']}. {worker['name']} (Role: {worker['role']})")
            print(f"   Address: {worker['walletAddress']}")
            print(f"   Registered: {worker['registered']}\n")
    else:
        print("❌ No workers in blockchain\n")
        
except Exception as e:
    print(f"❌ Error reading blockchain: {e}\n")

# Compare
print("="*70)
print("🔎 Comparison:")
print("="*70)
print(f"MongoDB: {len(mongo_workers)} workers")
print(f"Blockchain: {len(blockchain_workers)} workers")

if len(mongo_workers) < len(blockchain_workers):
    print("\n⚠️  ISSUE: Blockchain has more workers than MongoDB")
    print("💡 Some blockchain workers were not saved to MongoDB")
    
    # Find missing workers
    mongo_addresses = {w['walletAddress'] for w in mongo_workers}
    blockchain_addresses = {w['walletAddress'] for w in blockchain_workers}
    missing = blockchain_addresses - mongo_addresses
    
    if missing:
        print(f"\n❌ Missing from MongoDB:")
        for addr in missing:
            worker = next(w for w in blockchain_workers if w['walletAddress'] == addr)
            print(f"   - {worker['name']} ({addr})")
            
elif len(mongo_workers) > len(blockchain_workers):
    print("\n⚠️  ISSUE: MongoDB has more workers than blockchain")
    print("💡 This shouldn't happen - data inconsistency!")
else:
    print("\n✅ Databases are synchronized!")

print("\n" + "="*70)
print("💡 SOLUTION:")
print("="*70)
if len(mongo_workers) < len(blockchain_workers):
    print("Run sync_databases.py to sync MongoDB with blockchain")
elif len(mongo_workers) == 0 and len(blockchain_workers) == 0:
    print("Register a new worker with a unique wallet address")
else:
    print("Databases look good!")
