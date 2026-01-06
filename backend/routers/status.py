from fastapi import APIRouter, HTTPException
from model import StatusModel
from contract import contract, send_transaction
from database import get_database

router = APIRouter(prefix="/status")

@router.post("/update")
def update_status(data: StatusModel):
    try:
        # Get database connection
        db = get_database()
        
        contract_function = contract.functions.updateStatus(
            data.productId,
            data.location,
            data.temperature,
            data.humidity,
            data.quantity
        )
        
        result = send_transaction(contract_function)
        
        if result["success"]:
            # Save status update with full data
            try:
                import time
                status_data = {
                    "productId": data.productId,
                    "location": data.location,
                    "temperature": data.temperature,
                    "humidity": data.humidity,
                    "quantity": data.quantity,
                    "timestamp": int(time.time()),
                    "tx_hash": result["tx_hash"]
                }
                
                db.status.insert_one(status_data)
                print(f"✅ Status saved to MongoDB: {status_data}")
                
            except Exception as mongo_error:
                print(f"⚠️  MongoDB insert failed: {mongo_error}")
                print(f"💡 Status is in blockchain. Check product history.")
            
            return {"message": "Status updated", "tx_hash": result["tx_hash"]}
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track/{pid}")
def track_status(pid: int):
    try:
        db = get_database()
        # Query by productId field, not pid
        status_data = db.status.find({"productId": pid})
        statuses = list(status_data)
        # Convert ObjectId to string
        for status in statuses:
            status["_id"] = str(status["_id"])
        return statuses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
