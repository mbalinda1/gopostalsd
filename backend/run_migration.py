#!/usr/bin/env python3
"""
Script to manually run database migrations
"""

import os
import sys
from flask import Flask
from flask_migrate import upgrade, current, history

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migration():
    """Run database migration"""
    try:
        # Import your Flask app
        from server import create_server
        
        # Create app instance
        app = create_server("development")
        
        with app.app_context():
            print("Current migration status:")
            try:
                current_rev = current()
                print(f"Current revision: {current_rev}")
            except Exception as e:
                print(f"No current revision found: {e}")
            
            print("\nMigration history:")
            try:
                history_info = history()
                for rev in history_info:
                    print(f"  {rev.revision}: {rev.doc}")
            except Exception as e:
                print(f"Error getting history: {e}")
            
            print("\nRunning migration...")
            upgrade()
            print("Migration completed successfully!")
            
            print("\nNew migration status:")
            current_rev = current()
            print(f"Current revision: {current_rev}")
            
    except Exception as e:
        print(f"Error running migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
