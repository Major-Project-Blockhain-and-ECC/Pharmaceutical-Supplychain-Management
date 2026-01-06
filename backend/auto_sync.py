"""
Auto-sync module for MongoDB and Blockchain synchronization
"""

from database import get_database
from contract import contract
import asyncio
from datetime import datetime

def sync_workers_from_blockchain():
    """
    Sync workers from blockchain to MongoDB
    Returns: (synced_count, error)
    """
    try:
        db = get_database()
        
        # Get blockchain workers
        blockchain_workers = []
        for i in range(100):
            try:
                worker = contract.functions.workers(i).call()
                if worker[1]:  # name field
                    blockchain_workers.append({
                        "workerId": worker[0],
                        "name": worker[1],
                        "role": worker[2],
                        "timestamp": worker[3],
                        "walletAddress": worker[4]
                    })
            except:
                break
        
        # Get MongoDB workers
        mongo_workers = list(db.workers.find())
        mongo_addresses = {w.get('walletAddress') for w in mongo_workers}
        
        # Sync missing workers
        synced = 0
        for worker in blockchain_workers:
            if worker['walletAddress'] not in mongo_addresses:
                db.workers.insert_one(worker)
                synced += 1
        
        return synced, None
        
    except Exception as e:
        return 0, str(e)

def sync_products_from_blockchain():
    """
    Sync products from blockchain to MongoDB
    Returns: (synced_count, error)
    """
    try:
        db = get_database()
        
        # Get blockchain products
        blockchain_products = []
        for i in range(100):
            try:
                product = contract.functions.products(i).call()
                # Product struct: (productId, name, description, minTemp, maxTemp, minHumidity, maxHumidity, quantity, mfgDate, timestamp, currentOwner, isSpoiled)
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
            except:
                break
        
        # Get MongoDB products
        mongo_products = list(db.products.find())
        mongo_product_ids = {p.get('productId') for p in mongo_products if 'productId' in p}
        
        # Sync missing products
        synced = 0
        for product in blockchain_products:
            if product['productId'] not in mongo_product_ids:
                db.products.insert_one(product)
                synced += 1
        
        return synced, None
        
    except Exception as e:
        return 0, str(e)

def sync_status_from_blockchain():
    """
    Sync product status history from blockchain to MongoDB
    Returns: (synced_count, error)
    """
    try:
        db = get_database()
        
        # Get all products first
        product_count = 0
        for i in range(100):
            try:
                product = contract.functions.products(i).call()
                if product[1]:  # name exists
                    product_count = i + 1
            except:
                break
        
        if product_count == 0:
            return 0, None
        
        # Get existing status entries from MongoDB
        existing_statuses = list(db.status.find())
        # Create unique key for each status: productId + timestamp
        existing_keys = {
            f"{s.get('productId', '')}_{s.get('timestamp', '')}" 
            for s in existing_statuses 
            if 'productId' in s and 'timestamp' in s
        }
        
        # Sync status for each product
        synced = 0
        for product_id in range(product_count):
            try:
                # Get product history from blockchain
                history = contract.functions.getProductHistory(product_id).call()
                
                for status in history:
                    # Status struct: (location, temperature, humidity, workerId, productId, quantity, isSpoiled, timestamp)
                    status_key = f"{status[4]}_{status[7]}"  # productId_timestamp
                    
                    if status_key not in existing_keys:
                        status_data = {
                            "productId": status[4],
                            "location": status[0],
                            "temperature": status[1],
                            "humidity": status[2],
                            "workerId": status[3],
                            "quantity": status[5],
                            "isSpoiled": status[6],
                            "timestamp": status[7]
                        }
                        db.status.insert_one(status_data)
                        synced += 1
                        
            except Exception as e:
                # Product might not have history yet, continue
                continue
        
        return synced, None
        
    except Exception as e:
        return 0, str(e)

def auto_sync_all(silent=False):
    """
    Automatically sync all data from blockchain to MongoDB
    Args:
        silent: If True, suppress console output
    Returns:
        dict with sync results
    """
    if not silent:
        print("🔄 Auto-syncing MongoDB with Blockchain...")
    
    results = {
        "workers_synced": 0,
        "products_synced": 0,
        "status_synced": 0,
        "errors": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Sync workers
    workers_synced, worker_error = sync_workers_from_blockchain()
    results["workers_synced"] = workers_synced
    if worker_error:
        results["errors"].append(f"Workers: {worker_error}")
    elif not silent and workers_synced > 0:
        print(f"   ✅ Synced {workers_synced} workers")
    
    # Sync products
    products_synced, product_error = sync_products_from_blockchain()
    results["products_synced"] = products_synced
    if product_error:
        results["errors"].append(f"Products: {product_error}")
    elif not silent and products_synced > 0:
        print(f"   ✅ Synced {products_synced} products")
    
    # Sync status updates
    status_synced, status_error = sync_status_from_blockchain()
    results["status_synced"] = status_synced
    if status_error:
        results["errors"].append(f"Status: {status_error}")
    elif not silent and status_synced > 0:
        print(f"   ✅ Synced {status_synced} status updates")
    
    if not silent:
        if results["workers_synced"] == 0 and results["products_synced"] == 0 and results["status_synced"] == 0:
            print("   ✅ Already in sync")
        elif results["errors"]:
            print(f"   ⚠️  Sync completed with errors: {results['errors']}")
        else:
            print("   ✅ Sync complete")
    
    return results

async def periodic_sync(interval_minutes=5):
    """
    Background task to periodically sync blockchain to MongoDB
    Args:
        interval_minutes: How often to sync (default: 5 minutes)
    """
    while True:
        try:
            await asyncio.sleep(interval_minutes * 60)
            print(f"\n⏰ Periodic sync (every {interval_minutes} min)...")
            auto_sync_all(silent=False)
        except Exception as e:
            print(f"❌ Periodic sync error: {e}")
