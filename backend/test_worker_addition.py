"""
Test Worker Addition - Verify MongoDB insertion
"""

from database import get_database
import requests
import json

# Test data
test_worker = {
    "name": "Test Worker",
    "role": 0,  # MANUFACTURER
    "walletAddress": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
}

print("="*70)
print("🧪 Testing Worker Addition Flow")
print("="*70 + "\n")

# Step 1: Check current workers in MongoDB
print("Step 1: Checking MongoDB before addition...")
db = get_database()
initial_count = db.workers.count_documents({})
print(f"Current workers in MongoDB: {initial_count}\n")

# Step 2: Test direct MongoDB insertion
print("Step 2: Testing direct MongoDB insertion...")
try:
    result = db.workers.insert_one(test_worker)
    print(f"✅ Direct insertion successful! ID: {result.inserted_id}")
    
    # Verify
    count_after = db.workers.count_documents({})
    print(f"Workers in MongoDB after insertion: {count_after}\n")
    
    # Clean up test data
    db.workers.delete_one({"_id": result.inserted_id})
    print("🗑️  Test data cleaned up\n")
    
except Exception as e:
    print(f"❌ Direct insertion failed: {e}\n")

# Step 3: Test API endpoint (if backend is running)
print("Step 3: Testing API endpoint...")
print("Note: Make sure backend is running on http://localhost:8000\n")

api_url = "http://localhost:8000/workers/add"

try:
    response = requests.post(api_url, json=test_worker, timeout=5)
    
    if response.status_code == 200:
        print(f"✅ API call successful!")
        print(f"Response: {response.json()}\n")
        
        # Check MongoDB
        count_after_api = db.workers.count_documents({})
        print(f"Workers in MongoDB after API call: {count_after_api}")
        
        # Find the worker
        worker = db.workers.find_one({"walletAddress": test_worker["walletAddress"]})
        if worker:
            print(f"✅ Worker found in MongoDB: {worker}")
        else:
            print("❌ Worker NOT found in MongoDB!")
            
    else:
        print(f"❌ API call failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("⚠️  Could not connect to backend API")
    print("💡 Start backend with: uvicorn main:app --reload")
    
except Exception as e:
    print(f"❌ API test failed: {e}")

# Step 4: List all workers
print("\n" + "="*70)
print("📋 Current Workers in MongoDB:")
print("="*70)

workers = list(db.workers.find())
if workers:
    for idx, worker in enumerate(workers, 1):
        print(f"\n{idx}. {worker['name']}")
        print(f"   Role: {worker['role']}")
        print(f"   Address: {worker['walletAddress']}")
else:
    print("No workers found in database")

print("\n" + "="*70)
print("✅ Test Complete")
print("="*70)
