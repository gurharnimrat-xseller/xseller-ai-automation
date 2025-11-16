#!/usr/bin/env python3
"""
Ping Backend Health Check Script

Tests connectivity to the backend API and verifies the /api/health endpoint.
Usage:
    python scripts/ping_backend.py
    
Environment:
    BACKEND_API_BASE_URL: The base URL of the backend API (default: http://localhost:8000)
"""

import os
import sys
import requests
from typing import Dict, Any


def ping_health_endpoint(base_url: str) -> Dict[str, Any]:
    """
    Ping the /api/health endpoint and return the response.
    
    Args:
        base_url: Base URL of the backend API
        
    Returns:
        Response JSON or error details
    """
    health_url = f"{base_url.rstrip('/')}/api/health"
    
    print(f"🏥 Pinging health endpoint: {health_url}")
    print("=" * 80)
    
    try:
        response = requests.get(health_url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print("\nResponse Body:")
        try:
            json_response = response.json()
            import json
            print(json.dumps(json_response, indent=2))
        except Exception:
            print(response.text)
        
        print("=" * 80)
        
        if response.status_code == 200:
            print("✅ Health check PASSED")
            return {"success": True, "data": response.json()}
        else:
            print(f"❌ Health check FAILED with status {response.status_code}")
            return {"success": False, "status_code": response.status_code, "error": response.text}
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: Cannot reach {health_url}")
        print(f"   Error: {e}")
        print("=" * 80)
        return {"success": False, "error": "connection_error", "details": str(e)}
    
    except requests.exceptions.Timeout as e:
        print(f"❌ TIMEOUT ERROR: Request timed out after 10 seconds")
        print(f"   Error: {e}")
        print("=" * 80)
        return {"success": False, "error": "timeout", "details": str(e)}
    
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("=" * 80)
        return {"success": False, "error": "unexpected_error", "details": str(e)}


def main() -> int:
    """
    Main entry point for the health check script.
    
    Returns:
        Exit code: 0 on success, 1 on failure
    """
    # Get base URL from environment or use default
    base_url = os.getenv("BACKEND_API_BASE_URL", "http://localhost:8000")
    
    if not base_url or base_url.strip() == "":
        print("❌ ERROR: BACKEND_API_BASE_URL is not set or is empty")
        print("   Please set the environment variable:")
        print("   export BACKEND_API_BASE_URL=https://your-backend-url.com")
        return 1
    
    print("\n🔍 Backend Health Check")
    print("=" * 80)
    print(f"Target: {base_url}")
    print("=" * 80)
    print()
    
    # Run health check
    result = ping_health_endpoint(base_url)
    
    # Return appropriate exit code
    if result.get("success"):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
