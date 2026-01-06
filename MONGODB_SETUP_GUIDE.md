# MONGODB SETUP & VERIFICATION GUIDE

## Overview
This guide ensures MongoDB is properly configured for PharmaDApp.

---

## Quick Start

### 1. Test MongoDB Connection
```bash
cd backend
python test_mongodb.py
```

If all tests pass ✅, you're good to go!

---

## Installation (If MongoDB Not Installed)

### **Windows:**
```powershell
# Download MongoDB Community Server
# https://www.mongodb.com/try/download/community

# After installation, start service:
net start MongoDB

# Verify installation:
mongod --version
```

### **macOS:**
```bash
# Install via Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start service
brew services start mongodb-community

# Verify
mongod --version
```

### **Linux (Ubuntu/Debian):**
```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
mongod --version
```

---

## Configuration

### **1. Environment Variables (`.env` file)**

Your `backend/.env` should contain:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=pharma_db
PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=your_contract_address_here
RPC_URL=http://127.0.0.1:8545
```

### **2. Connection Settings**

Current configuration in `database.py`:
- **Connection Timeout**: 5 seconds
- **Server Selection Timeout**: 5 seconds
- **Max Pool Size**: 50 connections
- **Min Pool Size**: 10 connections
- **Retry Writes**: Enabled
- **Retry Reads**: Enabled

---

## Database Schema

### **Collections:**

#### **1. workers**
```json
{
  "name": "John Doe",
  "role": "Manufacturer",
  "walletAddress": "0x1234..."
}
```

#### **2. products**
```json
{
  "name": "Pfizer COVID-19 Vaccine",
  "description": "mRNA vaccine",
  "requiredTemp": "-80°C to -60°C",
  "mfgDate": "2024-06-15",
  "quantity": 1000
}
```

#### **3. status**
```json
{
  "productId": 0,
  "location": "New York Warehouse",
  "temperature": -75,
  "humidity": 45,
  "heatIndex": 0,
  "quantity": 1000
}
```

---

## Verification Steps

### **Step 1: Check MongoDB Service**
```bash
# Windows
sc query MongoDB

# macOS
brew services list | grep mongodb

# Linux
sudo systemctl status mongod
```

### **Step 2: Test Connection Manually**
```bash
# Connect using mongosh (modern client)
mongosh

# Or mongo (legacy client)
mongo

# Once connected, test:
> show dbs
> use pharma_db
> show collections
```

### **Step 3: Run Python Test**
```bash
cd backend
python test_mongodb.py
```

Expected output:
```
🧪 MONGODB CONNECTION TEST
======================================================================

Test 1: Connecting to MongoDB...
✅ PASS: Connection established

Test 2: Getting database instance...
✅ PASS: Database 'pharma_db' accessible

Test 3: Listing collections...
✅ PASS: Found 3 collections

... (more tests)

🎉 ALL TESTS PASSED!
```

### **Step 4: Check Health Endpoint**
```bash
# Start backend
cd backend
uvicorn main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "collections": ["workers", "products", "status"]
}
```

---

## Troubleshooting

### **Problem 1: "Connection Refused"**

**Symptoms:**
```
❌ MongoDB Connection Failed: Connection refused
```

**Solutions:**
1. **Start MongoDB service:**
   ```bash
   # Windows
   net start MongoDB
   
   # macOS
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```

2. **Check if port 27017 is in use:**
   ```bash
   # Windows
   netstat -ano | findstr :27017
   
   # macOS/Linux
   lsof -i :27017
   ```

3. **Verify MONGO_URL in `.env`:**
   ```
   MONGO_URL=mongodb://localhost:27017
   ```

---

### **Problem 2: "Server Selection Timeout"**

**Symptoms:**
```
❌ MongoDB Server Timeout: Server selection timeout
```

**Solutions:**
1. **Check firewall settings** - Allow port 27017
2. **Verify MongoDB is listening:**
   ```bash
   mongosh --eval "db.runCommand({ ping: 1 })"
   ```
3. **Check MongoDB logs:**
   ```bash
   # Windows
   C:\Program Files\MongoDB\Server\6.0\log\mongod.log
   
   # macOS
   /usr/local/var/log/mongodb/mongo.log
   
   # Linux
   /var/log/mongodb/mongod.log
   ```

---

### **Problem 3: "Authentication Failed"**

**Symptoms:**
```
❌ Authentication failed
```

**Solutions:**
1. **If using local MongoDB (no auth):**
   ```env
   MONGO_URL=mongodb://localhost:27017
   ```

2. **If MongoDB has authentication:**
   ```env
   MONGO_URL=mongodb://username:password@localhost:27017
   ```

3. **For MongoDB Atlas (cloud):**
   ```env
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pharma_db?retryWrites=true&w=majority
   ```

---

### **Problem 4: "Database Not Found"**

**Symptoms:**
- Collections are empty
- Database doesn't exist

**Solutions:**
- MongoDB creates databases automatically on first write
- Just run the application and add a worker/product
- Database will be created automatically

---

### **Problem 5: "Import Error in Routers"**

**Symptoms:**
```python
ModuleNotFoundError: No module named 'database'
```

**Solutions:**
1. **Ensure you're in the backend directory:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Check `__init__.py` exists:**
   ```bash
   # Should exist (even if empty)
   backend/__init__.py
   ```

3. **Use absolute imports if needed:**
   ```python
   # In routers files
   from database import get_database  # ✅ Correct
   import database  # ❌ Avoid
   ```

---

## Best Practices

### **1. Connection Pooling**
✅ Already configured in `database.py`:
- Max pool: 50 connections
- Min pool: 10 connections

### **2. Error Handling**
✅ All routes now use try-except with HTTPException

### **3. Graceful Shutdown**
✅ FastAPI lifecycle events handle connection cleanup

### **4. Health Checks**
✅ `/health` endpoint monitors database status

### **5. Index Creation (Recommended)**
```python
# Add to database.py after connection
def create_indexes():
    """Create indexes for better query performance"""
    db = get_database()
    
    # Index on worker wallet address
    db.workers.create_index("walletAddress", unique=True)
    
    # Index on product queries
    db.products.create_index("mfgDate")
    
    # Index on status tracking
    db.status.create_index([("productId", 1), ("timestamp", -1)])
    
    print("✅ Database indexes created")
