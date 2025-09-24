#!/usr/bin/env python3
"""
Test script for Sinalite pricing integration.
This script tests the complete pricing flow from API to frontend.
"""

import os
import sys
import json
from flask import Flask

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import create_server, database
from server.thirdparty.sinalite import SinaliteAdapter
from server.services.pricing_service import PricingService

def test_sinalite_connection():
    """Test basic Sinalite API connection and authentication."""
    print("🔍 Testing Sinalite API Connection...")
    
    app = create_server()
    with app.app_context():
        sinalite = SinaliteAdapter(app)
        
        # Test authentication
        if sinalite.authenticate():
            print("✅ Sinalite authentication successful")
        else:
            print("❌ Sinalite authentication failed")
            return False
        
        # Test getting products
        products = sinalite.get_products()
        if products:
            print(f"✅ Retrieved {len(products)} products from Sinalite")
            print(f"   Sample product: {products[0] if products else 'None'}")
        else:
            print("❌ Failed to retrieve products")
            return False
        
        return True

def test_product_details():
    """Test getting product details and options."""
    print("\n🔍 Testing Product Details...")
    
    app = create_server()
    with app.app_context():
        sinalite = SinaliteAdapter(app)
        sinalite.authenticate()
        
        # Get first product
        products = sinalite.get_products()
        if not products:
            print("❌ No products available for testing")
            return False
        
        product_id = products[0]['id']
        print(f"   Testing with product ID: {product_id}")
        
        # Get product details
        details = sinalite.get_product_details(product_id, 6)  # Canada store
        if details and len(details) >= 3:
            print("✅ Product details retrieved successfully")
            print(f"   Options count: {len(details[0])}")
            print(f"   Pricing combinations: {len(details[1])}")
            print(f"   Metadata: {len(details[2])}")
            
            # Show sample options
            if details[0]:
                print("   Sample options:")
                for i, option in enumerate(details[0][:5]):  # Show first 5
                    print(f"     {option}")
                if len(details[0]) > 5:
                    print(f"     ... and {len(details[0]) - 5} more")
            
            return True
        else:
            print("❌ Failed to retrieve product details")
            return False

def test_pricing_calculation():
    """Test pricing calculation with sample options."""
    print("\n🔍 Testing Pricing Calculation...")
    
    app = create_server()
    with app.app_context():
        sinalite = SinaliteAdapter(app)
        sinalite.authenticate()
        pricing_service = PricingService(sinalite)
        
        # Get first product
        products = sinalite.get_products()
        if not products:
            print("❌ No products available for testing")
            return False
        
        product_id = products[0]['id']
        print(f"   Testing with product ID: {product_id}")
        
        # Get product options
        options = pricing_service.get_product_options(product_id, 6)
        if not options:
            print("❌ No options available for testing")
            return False
        
        print(f"   Available option groups: {[group['group'] for group in options]}")
        
        # Try to calculate price with first available options
        selected_options = []
        for group in options:
            if group['options']:
                selected_options.append(group['options'][0]['id'])
                print(f"   Selected {group['group']}: {group['options'][0]['name']} (ID: {group['options'][0]['id']})")
        
        if selected_options:
            print(f"   Testing with option IDs: {selected_options}")
            
            # Calculate price
            pricing = pricing_service.calculate_product_price(product_id, selected_options, 6)
            if pricing:
                print(f"✅ Price calculation successful: ${pricing.get('price', 'N/A')}")
                return True
            else:
                print("❌ Price calculation failed")
                return False
        else:
            print("❌ No options selected for testing")
            return False

def test_key_based_pricing():
    """Test key-based pricing directly."""
    print("\n🔍 Testing Key-Based Pricing...")
    
    app = create_server()
    with app.app_context():
        sinalite = SinaliteAdapter(app)
        sinalite.authenticate()
        
        # Get first product
        products = sinalite.get_products()
        if not products:
            print("❌ No products available for testing")
            return False
        
        product_id = products[0]['id']
        
        # Get product details to find a valid key
        details = sinalite.get_product_details(product_id, 6)
        if not details or len(details) < 2:
            print("❌ No pricing data available")
            return False
        
        # Look for a pricing key in the second array
        pricing_combinations = details[1]
        if not pricing_combinations:
            print("❌ No pricing combinations available")
            return False
        
        # Find a key with a price - pricing combinations are in format [price, key]
        valid_key = None
        for combo in pricing_combinations:
            if isinstance(combo, dict) and 'key' in combo and 'price' in combo:
                valid_key = combo['key']
                print(f"   Testing with key: {valid_key}")
                break
            elif isinstance(combo, list) and len(combo) >= 2:
                # Format: [price, key] or similar
                valid_key = str(combo[1])  # Second element is usually the key
                print(f"   Testing with key: {valid_key}")
                break
        
        if not valid_key:
            print("❌ No valid pricing key found")
            return False
        
        # Test key-based pricing
        price_data = sinalite.get_price_by_key(product_id, valid_key)
        if price_data and 'price' in price_data:
            print(f"✅ Key-based pricing successful: ${price_data['price']}")
            return True
        else:
            print("❌ Key-based pricing failed")
            return False

def main():
    """Run all tests."""
    print("🚀 Starting Sinalite Pricing Integration Tests\n")
    
    tests = [
        ("Sinalite Connection", test_sinalite_connection),
        ("Product Details", test_product_details),
        ("Pricing Calculation", test_pricing_calculation),
        ("Key-Based Pricing", test_key_based_pricing)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("🎉 All tests passed! The pricing system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and API credentials.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
