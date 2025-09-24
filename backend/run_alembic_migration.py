#!/usr/bin/env python3
"""
Script to run migration using Alembic directly
"""

import os
import sys
from alembic.config import Config
from alembic import command

def run_alembic_migration():
    """Run migration using Alembic directly"""
    try:
        # Get the migrations directory path
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        alembic_cfg = os.path.join(migrations_dir, 'alembic.ini')
        
        if not os.path.exists(alembic_cfg):
            print(f"Alembic config not found at: {alembic_cfg}")
            sys.exit(1)
        
        # Create Alembic config
        config = Config(alembic_cfg)
        
        print("Current migration status:")
        try:
            command.current(config)
        except Exception as e:
            print(f"Error getting current status: {e}")
        
        print("\nRunning migration...")
        command.upgrade(config, "head")
        print("Migration completed successfully!")
        
        print("\nNew migration status:")
        command.current(config)
        
    except Exception as e:
        print(f"Error running migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_alembic_migration()
