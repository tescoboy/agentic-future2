#!/usr/bin/env python3
"""
Script to create platform deployments for Peer39 signals.
"""

import sqlite3
import os
from datetime import datetime

def create_platform_deployments():
    """Create platform deployments for Peer39 signals."""
    
    # Connect to database
    db_path = os.getenv('DATABASE_PATH', 'signals_agent.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all Peer39 signals
    cursor.execute("SELECT id FROM signal_segments WHERE data_provider = 'Peer39'")
    peer39_signals = cursor.fetchall()
    
    print(f"Found {len(peer39_signals)} Peer39 signals")
    
    # Platforms to deploy to (must match valid_platforms in api_models.py)
    platforms = [
        'index-exchange',
        'the-trade-desk', 
        'openx',
        'pubmatic',
        'dv360',
        'tradedesk',
        'amazon',
        'google-ads'
    ]
    
    # Clear existing Peer39 platform deployments
    cursor.execute("""
        DELETE FROM platform_deployments 
        WHERE signals_agent_segment_id IN (
            SELECT id FROM signal_segments WHERE data_provider = 'Peer39'
        )
    """)
    print("Cleared existing Peer39 platform deployments")
    
    # Create platform deployments for each signal
    deployment_count = 0
    
    for (signal_id,) in peer39_signals:
        for platform in platforms:
            try:
                # Generate platform-specific segment ID
                platform_segment_id = f"{platform}_{signal_id.replace('peer39_', '')}"
                
                # Insert platform deployment
                cursor.execute("""
                    INSERT INTO platform_deployments (
                        signals_agent_segment_id, platform, decisioning_platform_segment_id, 
                        scope, is_live, deployed_at, estimated_activation_duration_minutes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal_id, platform, platform_segment_id,
                    'platform-wide', 1, datetime.now().isoformat(), 60
                ))
                
                deployment_count += 1
                
            except Exception as e:
                print(f"Error creating deployment for {signal_id} on {platform}: {e}")
                continue
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Successfully created {deployment_count} platform deployments")
    
    # Verify the data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM platform_deployments")
    total_deployments = cursor.fetchone()[0]
    print(f"Total platform deployments in database: {total_deployments}")
    
    # Show some examples
    cursor.execute("""
        SELECT pd.signals_agent_segment_id, pd.platform, ss.name 
        FROM platform_deployments pd
        JOIN signal_segments ss ON pd.signals_agent_segment_id = ss.id
        WHERE ss.data_provider = 'Peer39'
        LIMIT 10
    """)
    examples = cursor.fetchall()
    print("\nSample platform deployments:")
    for signal_id, platform, name in examples:
        print(f"  - {signal_id} ({platform}): {name}")
    
    conn.close()

if __name__ == "__main__":
    create_platform_deployments()
