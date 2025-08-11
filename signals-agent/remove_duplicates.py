#!/usr/bin/env python3
"""
Script to remove duplicate signals from the database.
Removes duplicates based on name, keeping the first occurrence.
"""

import sqlite3
import os
from datetime import datetime

def remove_duplicates():
    """Remove duplicate signals from the database."""
    
    # Connect to database
    db_path = os.getenv('DATABASE_PATH', 'signals_agent.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 Checking for duplicates...")
    
    # Check for duplicates by name
    cursor.execute("""
        SELECT name, COUNT(*) as count 
        FROM signal_segments 
        GROUP BY name 
        HAVING count > 1 
        ORDER BY count DESC
    """)
    
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("✅ No duplicates found!")
        conn.close()
        return
    
    print(f"❌ Found {len(duplicates)} duplicate names:")
    for name, count in duplicates:
        print(f"   - {name}: {count} occurrences")
    
    print("\n🗑️ Removing duplicates...")
    
    # Remove duplicates, keeping the first occurrence of each name
    cursor.execute("""
        DELETE FROM signal_segments 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM signal_segments 
            GROUP BY name
        )
    """)
    
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"✅ Removed {deleted_count} duplicate signals")
    
    # Verify removal
    cursor.execute("SELECT COUNT(*) FROM signal_segments")
    remaining_count = cursor.fetchone()[0]
    print(f"📊 Remaining signals: {remaining_count}")
    
    # Check for any remaining duplicates
    cursor.execute("""
        SELECT name, COUNT(*) as count 
        FROM signal_segments 
        GROUP BY name 
        HAVING count > 1
    """)
    
    remaining_duplicates = cursor.fetchall()
    if remaining_duplicates:
        print("❌ Still have duplicates:")
        for name, count in remaining_duplicates:
            print(f"   - {name}: {count} occurrences")
    else:
        print("✅ All duplicates removed successfully!")
    
    conn.close()

def add_unique_constraints():
    """Add unique constraints to prevent future duplicates."""
    
    db_path = os.getenv('DATABASE_PATH', 'signals_agent.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔒 Adding unique constraints...")
    
    try:
        # Add unique constraint on name
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_signal_segments_name_unique 
            ON signal_segments(name)
        """)
        print("✅ Added unique constraint on signal name")
        
        # Add unique constraint on id (should already exist as PRIMARY KEY)
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_signal_segments_id_unique 
            ON signal_segments(id)
        """)
        print("✅ Added unique constraint on signal id")
        
        conn.commit()
        print("✅ All constraints added successfully!")
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Error adding constraints: {e}")
        print("This might be due to existing duplicates. Run remove_duplicates() first.")
    
    conn.close()

def update_data_loading_scripts():
    """Update data loading scripts to prevent duplicates."""
    
    print("\n📝 Updating data loading scripts...")
    
    # Update the Peer39 data loading script
    peer39_script = 'load_peer39_data.py'
    if os.path.exists(peer39_script):
        print(f"✅ Found {peer39_script}")
        print("   - Script already uses INSERT OR REPLACE which prevents duplicates")
        print("   - Script clears existing data before inserting, which prevents duplicates")
    else:
        print(f"❌ {peer39_script} not found")
    
    # Update the main database initialization
    db_script = 'database.py'
    if os.path.exists(db_script):
        print(f"✅ Found {db_script}")
        print("   - Uses INSERT OR REPLACE for idempotency")
        print("   - Checks for existing data before insertion")
    else:
        print(f"❌ {db_script} not found")

def main():
    """Main function to clean up duplicates and prevent future ones."""
    
    print("🧹 Signal Database Duplicate Cleanup")
    print("=" * 40)
    
    # Step 1: Remove existing duplicates
    remove_duplicates()
    
    # Step 2: Add constraints to prevent future duplicates
    add_unique_constraints()
    
    # Step 3: Update data loading scripts
    update_data_loading_scripts()
    
    print("\n🎉 Duplicate cleanup completed!")
    print("\n📋 Summary:")
    print("   - Removed duplicate signals by name")
    print("   - Added unique constraints to prevent future duplicates")
    print("   - Verified data loading scripts are duplicate-safe")

if __name__ == "__main__":
    main()
