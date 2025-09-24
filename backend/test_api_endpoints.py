#!/usr/bin/env python3
"""
Test script for API endpoints.
This script tests the pricing API endpoints directly.
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the pricing API endpoints."""
    base_url = "http://localhost:5000/api/pricing"
    
    print("🔍 Testing API Endpoints...")
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Test 1: Get product options
    print("\n1. Testing product options endpoint...")
    try:
        response = requests.get(f"{base_url}/products/1/options?store_code=6")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product options retrieved: {len(data)} option groups")
            for group in data[:3]:  # Show first 3 groups
                print(f"   - {group['group']}: {len(group['options'])} options")
        else:
            print(f"❌ Failed to get product options: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing product options: {e}")
    
    # Test 2: Calculate price
    print("\n2. Testing price calculation endpoint...")
    try:
        payload = {
            "product_id": 1,
            "options": [4, 5, 30, 79, 93, 540],  # Sample options
            "store_code": 6
        }
        response = requests.post(f"{base_url}/products/1/price", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Price calculated: ${data.get('price', 'N/A')}")
        else:
            print(f"❌ Failed to calculate price: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing price calculation: {e}")
    
    # Test 3: Get or create cart
    print("\n3. Testing cart creation endpoint...")
    try:
        response = requests.get(f"{base_url}/cart?session_id=test123&store_code=6")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cart created: ID {data.get('id', 'N/A')}")
        else:
            print(f"❌ Failed to create cart: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing cart creation: {e}")

if __name__ == "__main__":
    test_api_endpoints()
