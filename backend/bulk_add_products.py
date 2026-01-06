"""
Bulk Product Addition Script
Add multiple pharmaceutical products to blockchain and MongoDB
"""

from contract import contract, web3
from database import get_database
from datetime import datetime
import time

# Sample pharmaceutical products with authentic temperature requirements
PRODUCTS = [
    {
        "name": "Pfizer COVID-19 Vaccine (Comirnaty)",
        "description": "mRNA vaccine requiring ultra-cold storage",
        "minTemp": -80,
        "maxTemp": -60,
        "minHumidity": 30,
        "maxHumidity": 60,
        "quantity": 500,
        "mfgDate": "2024-12-01"
    },
    {
        "name": "Moderna COVID-19 Vaccine",
        "description": "mRNA vaccine with flexible storage",
        "minTemp": -25,
        "maxTemp": -15,
        "minHumidity": 30,
        "maxHumidity": 60,
        "quantity": 400,
        "mfgDate": "2024-12-05"
    },
    {
        "name": "Human Insulin (Humulin)",
        "description": "Critical diabetes medication",
        "minTemp": 2,
        "maxTemp": 8,
        "minHumidity": 40,
        "maxHumidity": 70,
        "quantity": 1000,
        "mfgDate": "2024-11-20"
    },
    {
        "name": "Hepatitis B Vaccine",
        "description": "Recombinant vaccine for HBV",
        "minTemp": 2,
        "maxTemp": 8,
        "minHumidity": 35,
        "maxHumidity": 65,
        "quantity": 800,
        "mfgDate": "2024-12-10"
    },
    {
        "name": "MMR Vaccine (Measles, Mumps, Rubella)",
        "description": "Live attenuated viral vaccine",
        "minTemp": 2,
        "maxTemp": 8,
        "minHumidity": 35,
        "maxHumidity": 65,
        "quantity": 600,
        "mfgDate": "2024-12-08"
    },
    {
        "name": "Factor VIII Concentrate",
        "description": "Blood clotting factor for hemophilia",
        "minTemp": 2,
        "maxTemp": 8,
        "minHumidity": 35,
        "maxHumidity": 60,
        "quantity": 200,
        "mfgDate": "2024-11-25"
    },
    {
        "name": "Monoclonal Antibody (Rituximab)",
        "description": "Biologic for cancer and autoimmune diseases",
        "minTemp": 2,
        "maxTemp": 8,
        "minHumidity": 40,
        "maxHumidity": 70,
        "quantity": 150,
        "mfgDate": "2024-12-01"
    },
    {
        "name": "Rabies Vaccine (Inactivated)",
        "description": "Life-saving post-exposure prophylaxis",
        "minTemp": 2,
        "maxTemp": 8,
        "minHumidity": 35,
        "maxHumidity": 65,
        "quantity": 300,
        "mfgDate": "2024-11-28"
    },
    {
        "name": "Fresh Frozen Plasma (FFP)",
        "description": "Blood product for coagulation disorders",
        "minTemp": -25,
        "maxTemp": -18,
        "minHumidity": 30,
        "maxHumidity": 60,
        "quantity": 100,
        "mfgDate": "2024-12-15"
    },
    {
        "name": "Immunoglobulin IV (IVIG)",
        "description": "Antibody therapy for immune deficiencies",
        "minTemp": 2,
        "maxTemp": 8,
        "minHumidity": 40,
        "maxHumidity": 70,
        "quantity": 250,
        "mfgDate": "2024-12-12"
    }
]

def add_product_to_blockchain(product, manufacturer_address):
    """
    Add a single product to blockchain
    """
    try:
        # Call smart contract (mfgDate is a string)
        tx_hash = contract.functions.addProduct(
            product["name"],
            product["description"],
            product["minTemp"],
            product["maxTemp"],
            product["minHumidity"],
            product["maxHumidity"],
            product["quantity"],
            product["mfgDate"]  # Send as string
        ).transact({
            'from': manufacturer_address,
            'gas': 3000000
        })
        
        # Wait for transaction
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            # Get product ID from blockchain
            product_count = contract.functions.productCount().call()
            return product_count, None
        else:
            return None, "Transaction failed"
            
    except Exception as e:
        return None, str(e)

