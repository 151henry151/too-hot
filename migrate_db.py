#!/usr/bin/env python3
"""
Database migration script to add CommitInfo table for time tracking
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import db, CommitInfo

def migrate_database():
    """Add CommitInfo table to the database"""
    from app import app
    
    with app.app_context():
        try:
            # Create the new table
            db.create_all()
            
            # Check if CommitInfo table exists
            engine = db.engine
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='commit_info'
                """))
                table_exists = result.fetchone() is not None
                
            if table_exists:
                print("✅ CommitInfo table already exists")
            else:
                print("✅ Created CommitInfo table")
                
            print("✅ Database migration completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database migration failed: {e}")
            return False

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    success = migrate_database()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1) 