```

---

## MongoDB Atlas (Cloud Option)

If you prefer cloud hosting:

1. **Sign up:** https://www.mongodb.com/cloud/atlas
2. **Create free cluster** (M0 - 512MB storage)
3. **Get connection string:**
   ```
   mongodb+srv://<username>:<password>@cluster.mongodb.net/pharma_db
   ```
4. **Update `.env`:**
   ```env
   MONGO_URL=mongodb+srv://your-username:your-password@cluster.mongodb.net/pharma_db?retryWrites=true&w=majority
   ```
5. **Whitelist IP address** in Atlas dashboard

---

## Changes Summary

### **✅ What Was Fixed:**

1. **database.py**
   - Added proper error handling (ConnectionFailure, ServerSelectionTimeoutError)
   - Added connection timeouts and pooling configuration
   - Added `get_database()` function for lazy connection
   - Added `close_mongodb_connection()` for cleanup
   - Added connection testing with ping
   - Graceful startup (app doesn't crash if MongoDB is down)

2. **main.py**
   - Added FastAPI lifecycle manager (`lifespan`)
   - Added MongoDB connection verification on startup
   - Added cleanup on shutdown
   - Added `/health` endpoint for monitoring

3. **routers/*.py**
   - Changed from `from database import db` to `from database import get_database`
   - All routes now call `db = get_database()` dynamically
   - Replaced tuple returns with `HTTPException`
   - Added ObjectId to string conversion for JSON serialization
   - Better error handling in all routes

4. **test_mongodb.py** (NEW)
   - Comprehensive connection testing
   - Write/read verification
   - Service status check
   - Troubleshooting guidance

---

## Running the Application

### **1. Start MongoDB**
```bash
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### **2. Test Connection**
```bash
cd backend
python test_mongodb.py
```

### **3. Start Backend**
```bash
cd backend
uvicorn main:app --reload
```

### **4. Verify Health**
```bash
curl http://localhost:8000/health
```

### **5. Check Logs**
Look for these messages:
```
🔌 Attempting to connect to MongoDB at mongodb://localhost:27017...
✅ MongoDB connection successful!
📦 Database 'pharma_db' accessible. Collections: []
🚀 Starting up application...
✅ MongoDB connection verified at startup
```

---

## Security Recommendations (Production)

1. **Enable Authentication:**
   ```bash
   # In mongod.conf
   security:
     authorization: enabled
   ```

2. **Use Strong Credentials:**
   ```env
   MONGO_URL=mongodb://admin:strong_password@localhost:27017/?authSource=admin
   ```

3. **Limit IP Access:**
   ```bash
   # In mongod.conf
   net:
     bindIp: 127.0.0.1
   ```

4. **Use Environment Variables** (never hardcode credentials)

5. **Enable SSL/TLS** for production deployments

---

## Support

If issues persist:
1. Check MongoDB logs
2. Run `python test_mongodb.py` for diagnostics
3. Verify `.env` configuration
4. Ensure MongoDB version >= 4.0
5. Check backend logs for detailed error messages

**MongoDB Documentation:** https://docs.mongodb.com/manual/
**PyMongo Documentation:** https://pymongo.readthedocs.io/
