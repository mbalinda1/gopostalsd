#!/usr/bin/env python3
"""
Script to check database tables and migration status
"""

import psycopg2
from server import create_server

def check_database():
    """Check database tables and migration status"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/gopostalsd')
        cur = conn.cursor()
        
        print("=== Database Connection Test ===")
        print("✅ PostgreSQL connection successful")
        
        # Check tables
        print("\n=== Tables in Database ===")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  No tables found")
        
        # Check alembic version
        print("\n=== Migration Status ===")
        try:
            cur.execute("SELECT version_num FROM alembic_version;")
            version = cur.fetchone()
            if version:
                print(f"  Current migration: {version[0]}")
            else:
                print("  No migration version found")
        except Exception as e:
            print(f"  Error checking migration version: {e}")
        
        # Check if pricing tables exist
        print("\n=== Pricing Tables Check ===")
        pricing_tables = [
            'product_options', 'product_pricing', 'carts', 
            'cart_items', 'shipping_options', 'product_variants'
        ]
        
        for table in pricing_tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            exists = cur.fetchone()[0]
            status = "✅" if exists else "❌"
            print(f"  {status} {table}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def check_flask_app():
    """Check Flask app database configuration"""
    try:
        print("\n=== Flask App Configuration ===")
        app = create_server('development')
        print(f"  Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Check if we can connect through Flask
        from server import database
        with app.app_context():
            # Try to query a table
            try:
                result = database.session.execute("SELECT 1").fetchone()
                print("  ✅ Flask database connection successful")
            except Exception as e:
                print(f"  ❌ Flask database connection failed: {e}")
                
    except Exception as e:
        print(f"❌ Flask app check failed: {e}")

if __name__ == "__main__":
    check_database()
    check_flask_app()
