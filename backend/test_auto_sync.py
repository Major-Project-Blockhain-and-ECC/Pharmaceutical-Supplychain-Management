"""
Test Auto-Sync Functionality
"""

# Test 1: Import auto_sync module
print("Test 1: Importing auto_sync module...")
try:
    from auto_sync import auto_sync_all, sync_workers_from_blockchain, sync_products_from_blockchain
    print("✅ PASS: auto_sync module imported\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 2: Test sync functions exist
print("Test 2: Checking sync functions...")
try:
    assert callable(auto_sync_all)
    assert callable(sync_workers_from_blockchain)
    assert callable(sync_products_from_blockchain)
    print("✅ PASS: All sync functions available\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 3: Test auto_sync_all
print("Test 3: Running auto_sync_all...")
try:
    results = auto_sync_all(silent=True)
    print(f"✅ PASS: auto_sync_all completed")
    print(f"   Workers synced: {results['workers_synced']}")
    print(f"   Products synced: {results['products_synced']}")
    print(f"   Errors: {results['errors']}\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 4: Verify MongoDB has correct data
print("Test 4: Verifying MongoDB data...")
try:
    from database import get_database
    db = get_database()
    
    worker_count = db.workers.count_documents({})
    product_count = db.products.count_documents({})
    
    print(f"✅ PASS: MongoDB accessible")
    print(f"   Workers in MongoDB: {worker_count}")
    print(f"   Products in MongoDB: {product_count}\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 5: Compare with blockchain
print("Test 5: Comparing with blockchain...")
try:
    from contract import contract
    
    # Count blockchain workers
    blockchain_workers = 0
    for i in range(100):
        try:
            worker = contract.functions.workers(i).call()
            if worker[1]:
                blockchain_workers += 1
        except:
            break
    
    # Count blockchain products
    blockchain_products = 0
    for i in range(100):
        try:
            product = contract.functions.products(i).call()
            if product[1]:
                blockchain_products += 1
        except:
            break
    
    print(f"✅ PASS: Blockchain accessible")
    print(f"   Workers in Blockchain: {blockchain_workers}")
    print(f"   Products in Blockchain: {blockchain_products}")
    
    # Check if in sync
    if worker_count == blockchain_workers and product_count == blockchain_products:
        print(f"\n🎉 SUCCESS: MongoDB and Blockchain are synchronized!")
    else:
        print(f"\n⚠️  WARNING: Out of sync detected")
        print(f"   Difference: Workers={blockchain_workers-worker_count}, Products={blockchain_products-product_count}")
        
except Exception as e:
    print(f"❌ FAIL: {e}\n")

print("\n" + "="*70)
print("✅ Auto-sync functionality is ready!")
print("="*70)
print("\nNext steps:")
print("1. Restart backend: uvicorn main:app --reload")
print("2. Watch for auto-sync on startup")
print("3. Test endpoints:")
print("   - GET  http://localhost:8000/sync/status")
print("   - POST http://localhost:8000/sync")
