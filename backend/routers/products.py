from fastapi import APIRouter, HTTPException
from model import ProductModel
from contract import contract, send_transaction
from database import get_database

router = APIRouter(prefix="/products")

@router.post("/add")
def add_product(data: ProductModel):
    try:
        # Get database connection
        db = get_database()
        
        contract_function = contract.functions.addProduct(
            data.name,
            data.description,
            data.minTemp,
            data.maxTemp,
            data.minHumidity,
            data.maxHumidity,
            data.quantity,
            data.mfgDate
        )
        
        result = send_transaction(contract_function)
        
        if result["success"]:
            # Get the product ID from blockchain
            try:
                from contract import contract as contract_instance
                product_id = None
                
                # Find the latest product
                for i in range(100):
                    try:
                        product = contract_instance.functions.products(i).call()
                        if product[1] == data.name:  # Match by name
                            product_id = product[0]
                    except:
                        break
                
                # Insert full blockchain data structure
                product_data = {
                    "productId": product_id if product_id is not None else -1,
                    "name": data.name,
                    "description": data.description,
                    "minTemp": data.minTemp,
                    "maxTemp": data.maxTemp,
                    "minHumidity": data.minHumidity,
                    "maxHumidity": data.maxHumidity,
                    "quantity": data.quantity,
                    "mfgDate": data.mfgDate
                }
                
                db.products.insert_one(product_data)
                print(f"✅ Product saved to MongoDB: {product_data}")
                
            except Exception as mongo_error:
                print(f"⚠️  MongoDB insert failed: {mongo_error}")
                print(f"💡 Product is in blockchain. Will auto-sync on next startup.")
            
            return {"message": "Product added", "tx_hash": result["tx_hash"]}
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
def list_products():
    try:
        db = get_database()
        products = list(db.products.find())
        # Convert ObjectId to string for JSON serialization
        for product in products:
            product["_id"] = str(product["_id"])
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/history/{product_id}")
def get_product_history(product_id: int):
    try:
        history = contract.functions.getProductHistory(product_id).call()
        result = []
        for status in history:
            result.append({
                "location": status[0],
                "temperature": status[1],
                "humidity": status[2],
                "heatIndex": status[3],
                "workerId": status[4],
                "productId": status[5],
                "quantity": status[6],
                "qualityMaintained": status[7],
                "timestamp": status[8]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
