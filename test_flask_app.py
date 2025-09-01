#!/usr/bin/env python3
"""
Test script for ShopAssist AI Flask Backend
Tests basic functionality without requiring API keys
"""

import sys
import requests
import time
import subprocess
import os
from urllib.parse import urljoin

def test_flask_app():
    """Test the Flask application functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing ShopAssist AI Flask Backend")
    print("=" * 50)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(urljoin(base_url, "/health"), timeout=5)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("   ✅ Health endpoint working")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health endpoint connection failed: {e}")
        return False
    
    # Test 2: Main page
    print("2. Testing main page...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200 and "ShopAssist AI Chat" in response.text:
            print("   ✅ Main page loads correctly")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Main page connection failed: {e}")
        return False
    
    # Test 3: Static files
    print("3. Testing static files...")
    static_files = ["/static/style.css", "/static/script.js"]
    for static_file in static_files:
        try:
            response = requests.get(urljoin(base_url, static_file), timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {static_file} accessible")
            else:
                print(f"   ❌ {static_file} failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {static_file} connection failed: {e}")
            return False
    
    # Test 4: Chat endpoint (expect error without API key)
    print("4. Testing chat endpoint...")
    try:
        response = requests.post(
            urljoin(base_url, "/chat"),
            json={"message": "test"},
            timeout=10
        )
        if response.status_code == 500:  # Expected without API key
            print("   ✅ Chat endpoint responds (API key required for full functionality)")
        elif response.status_code == 400:
            print("   ✅ Chat endpoint validates input correctly")
        else:
            print(f"   ⚠️  Chat endpoint returned unexpected status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Chat endpoint connection failed: {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("\nTo test full chat functionality:")
    print("1. Set OPENAI_API_KEY in your environment")
    print("2. Restart the Flask app")
    print("3. Visit http://127.0.0.1:5000 and try chatting")
    
    return True

def check_imports():
    """Check if all required modules can be imported"""
    print("🔍 Checking imports...")
    try:
        from app import app
        print("   ✅ Flask app imports successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

def main():
    """Main test function"""
    print("ShopAssist AI Flask Backend Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Test imports
    if not check_imports():
        print("\n❌ Import tests failed. Please check your setup.")
        sys.exit(1)
    
    # Check if Flask app is running
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=2)
        app_running = True
    except requests.exceptions.RequestException:
        app_running = False
    
    if not app_running:
        print("\n⚠️  Flask app is not running.")
        print("Please start it with: python app.py")
        print("Then run this test again.")
        sys.exit(1)
    
    # Run tests
    if test_flask_app():
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()