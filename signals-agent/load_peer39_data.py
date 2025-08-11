#!/usr/bin/env python3
"""
Script to load Peer39 segments from sample_data.json into the database.
"""

import json
import sqlite3
import os
from datetime import datetime

def load_peer39_data():
    """Load Peer39 segments from sample_data.json into the database."""
    
    # Read the sample data
    with open('sample_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"Found {data['totalCount']} segments in sample_data.json")
    
    # Connect to database
    db_path = os.getenv('DATABASE_PATH', 'signals_agent.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing signal_segments data
    cursor.execute("DELETE FROM signal_segments")
    print("Cleared existing signal_segments data")
    
    # Also clear platform deployments to avoid orphaned records
    cursor.execute("DELETE FROM platform_deployments")
    print("Cleared existing platform_deployments data")
    
    # Insert Peer39 segments
    segments = data['segments']
    inserted_count = 0
    
    for segment in segments:
        try:
            # Extract data from Peer39 format
            segment_id = f"peer39_{segment['segmentID']}"
            name = segment['externalSegmentName']
            description = f"Peer39 segment: {name}"
            data_provider = "Peer39"
            signal_type = "audience"
            catalog_access = "public"
            
            # Generate a reasonable price based on segment type
            if "Luxury" in name or "High-Value" in name:
                base_cpm = 15.0
            elif "Automotive" in name or "Travel" in name:
                base_cpm = 12.0
            elif "Health" in name or "Diet" in name:
                base_cpm = 10.0
            else:
                base_cpm = 8.0
            
            # Generate coverage percentage (random but realistic)
            import random
            coverage_percentage = random.uniform(2.0, 25.0)
            
            # Generate revenue share (random but realistic)
            revenue_share_percentage = random.uniform(10.0, 30.0)
            
            # Insert into database
            cursor.execute("""
                INSERT INTO signal_segments (
                    id, name, description, data_provider, signal_type, 
                    catalog_access, base_cpm, coverage_percentage, revenue_share_percentage,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                segment_id, name, description, data_provider, signal_type,
                catalog_access, base_cpm, coverage_percentage, revenue_share_percentage,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            
            inserted_count += 1
            
        except Exception as e:
            print(f"Error inserting segment {segment.get('externalSegmentName', 'Unknown')}: {e}")
            continue
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Successfully inserted {inserted_count} Peer39 segments into database")
    
    # Verify the data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM signal_segments")
    total_count = cursor.fetchone()[0]
    print(f"Total signals in database: {total_count}")
    
    # Show some examples
    cursor.execute("SELECT name, data_provider FROM signal_segments LIMIT 10")
    examples = cursor.fetchall()
    print("\nSample segments:")
    for name, data_provider in examples:
        print(f"  - {name} ({data_provider})")
    
    conn.close()

if __name__ == "__main__":
    load_peer39_data()
