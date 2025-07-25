#!/usr/bin/env python3
"""
Database migration script to add missing columns to existing tables.
"""

import os
import sys
from sqlalchemy import text
from app import app, db

def migrate_database():
    """Add missing columns to existing database tables"""
    with app.app_context():
        try:
            # Check if location column exists in Device table
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'device' AND column_name = 'location'
            """))
            
            if not result.fetchone():
                print("Adding 'location' column to Device table...")
                db.session.execute(text("""
                    ALTER TABLE device 
                    ADD COLUMN location VARCHAR(128) DEFAULT 'auto'
                """))
                db.session.commit()
                print("✅ Successfully added 'location' column to Device table")
            else:
                print("✅ 'location' column already exists in Device table")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            return False
            
        return True

if __name__ == "__main__":
    print("Running database migration...")
    if migrate_database():
        print("✅ Database migration completed successfully")
    else:
        print("❌ Database migration failed")
        sys.exit(1) 