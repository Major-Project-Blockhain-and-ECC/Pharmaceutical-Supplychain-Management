# 🚀 MONGODB CONNECTION - QUICK REFERENCE

## Test Connection (Do This First!)
```bash
cd backend
python test_mongodb.py
```

## Start Backend
```bash
cd backend
uvicorn main:app --reload
```

## Check Health
```bash
curl http://localhost:8000/health
```

## If MongoDB Not Running

**Windows:**
```powershell
net start MongoDB
```

**macOS:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Connection refused | Start MongoDB service |
| Timeout | Check `.env` MONGO_URL |
| Import errors | Run from `backend` directory |
| ObjectId errors | **FIXED** ✅ |

## What Was Fixed

✅ Error handling added  
✅ Connection pooling configured  
✅ Graceful startup/shutdown  
✅ Health endpoint: `/health`  
✅ All routers use `get_database()`  
✅ HTTPException instead of tuples  
✅ ObjectId serialization  
✅ Test script: `test_mongodb.py`  

## Files Changed

- `backend/database.py` - Complete rewrite
- `backend/main.py` - Added lifecycle + health
- `backend/routers/*.py` - Dynamic DB + error handling
- `backend/test_mongodb.py` - **NEW** test script

## Full Documentation

📖 **Complete Guide:** [MONGODB_SETUP_GUIDE.md](MONGODB_SETUP_GUIDE.md)  
📋 **Detailed Summary:** [MONGODB_FIX_SUMMARY.md](MONGODB_FIX_SUMMARY.md)

## Support

Test failed? Check:
1. MongoDB running: `mongosh`
2. Environment: `backend/.env`
3. Port 27017: `netstat -ano | findstr :27017`
4. Logs: Run `test_mongodb.py` for diagnostics