def sync_product_to_mongodb(product_id, product_data):
    """
    Sync product to MongoDB
    """
    try:
        db = get_database()
        
        # Check if already exists
        existing = db.products.find_one({"productId": product_id})
        if existing:
            return True, "Already in MongoDB"
        
        # Insert to MongoDB
        mongo_product = {
            "productId": product_id,
            "name": product_data["name"],
            "description": product_data["description"],
            "minTemp": product_data["minTemp"],
            "maxTemp": product_data["maxTemp"],
            "minHumidity": product_data["minHumidity"],
            "maxHumidity": product_data["maxHumidity"],
            "quantity": product_data["quantity"],
            "manufacturingDate": product_data["mfgDate"],
            "synced_at": datetime.now().isoformat()
        }
        
        db.products.insert_one(mongo_product)
        return True, "Synced to MongoDB"
        
    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "="*70)
    print("🏭 BULK PRODUCT ADDITION TO PHARMA SUPPLY CHAIN")
    print("="*70)
    
    # Get manufacturer address (first account)
    accounts = web3.eth.accounts
    if not accounts:
        print("❌ No accounts available. Make sure blockchain is running.")
        return
    
    manufacturer_address = accounts[0]
    print(f"\n📋 Using manufacturer address: {manufacturer_address}")
    
    # Check if manufacturer is registered
    try:
        worker_count = contract.functions.workerCount().call()
        is_registered = False
        manufacturer_role = 0  # MANUFACTURER = 0
        
        print(f"📊 Checking {worker_count} registered workers...")
        
        for i in range(1, worker_count + 1):
            worker = contract.functions.workers(i).call()
            worker_address = worker[4]  # walletAddress is at index 4
            worker_role = worker[2]     # role is at index 2
            
            if worker_address.lower() == manufacturer_address.lower() and worker_role == manufacturer_role:
                is_registered = True
                print(f"✅ Address is registered as MANUFACTURER (Worker ID: {i})")
                break
        
        if not is_registered:
            print(f"\n⚠️  Address {manufacturer_address} is NOT registered as a manufacturer")
            print("🔧 Registering as manufacturer...")
            
            # Register as manufacturer
            tx_hash = contract.functions.registerWorker(
                "Bulk Product Manufacturer",
                0  # MANUFACTURER role
            ).transact({
                'from': manufacturer_address,
                'gas': 3000000
            })
            
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print("✅ Successfully registered as manufacturer")
            else:
                print("❌ Failed to register as manufacturer")
                return
                
    except Exception as e:
        print(f"❌ Error checking worker registration: {e}")
        return
    
    print(f"📦 Total products to add: {len(PRODUCTS)}")
    
    input("\n⏸️  Press Enter to start adding products...")
    
    # Statistics
    success_count = 0
    failed_count = 0
    results = []
    
    print("\n" + "-"*70)
    
    for idx, product in enumerate(PRODUCTS, 1):
        print(f"\n[{idx}/{len(PRODUCTS)}] Adding: {product['name']}")
        print(f"   📊 Temp: {product['minTemp']}°C to {product['maxTemp']}°C")
        print(f"   💧 Humidity: {product['minHumidity']}% to {product['maxHumidity']}%")
        print(f"   📦 Quantity: {product['quantity']}")
        
        # Add to blockchain
        product_id, error = add_product_to_blockchain(product, manufacturer_address)
        
        if product_id:
            print(f"   ✅ Added to blockchain (Product ID: {product_id})")
            
            # Sync to MongoDB
            sync_success, sync_msg = sync_product_to_mongodb(product_id, product)
            if sync_success:
                print(f"   ✅ {sync_msg}")
                success_count += 1
                results.append({
                    "name": product["name"],
                    "productId": product_id,
                    "status": "SUCCESS"
                })
            else:
                print(f"   ⚠️  MongoDB sync failed: {sync_msg}")
                failed_count += 1
                results.append({
                    "name": product["name"],
                    "productId": product_id,
                    "status": "BLOCKCHAIN_ONLY"
                })
        else:
            print(f"   ❌ Failed: {error}")
            failed_count += 1
            results.append({
                "name": product["name"],
                "status": "FAILED",
                "error": error
            })
        
        # Small delay to avoid overwhelming the blockchain
        if idx < len(PRODUCTS):
            time.sleep(0.5)
    
    # Summary
    print("\n" + "="*70)
    print("📊 BULK ADDITION SUMMARY")
    print("="*70)
    print(f"✅ Successfully added: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📦 Total products: {len(PRODUCTS)}")
    
    if success_count > 0:
        print("\n✅ Successfully Added Products:")
        for result in results:
            if result["status"] == "SUCCESS":
                print(f"   • {result['name']} (ID: {result['productId']})")
    
    if failed_count > 0:
        print("\n❌ Failed Products:")
        for result in results:
            if result["status"] == "FAILED":
                print(f"   • {result['name']}: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*70)
    print("✅ Bulk addition complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
