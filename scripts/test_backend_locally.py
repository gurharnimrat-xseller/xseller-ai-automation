#!/usr/bin/env python3
"""
Local Backend Testing Script

Thoroughly tests the backend to ensure it's ready for Railway deployment.
Run this script before deploying to Railway to verify all fixes are working.
"""

import requests
import time
import sys
import subprocess
import signal
import os
from pathlib import Path


def start_backend():
    """Start the backend server."""
    print("🚀 Starting backend server...")
    backend_dir = Path(__file__).parent.parent / "backend"
    
    # Start the server in the background
    process = subprocess.Popen(
        ["python", "-m", "app.main"],
        cwd=str(backend_dir),
        env={**os.environ, "PORT": "8000"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    max_wait = 30
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=1)
            if response.status_code == 200:
                print(f"✅ Backend started successfully in {time.time() - start_time:.2f}s")
                return process
        except requests.exceptions.RequestException:
            time.sleep(0.5)
    
    print("❌ Backend failed to start within 30 seconds")
    process.kill()
    return None


def test_health_endpoint():
    """Test the /api/health endpoint."""
    print("\n📋 Testing /api/health endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("api") == "healthy" and data.get("database") == "connected":
                print("   ✅ Health check PASSED")
                return True
        
        print("   ❌ Health check FAILED")
        return False
    except Exception as e:
        print(f"   ❌ Health check ERROR: {e}")
        return False


def test_news_ingest_endpoint():
    """Test the /api/news/ingest endpoint."""
    print("\n📋 Testing /api/news/ingest endpoint...")
    try:
        payload = {
            "sources": ["newsapi", "mock"],
            "limit_per_source": 20
        }
        response = requests.post(
            "http://localhost:8000/api/news/ingest",
            json=payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "job_id" in data and "status" in data:
                print("   ✅ News ingest endpoint PASSED")
                return True
        
        print("   ❌ News ingest endpoint FAILED")
        return False
    except Exception as e:
        print(f"   ❌ News ingest endpoint ERROR: {e}")
        return False


def test_routes_registered():
    """Test that all expected routes are registered."""
    print("\n📋 Testing route registration...")
    try:
        response = requests.get("http://localhost:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})
            
            # Check for critical routes
            critical_routes = [
                "/api/health",
                "/api/news/ingest",
                "/api/news/rank",
                "/api/content/queue"
            ]
            
            all_present = True
            for route in critical_routes:
                if route in paths:
                    print(f"   ✅ {route} is registered")
                else:
                    print(f"   ❌ {route} is NOT registered")
                    all_present = False
            
            if all_present:
                print(f"   ✅ All {len(paths)} routes registered successfully")
                return True
            else:
                print("   ❌ Some critical routes are missing")
                return False
        
        print("   ❌ Could not fetch OpenAPI spec")
        return False
    except Exception as e:
        print(f"   ❌ Route registration check ERROR: {e}")
        return False


def main():
    """Main test execution."""
    print("=" * 80)
    print("🧪 BACKEND LOCAL TESTING SUITE")
    print("=" * 80)
    
    # Start backend
    process = start_backend()
    if not process:
        print("\n❌ FAILED: Backend did not start")
        return 1
    
    try:
        # Run tests
        results = []
        results.append(("Health Endpoint", test_health_endpoint()))
        results.append(("News Ingest Endpoint", test_news_ingest_endpoint()))
        results.append(("Route Registration", test_routes_registered()))
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        all_passed = True
        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {test_name}")
            if not passed:
                all_passed = False
        
        print("=" * 80)
        
        if all_passed:
            print("🎉 All tests PASSED! Backend is ready for Railway deployment.")
            return 0
        else:
            print("❌ Some tests FAILED. Fix issues before deploying to Railway.")
            return 1
    
    finally:
        # Stop backend
        print("\n🛑 Stopping backend server...")
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=5)
        print("✅ Backend stopped")


if __name__ == "__main__":
    sys.exit(main())
