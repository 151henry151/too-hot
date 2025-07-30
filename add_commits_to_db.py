#!/usr/bin/env python3
"""
Script to manually add commit information to the database
This avoids using GitHub API quota for commits we already have information about.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, CommitInfo

def add_commit_to_db(commit_hash, commit_message, commit_date, lines_added, lines_deleted, time_spent_minutes):
    """Add a single commit to the database"""
    try:
        # Check if commit already exists
        existing = CommitInfo.query.filter_by(commit_hash=commit_hash).first()
        if existing:
            print(f"⚠️  Commit {commit_hash[:7]} already exists in database")
            return False
        
        # Create new commit record
        commit_info = CommitInfo(
            commit_hash=commit_hash,
            commit_message=commit_message,
            commit_date=commit_date,
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            lines_changed=lines_added + lines_deleted,
            time_spent_minutes=time_spent_minutes
        )
        
        db.session.add(commit_info)
        db.session.commit()
        print(f"✅ Added commit {commit_hash[:7]} to database")
        return True
        
    except Exception as e:
        print(f"❌ Error adding commit {commit_hash[:7]}: {e}")
        db.session.rollback()
        return False

def add_sample_commits():
    """Add some sample commits to the database"""
    commits_data = [
        # Format: (hash, message, date, lines_added, lines_deleted, time_spent_minutes)
        # Add your commit data here
        # Example:
        # ("abc1234567890abcdef1234567890abcdef1234", "Fix text wrapping in mobile app", datetime(2024, 1, 15, 10, 30, 0), 25, 5, 45),
    ]
    
    with app.app_context():
        success_count = 0
        for commit_data in commits_data:
            if add_commit_to_db(*commit_data):
                success_count += 1
        
        print(f"\n✅ Successfully added {success_count} commits to database")

def add_commit_interactive():
    """Interactive function to add commits one by one"""
    with app.app_context():
        while True:
            print("\n" + "="*50)
            print("Add Commit to Database")
            print("="*50)
            
            commit_hash = input("Commit hash (or 'quit' to exit): ").strip()
            if commit_hash.lower() == 'quit':
                break
            
            commit_message = input("Commit message: ").strip()
            date_str = input("Commit date (YYYY-MM-DD HH:MM:SS): ").strip()
            
            try:
                commit_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD HH:MM:SS")
                continue
            
            try:
                lines_added = int(input("Lines added: ").strip())
                lines_deleted = int(input("Lines deleted: ").strip())
                time_spent = int(input("Time spent (minutes): ").strip())
            except ValueError:
                print("❌ Invalid number format")
                continue
            
            if add_commit_to_db(commit_hash, commit_message, commit_date, lines_added, lines_deleted, time_spent):
                print("✅ Commit added successfully!")
            else:
                print("❌ Failed to add commit")

if __name__ == "__main__":
    print("🔄 Commit Database Manager")
    print("1. Add sample commits (edit script first)")
    print("2. Add commits interactively")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        add_sample_commits()
    elif choice == "2":
        add_commit_interactive()
    else:
        print("❌ Invalid choice") 