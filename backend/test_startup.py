#!/usr/bin/env python3
"""
Test script to verify the startup functionality works correctly.
This script tests the database initialization and unclassified product type creation.
"""
import sys
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

def test_startup():
    """Test the startup functionality"""
    try:
        print("🧪 Testing server startup functionality...")
        print("=" * 50)
        
        # Test 1: Import the startup module
        print("📦 Testing imports...")
        from server.startup import ensure_database_structures, verify_database_health
        print("✅ Startup module imported successfully")
        
        # Test 2: Create a minimal Flask app context
        print("\n📱 Testing Flask app context...")
        from server import create_server
        app = create_server()
        
        with app.app_context():
            print("✅ Flask app context created successfully")
            
            # Test 3: Test database health check
            print("\n🔍 Testing database health check...")
            db_healthy = verify_database_health()
            if db_healthy:
                print("✅ Database health check passed")
            else:
                print("❌ Database health check failed")
                return False
            
            # Test 4: Test database structure initialization
            print("\n🔧 Testing database structure initialization...")
            init_success = ensure_database_structures()
            if init_success:
                print("✅ Database structure initialization completed successfully")
            else:
                print("❌ Database structure initialization failed")
                return False
            
            # Test 5: Verify unclassified type exists
            print("\n📋 Verifying unclassified product type...")
            from server.models.print_product import PrintProductType
            from server import database as db
            
            unclassified_type = db.session.get(PrintProductType, 0)
            if unclassified_type:
                print(f"✅ Unclassified type verified: {unclassified_type.name} (ID: {unclassified_type.id})")
                print(f"   Description: {unclassified_type.description}")
                print(f"   Category ID: {unclassified_type.category_id}")
            else:
                print("❌ Unclassified type not found in database")
                return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Startup functionality is working correctly.")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1) 