from fastapi import APIRouter, HTTPException
from model import WorkerModel
from contract import contract, send_transaction
from database import get_database

router = APIRouter(prefix="/workers")

@router.post("/add")
def add_worker(data: WorkerModel):
    try:
        print(f"📝 Adding worker: {data.name}, role: {data.role}, address: {data.walletAddress}")
        
        # Get database connection first
        db = get_database()
        
        # Prepare contract function with wallet address
        contract_function = contract.functions.registerWorker(data.name, data.role, data.walletAddress)
        
        # Send signed transaction
        result = send_transaction(contract_function)
        print(f"📦 Transaction result: {result}")
        
        if result["success"]:
            # CRITICAL: Always insert to MongoDB after blockchain success
            try:
                # Get worker ID from blockchain (it's the latest one)
                from contract import contract as contract_instance
                worker_id = None
                
                # Try to find the worker by address
                for i in range(100):
                    try:
                        worker = contract_instance.functions.workers(i).call()
                        if worker[4] == data.walletAddress:  # Match wallet address
                            worker_id = worker[0]
                            break
                    except:
                        break
                
                # Insert with full data
                worker_data = {
                    "workerId": worker_id if worker_id is not None else -1,
                    "name": data.name,
                    "role": data.role,
                    "walletAddress": data.walletAddress
                }
                
                db.workers.insert_one(worker_data)
                print(f"✅ Worker saved to MongoDB: {worker_data}")
                
            except Exception as mongo_error:
                print(f"⚠️  MongoDB insert failed: {mongo_error}")
                print(f"💡 Worker is in blockchain but not MongoDB. Run sync to fix.")
                # Don't fail the request - blockchain succeeded
            
            response_data = {"message": "Worker added", "tx_hash": result["tx_hash"]}
            print(f"✅ Response: {response_data}")
            return response_data
        else:
            error_response = {"error": result["error"]}
            print(f"❌ Error response: {error_response}")
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        error_response = {"error": str(e)}
        print(f"❌ Exception: {error_response}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_workers():
    try:
        db = get_database()
        result = db.workers.find()
        workers = list(result)
        # Convert ObjectId to string for JSON serialization
        for worker in workers:
            worker["_id"] = str(worker["_id"])
        return workers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
