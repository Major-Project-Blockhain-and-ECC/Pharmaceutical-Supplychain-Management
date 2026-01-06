from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "pharma_db")

# Connection settings
CONNECTION_TIMEOUT = 5000  # 5 seconds
SERVER_SELECTION_TIMEOUT = 5000  # 5 seconds
MAX_POOL_SIZE = 50
MIN_POOL_SIZE = 10

# Global client and db instances
client = None
db = None

def connect_to_mongodb():
    """
    Establish MongoDB connection with error handling
    Returns: (client, db) tuple or raises exception
    """
    global client, db
    
    try:
        print(f"🔌 Attempting to connect to MongoDB at {MONGO_URL}...")
        
        # Create client with proper configuration
        client = MongoClient(
            MONGO_URL,
            serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT,
            connectTimeoutMS=CONNECTION_TIMEOUT,
            maxPoolSize=MAX_POOL_SIZE,
            minPoolSize=MIN_POOL_SIZE,
            retryWrites=True,
            retryReads=True
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database
        db = client[DB_NAME]
        
        # Verify database access
        collections = db.list_collection_names()
        print(f"📦 Database '{DB_NAME}' accessible. Collections: {collections if collections else 'None (will be created on first insert)'}")
        
        return client, db
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        print(f"💡 Make sure MongoDB is running: mongod --version")
        raise Exception("Cannot connect to MongoDB. Is MongoDB running?")
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB Server Timeout: {e}")
        print(f"💡 Check if MongoDB is running on {MONGO_URL}")
        raise Exception("MongoDB server not responding")
        
    except Exception as e:
        print(f"❌ Unexpected MongoDB Error: {e}")
        raise Exception(f"MongoDB connection error: {str(e)}")

def get_database():
    """
    Get database instance, connect if not already connected
    """
    global db
    if db is None:
        connect_to_mongodb()
    return db

def close_mongodb_connection():
    """
    Properly close MongoDB connection
    """
    global client
    if client:
        print("🔌 Closing MongoDB connection...")
        client.close()
        print("✅ MongoDB connection closed")

# Initialize connection on module load
try:
    client, db = connect_to_mongodb()
except Exception as e:
    print(f"⚠️  Warning: Could not establish initial MongoDB connection: {e}")
    print("⚠️  Application will attempt to reconnect when database is accessed")
    # Don't crash the app, let it start and retry later
    client = None
    db = None
