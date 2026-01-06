#!/usr/bin/env python
"""
Quick script to restart backend with auto-sync
"""

import subprocess
import sys
import os

print("="*70)
print("🔄 RESTARTING BACKEND WITH AUTO-SYNC")
print("="*70)
print()
print("📋 Instructions:")
print()
print("1️⃣  Stop the current backend:")
print("   - Go to the terminal where backend is running")
print("   - Press Ctrl+C to stop it")
print()
print("2️⃣  Start backend with new auto-sync code:")
print("   cd E:\\PharmaDApp\\backend")
print("   uvicorn main:app --reload")
print()
print("3️⃣  Watch for auto-sync messages:")
print("   🚀 Starting up application...")
print("   ✅ MongoDB connection verified at startup")
print("   🔄 Auto-syncing data on startup...")
print("   ✅ Data already synchronized")
print("   ✅ Application ready!")
print()
print("="*70)
print()

# Offer to check if backend needs restart
response = input("Want to check current backend status? (y/n): ").strip().lower()

if response == 'y':
    try:
        import requests
        
        print("\n🔍 Checking current backend...")
        
        # Check health
        r = requests.get('http://localhost:8000/health', timeout=2)
        if r.status_code == 200:
            print("✅ Backend is running")
            
            # Check if sync endpoint exists (new feature)
            try:
                r2 = requests.get('http://localhost:8000/sync/status', timeout=2)
                if r2.status_code == 200:
                    print("✅ Auto-sync endpoints are available!")
                    print("   Backend is already updated!")
                    print()
                    print("Current sync status:")
                    import json
                    print(json.dumps(r2.json(), indent=2))
                else:
                    print("❌ Auto-sync endpoints NOT found")
                    print("   Backend is running OLD code")
                    print("   ⚠️  YOU NEED TO RESTART BACKEND")
            except:
                print("❌ Auto-sync endpoints NOT found")
                print("   Backend is running OLD code")
                print("   ⚠️  YOU NEED TO RESTART BACKEND")
        else:
            print("⚠️  Backend responded but with error")
            
    except Exception as e:
        print(f"❌ Backend not responding: {e}")
        print("   Start backend with: uvicorn main:app --reload")

print("\n" + "="*70)
