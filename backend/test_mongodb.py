"""
MongoDB Connection Test Script
Run this to verify your MongoDB setup before starting the application
"""

from database import connect_to_mongodb, get_database, close_mongodb_connection
import sys

def test_connection():
    """Test MongoDB connection"""
    print("\n" + "="*70)
    print("🧪 MONGODB CONNECTION TEST")
    print("="*70 + "\n")
    
    try:
        # Test 1: Connect to MongoDB
        print("Test 1: Connecting to MongoDB...")
        client, db = connect_to_mongodb()
        print("✅ PASS: Connection established\n")
        
        # Test 2: Get database instance
        print("Test 2: Getting database instance...")
        db = get_database()
        print(f"✅ PASS: Database '{db.name}' accessible\n")
        
        # Test 3: List collections
        print("Test 3: Listing collections...")
        collections = db.list_collection_names()
        if collections:
            print(f"✅ PASS: Found {len(collections)} collections:")
            for col in collections:
                print(f"   - {col}")
        else:
            print("ℹ️  INFO: No collections yet (will be created on first insert)")
        print()
        
        # Test 4: Test write operation
        print("Test 4: Testing write operation...")
        test_collection = db.test_connection
        test_doc = {"test": "connection_test", "status": "success"}
        result = test_collection.insert_one(test_doc)
        print(f"✅ PASS: Document inserted with ID: {result.inserted_id}\n")
        
        # Test 5: Test read operation
        print("Test 5: Testing read operation...")
        found = test_collection.find_one({"_id": result.inserted_id})
        if found:
            print(f"✅ PASS: Document retrieved: {found}\n")
        
        # Test 6: Clean up test data
        print("Test 6: Cleaning up test data...")
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ PASS: Test document deleted\n")
        
        # Test 7: Check critical collections
        print("Test 7: Checking critical collections...")
        critical_collections = ["workers", "products", "status"]
        for col_name in critical_collections:
            count = db[col_name].count_documents({})
            print(f"   - {col_name}: {count} documents")
        print()
        
        # Summary
        print("="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("✅ MongoDB is properly configured and ready to use")
        print("✅ You can now start the FastAPI application")
        print("\nTo start the backend, run:")
        print("   cd backend")
        print("   uvicorn main:app --reload")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print("="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"Error: {e}\n")
        print("💡 TROUBLESHOOTING STEPS:")
        print("1. Check if MongoDB is running:")
        print("   mongod --version")
        print("   (If not installed, download from: https://www.mongodb.com/try/download/community)")
        print("\n2. Start MongoDB service:")
        print("   Windows: net start MongoDB")
        print("   macOS: brew services start mongodb-community")
        print("   Linux: sudo systemctl start mongod")
        print("\n3. Verify MongoDB is listening on port 27017:")
        print("   Check your .env file: MONGO_URL=mongodb://localhost:27017")
        print("\n4. Test MongoDB connection manually:")
        print("   mongosh")
        print("="*70 + "\n")
        return False
    
    finally:
        # Close connection
        close_mongodb_connection()

def check_mongodb_service():
    """Check if MongoDB service is running"""
    import subprocess
    
    print("\n🔍 Checking MongoDB service status...\n")
    
    try:
        # Try to connect using mongosh or mongo
        result = subprocess.run(
            ["mongosh", "--eval", "db.version()", "--quiet"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ MongoDB is running (version: {result.stdout.strip()})")
            return True
        else:
            print("⚠️  MongoDB may not be running")
            return False
            
    except FileNotFoundError:
        print("ℹ️  mongosh not found, trying mongo client...")
        try:
            result = subprocess.run(
                ["mongo", "--eval", "db.version()", "--quiet"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ MongoDB is running")
                return True
        except:
            pass
        print("⚠️  Could not verify MongoDB status (client not found)")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  MongoDB connection timed out")
        return False
    except Exception as e:
        print(f"⚠️  Could not check MongoDB status: {e}")
        return False

if __name__ == "__main__":
    print("\n🏥 PharmaDApp - MongoDB Connection Tester\n")
    
    # First check if MongoDB service is running
    service_running = check_mongodb_service()
    
    # Run connection tests
    success = test_connection()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
