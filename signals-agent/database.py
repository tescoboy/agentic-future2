"""Database initialization and sample data for the Signals Agent."""

import os
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database with tables and sample data - idempotent."""
    db_path = os.environ.get('DATABASE_PATH', 'signals_agent.db')
    logger.info(f"Initializing database at: {db_path}")
    
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()
    
    try:
        # Enable WAL mode for better concurrent access
        cursor.execute("PRAGMA journal_mode=WAL")
        logger.info("WAL mode enabled")
        
        # Create tables
        create_tables(cursor)
        logger.info("Tables created/verified")
        
        # Insert sample data (idempotent)
        insert_sample_data(cursor)
        logger.info("Sample data inserted/verified")
        
        conn.commit()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables(cursor: sqlite3.Cursor):
    """Create all database tables with proper indices."""
    
    # Signal segments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signal_segments (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            data_provider TEXT NOT NULL,
            coverage_percentage REAL NOT NULL,
            signal_type TEXT NOT NULL CHECK (signal_type IN ('private', 'marketplace', 'audience', 'bidding', 'contextual', 'geographical', 'temporal', 'environmental')),
            catalog_access TEXT NOT NULL CHECK (catalog_access IN ('public', 'personalized', 'private')),
            base_cpm REAL NOT NULL,
            revenue_share_percentage REAL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Principals table (for access control)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS principals (
            principal_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            access_level TEXT NOT NULL CHECK (access_level IN ('public', 'personalized', 'private')),
            description TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # Principal segment access table (for personalized catalogs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS principal_segment_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            principal_id TEXT NOT NULL,
            signals_agent_segment_id TEXT NOT NULL,
            access_type TEXT NOT NULL CHECK (access_type IN ('granted', 'custom_pricing')),
            custom_cpm REAL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (principal_id) REFERENCES principals (principal_id),
            FOREIGN KEY (signals_agent_segment_id) REFERENCES signal_segments (id),
            UNIQUE(principal_id, signals_agent_segment_id)
        )
    """)
    
    # Platform deployments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signals_agent_segment_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            account TEXT,
            decisioning_platform_segment_id TEXT,
            scope TEXT NOT NULL CHECK (scope IN ('platform-wide', 'account-specific')),
            is_live BOOLEAN NOT NULL DEFAULT 0,
            deployed_at TEXT,
            estimated_activation_duration_minutes INTEGER NOT NULL DEFAULT 60,
            FOREIGN KEY (signals_agent_segment_id) REFERENCES signal_segments (id),
            UNIQUE(signals_agent_segment_id, platform, account)
        )
    """)
    
    # Unified contexts table for all context types (A2A-ready)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contexts (
            context_id TEXT PRIMARY KEY,
            context_type TEXT NOT NULL CHECK (context_type IN ('discovery', 'activation', 'optimization', 'reporting')),
            parent_context_id TEXT,
            principal_id TEXT,
            metadata TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'completed' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'expired')),
            created_at TEXT NOT NULL,
            completed_at TEXT,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (parent_context_id) REFERENCES contexts (context_id)
        )
    """)
    
    # LiveRamp marketplace segments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS liveramp_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            segment_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            provider_name TEXT,
            segment_type TEXT,
            reach_count INTEGER,
            has_pricing BOOLEAN,
            cpm_price REAL,
            categories TEXT,
            raw_data TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create FTS5 virtual table for full-text search
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS liveramp_segments_fts 
        USING fts5(
            segment_id UNINDEXED,
            name,
            description,
            provider_name,
            categories,
            content=liveramp_segments,
            content_rowid=id
        ) 
    """)
    
    # Create trigger to keep FTS in sync
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS liveramp_segments_ai 
        AFTER INSERT ON liveramp_segments BEGIN
            INSERT INTO liveramp_segments_fts(
                rowid, segment_id, name, description, provider_name, categories
            ) VALUES (
                new.id, new.segment_id, new.name, new.description, 
                new.provider_name, new.categories
            );
        END;
    """)
    
    # LiveRamp sync status table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS liveramp_sync_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sync_started TIMESTAMP,
            sync_completed TIMESTAMP,
            total_segments INTEGER,
            status TEXT,
            error_message TEXT
        )
    """)
    
    # Create required indices for performance
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_contexts_type_principal ON contexts (context_type, principal_id)",
        "CREATE INDEX IF NOT EXISTS idx_contexts_parent ON contexts (parent_context_id)",
        "CREATE INDEX IF NOT EXISTS idx_signal_segments_provider ON signal_segments (data_provider)",
        "CREATE INDEX IF NOT EXISTS idx_signal_segments_type ON signal_segments (signal_type)",
        "CREATE INDEX IF NOT EXISTS idx_signal_segments_access ON signal_segments (catalog_access)",
        "CREATE INDEX IF NOT EXISTS idx_platform_deployments_platform ON platform_deployments (platform)",
        "CREATE INDEX IF NOT EXISTS idx_platform_deployments_live ON platform_deployments (is_live)",
        "CREATE INDEX IF NOT EXISTS idx_principal_access_principal ON principal_segment_access (principal_id)",
        "CREATE INDEX IF NOT EXISTS idx_liveramp_segments_provider ON liveramp_segments (provider_name)",
        "CREATE INDEX IF NOT EXISTS idx_liveramp_segments_type ON liveramp_segments (segment_type)"
    ]
    
    for index_sql in indices:
        cursor.execute(index_sql)


def insert_sample_data(cursor: sqlite3.Cursor):
    """Insert sample signal segments and platform deployments - idempotent."""
    
    now = datetime.now().isoformat()
    
    # Sample signal segments aligned with required platforms
    segments = [
        {
            'id': 'signal_001',
            'name': 'High-Value Shoppers',
            'description': 'Audience of high-value online shoppers',
            'data_provider': 'LiveRamp',
            'coverage_percentage': 15.2,
            'signal_type': 'audience',
            'catalog_access': 'public',
            'base_cpm': 2.50,
            'revenue_share_percentage': 15.0,
        },
        {
            'id': 'signal_002',
            'name': 'Tech Enthusiasts',
            'description': 'Technology enthusiasts and early adopters',
            'data_provider': 'Peer39',
            'coverage_percentage': 8.7,
            'signal_type': 'audience',
            'catalog_access': 'public',
            'base_cpm': 1.80,
            'revenue_share_percentage': 12.0,
        },
        {
            'id': 'signal_003',
            'name': 'Travel Planners',
            'description': 'Users actively planning travel',
            'data_provider': 'LiveRamp',
            'coverage_percentage': 12.1,
            'signal_type': 'audience',
            'catalog_access': 'public',
            'base_cpm': 2.20,
            'revenue_share_percentage': 15.0,
        },
        {
            'id': 'sports_enthusiasts_public',
            'name': 'Sports Enthusiasts - Public',
            'description': 'Broad sports audience available platform-wide',
            'data_provider': 'Polk',
            'coverage_percentage': 45.0,
            'signal_type': 'audience',
            'catalog_access': 'public',
            'base_cpm': 3.50,
            'revenue_share_percentage': 15.0,
        },
        {
            'id': 'luxury_auto_intenders',
            'name': 'Luxury Automotive Intenders',
            'description': 'High-income individuals showing luxury car purchase intent',
            'data_provider': 'Experian',
            'coverage_percentage': 12.5,
            'signal_type': 'audience',
            'catalog_access': 'personalized',
            'base_cpm': 8.75,
            'revenue_share_percentage': 20.0,
        },
        {
            'id': 'peer39_luxury_auto',
            'name': 'Luxury Automotive Context',
            'description': 'Pages with luxury automotive content and high viewability',
            'data_provider': 'Peer39',
            'coverage_percentage': 15.0,
            'signal_type': 'audience',
            'catalog_access': 'public',
            'base_cpm': 2.50,
            'revenue_share_percentage': 12.0,
        },
        {
            'id': 'urban_millennials',
            'name': 'Urban Millennials',
            'description': 'Millennials living in major urban markets with disposable income',
            'data_provider': 'LiveRamp',
            'coverage_percentage': 32.0,
            'signal_type': 'audience',
            'catalog_access': 'public',
            'base_cpm': 4.00,
            'revenue_share_percentage': 15.0,
        }
    ]
    
    # Check if data already exists to ensure idempotency
    cursor.execute("SELECT COUNT(*) FROM signal_segments")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        logger.info(f"Database already contains {existing_count} segments, skipping data insertion")
        return
    
    # Insert segments using INSERT OR REPLACE for idempotency
    for segment in segments:
        cursor.execute("""
            INSERT OR REPLACE INTO signal_segments 
            (id, name, description, data_provider, coverage_percentage, 
             signal_type, catalog_access, base_cpm, revenue_share_percentage, 
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            segment['id'], segment['name'], segment['description'], 
            segment['data_provider'], segment['coverage_percentage'],
            segment['signal_type'], segment['catalog_access'],
            segment['base_cpm'], segment['revenue_share_percentage'],
            now, now
        ))
    
    logger.info(f"Inserted {len(segments)} signal segments")
    
    # Sample platform deployments for required platforms
    deployments = [
        # High-Value Shoppers
        {
            'signals_agent_segment_id': 'signal_001',
            'platform': 'index-exchange',
            'account': None,
            'decisioning_platform_segment_id': 'ix_high_value_shoppers',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'signal_001',
            'platform': 'the-trade-desk',
            'account': None,
            'decisioning_platform_segment_id': 'ttd_high_value_shoppers',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'signal_001',
            'platform': 'openx',
            'account': None,
            'decisioning_platform_segment_id': 'ox_high_value_shoppers',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'signal_001',
            'platform': 'pubmatic',
            'account': None,
            'decisioning_platform_segment_id': 'pm_high_value_shoppers',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        
        # Tech Enthusiasts
        {
            'signals_agent_segment_id': 'signal_002',
            'platform': 'index-exchange',
            'account': None,
            'decisioning_platform_segment_id': 'ix_tech_enthusiasts',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'signal_002',
            'platform': 'the-trade-desk',
            'account': None,
            'decisioning_platform_segment_id': 'ttd_tech_enthusiasts',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        
        # Travel Planners
        {
            'signals_agent_segment_id': 'signal_003',
            'platform': 'index-exchange',
            'account': None,
            'decisioning_platform_segment_id': 'ix_travel_planners',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'signal_003',
            'platform': 'pubmatic',
            'account': None,
            'decisioning_platform_segment_id': 'pm_travel_planners',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        
        # Sports enthusiasts - already live on multiple platforms
        {
            'signals_agent_segment_id': 'sports_enthusiasts_public',
            'platform': 'the-trade-desk',
            'account': None,
            'decisioning_platform_segment_id': 'ttd_sports_general',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'sports_enthusiasts_public',
            'platform': 'index-exchange',
            'account': None,
            'decisioning_platform_segment_id': 'ix_sports_enthusiasts_public',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        
        # Luxury auto - mix of live and requiring activation
        {
            'signals_agent_segment_id': 'peer39_luxury_auto',
            'platform': 'index-exchange',
            'account': None,
            'decisioning_platform_segment_id': 'ix_peer39_luxury_auto_gen',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'peer39_luxury_auto',
            'platform': 'openx',
            'account': None,
            'decisioning_platform_segment_id': 'ox_peer39_lux_auto_456',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        },
        {
            'signals_agent_segment_id': 'peer39_luxury_auto',
            'platform': 'pubmatic',
            'account': 'brand-456-pm',
            'decisioning_platform_segment_id': None,
            'scope': 'account-specific',
            'is_live': False,
            'deployed_at': None,
            'estimated_activation_duration_minutes': 60
        },
        
        # Urban millennials - live on TTD
        {
            'signals_agent_segment_id': 'urban_millennials',
            'platform': 'the-trade-desk',
            'account': None,
            'decisioning_platform_segment_id': 'ttd_urban_millennials_gen',
            'scope': 'platform-wide',
            'is_live': True,
            'deployed_at': now,
            'estimated_activation_duration_minutes': 60
        }
    ]
    
    # Check if deployments already exist
    cursor.execute("SELECT COUNT(*) FROM platform_deployments")
    existing_deployments = cursor.fetchone()[0]
    
    if existing_deployments > 0:
        logger.info(f"Database already contains {existing_deployments} deployments, skipping deployment insertion")
        return
    
    for deployment in deployments:
        cursor.execute("""
            INSERT OR REPLACE INTO platform_deployments 
            (signals_agent_segment_id, platform, account, decisioning_platform_segment_id,
             scope, is_live, deployed_at, estimated_activation_duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deployment['signals_agent_segment_id'], deployment['platform'],
            deployment['account'], deployment['decisioning_platform_segment_id'],
            deployment['scope'], deployment['is_live'], deployment['deployed_at'],
            deployment['estimated_activation_duration_minutes']
        ))
    
    logger.info(f"Inserted {len(deployments)} platform deployments")
    
    # Insert sample principals
    principals = [
        {
            'principal_id': 'public',
            'name': 'Public Access',
            'access_level': 'public',
            'description': 'Default public access - sees only public catalog segments'
        },
        {
            'principal_id': 'acme_corp',
            'name': 'ACME Corporation',
            'access_level': 'personalized',
            'description': 'Large advertiser with personalized catalog access and custom pricing'
        },
        {
            'principal_id': 'luxury_brands_inc',
            'name': 'Luxury Brands Inc',
            'access_level': 'personalized', 
            'description': 'Premium luxury brand advertiser with specialized segments'
        },
        {
            'principal_id': 'startup_agency',
            'name': 'Startup Digital Agency',
            'access_level': 'public',
            'description': 'Small agency with public catalog access only'
        },
        {
            'principal_id': 'auto_manufacturer',
            'name': 'Global Auto Manufacturer',
            'access_level': 'private',
            'description': 'Private client with exclusive custom segments'
        }
    ]
    
    # Check if principals already exist
    cursor.execute("SELECT COUNT(*) FROM principals")
    existing_principals = cursor.fetchone()[0]
    
    if existing_principals > 0:
        logger.info(f"Database already contains {existing_principals} principals, skipping principal insertion")
        return
    
    for principal in principals:
        cursor.execute("""
            INSERT OR REPLACE INTO principals 
            (principal_id, name, access_level, description, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            principal['principal_id'], principal['name'], principal['access_level'],
            principal['description'], now
        ))
    
    logger.info(f"Inserted {len(principals)} principals")
    
    # Insert principal-specific segment access
    principal_access = [
        # ACME Corp gets custom pricing on some segments
        {
            'principal_id': 'acme_corp',
            'signals_agent_segment_id': 'luxury_auto_intenders',
            'access_type': 'custom_pricing',
            'custom_cpm': 6.50,  # Discounted from 8.75
            'notes': 'Volume discount for large advertiser'
        },
        {
            'principal_id': 'acme_corp', 
            'signals_agent_segment_id': 'sports_enthusiasts_public',
            'access_type': 'custom_pricing',
            'custom_cpm': 2.75,  # Discounted from 3.50
            'notes': 'Preferred customer pricing'
        },
        
        # Luxury Brands Inc gets exclusive access to luxury segments
        {
            'principal_id': 'luxury_brands_inc',
            'signals_agent_segment_id': 'luxury_auto_intenders', 
            'access_type': 'granted',
            'custom_cpm': None,
            'notes': 'Exclusive access to luxury audience'
        }
    ]
    
    # Check if principal access already exists
    cursor.execute("SELECT COUNT(*) FROM principal_segment_access")
    existing_access = cursor.fetchone()[0]
    
    if existing_access > 0:
        logger.info(f"Database already contains {existing_access} principal access records, skipping access insertion")
        return
    
    for access in principal_access:
        cursor.execute("""
            INSERT OR REPLACE INTO principal_segment_access
            (principal_id, signals_agent_segment_id, access_type, custom_cpm, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            access['principal_id'], access['signals_agent_segment_id'], 
            access['access_type'], access['custom_cpm'], access['notes'], now
        ))
    
    logger.info(f"Inserted {len(principal_access)} principal access records")


def get_db_connection():
    """Get a database connection."""
    db_path = os.environ.get('DATABASE_PATH', 'signals_agent.db')
    return sqlite3.connect(db_path, timeout=30.0)


if __name__ == "__main__":
    init_db()