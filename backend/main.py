from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import workers, products, status, performance
from database import connect_to_mongodb, close_mongodb_connection, get_database
from contextlib import asynccontextmanager
from auto_sync import auto_sync_all, periodic_sync
import asyncio

# Background task for periodic sync
background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup: Ensure MongoDB connection
    try:
        print("🚀 Starting up application...")
        db = get_database()
        print("✅ MongoDB connection verified at startup")
        
        # Auto-sync on startup
        print("\n🔄 Auto-syncing data on startup...")
        sync_results = auto_sync_all(silent=False)
        
        if sync_results["workers_synced"] > 0 or sync_results["products_synced"] > 0 or sync_results.get("status_synced", 0) > 0:
            print(f"   📊 Startup sync: {sync_results['workers_synced']} workers, {sync_results['products_synced']} products, {sync_results.get('status_synced', 0)} status updates")
        else:
            print("   ✅ Data already synchronized")
        
        # Optional: Start periodic background sync (uncomment if needed)
        # task = asyncio.create_task(periodic_sync(interval_minutes=5))
        # background_tasks.add(task)
        # print("⏰ Periodic sync enabled (every 5 minutes)")
        
        print("\n✅ Application ready!\n")
        yield
        
    except Exception as e:
        print(f"⚠️  Startup warning: {e}")
        yield  # Allow app to start anyway
    finally:
        # Shutdown: Close MongoDB connection
        print("\n🛑 Shutting down application...")
        
        # Cancel background tasks
        for task in background_tasks:
            task.cancel()
        
        close_mongodb_connection()

app = FastAPI(
    title="Pharmaceutical Supply Chain Backend",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def root():
    return {"message": "Backend running successfully"}

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify MongoDB connection
    """
    try:
        db = get_database()
        # Test database access
        db.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "collections": db.list_collection_names()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/sync")
def manual_sync():
    """
    Manually trigger blockchain to MongoDB synchronization
    Useful for ensuring data consistency
    """
    try:
        results = auto_sync_all(silent=False)
        return {
            "success": True,
            "message": "Synchronization complete",
            "workers_synced": results["workers_synced"],
            "products_synced": results["products_synced"],
            "errors": results["errors"],
            "timestamp": results["timestamp"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/sync/status")
def sync_status():
    """
    Check synchronization status between blockchain and MongoDB
    """
    try:
        from contract import contract
        db = get_database()
        
        # Count blockchain workers
        blockchain_worker_count = 0
        for i in range(100):
            try:
                worker = contract.functions.workers(i).call()
                if worker[1]:  # name field
                    blockchain_worker_count += 1
            except:
                break
        
        # Count blockchain products
        blockchain_product_count = 0
        for i in range(100):
            try:
                product = contract.functions.products(i).call()
                if product[1]:  # name field
                    blockchain_product_count += 1
            except:
                break
        
        # Count MongoDB
        mongo_worker_count = db.workers.count_documents({})
        mongo_product_count = db.products.count_documents({})
        
        in_sync = (
            blockchain_worker_count == mongo_worker_count and
            blockchain_product_count == mongo_product_count
        )
        
        return {
            "in_sync": in_sync,
            "blockchain": {
                "workers": blockchain_worker_count,
                "products": blockchain_product_count
            },
            "mongodb": {
                "workers": mongo_worker_count,
                "products": mongo_product_count
            },
            "message": "Synchronized ✅" if in_sync else "Out of sync ⚠️"
        }
    except Exception as e:
        return {
            "error": str(e)
        }

app.include_router(workers.router)
app.include_router(products.router)
app.include_router(status.router)
app.include_router(performance.router)
