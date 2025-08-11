# Database Setup and Management

## Overview

The Signals Agent uses SQLite with WAL (Write-Ahead Logging) mode for better concurrent access and performance.

## Database Schema

The database includes the following tables:

### Core Tables
- **signal_segments** - Main signal/audience segments
- **principals** - Access control for different users/organizations
- **principal_segment_access** - Personalized access and pricing
- **platform_deployments** - Signal deployments across platforms
- **contexts** - A2A protocol contexts for discovery/activation

### LiveRamp Integration
- **liveramp_segments** - LiveRamp marketplace segments
- **liveramp_segments_fts** - Full-text search index (FTS5)
- **liveramp_sync_status** - Sync status tracking

## Supported Platforms

The sample data includes deployments for:
- Index Exchange
- The Trade Desk
- OpenX
- PubMatic

## Initialization

### First Time Setup

1. **Environment Setup**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   
   # Verify .env file exists with required variables
   cat .env
   ```

2. **Database Initialization**
   ```bash
   # Initialize database with tables and sample data
   python init_db.py
   ```

### Idempotent Operation

The initialization is **idempotent** - you can run it multiple times safely:
- Tables are created with `CREATE TABLE IF NOT EXISTS`
- Sample data is only inserted if tables are empty
- No duplicate data is created

## Sample Data

The database is seeded with:

- **7 signal segments** including:
  - High-Value Shoppers (signal_001)
  - Tech Enthusiasts (signal_002)
  - Travel Planners (signal_003)
  - Sports Enthusiasts
  - Luxury Automotive segments

- **14 platform deployments** across all supported platforms

- **5 principals** with different access levels:
  - Public access
  - Personalized access (ACME Corp, Luxury Brands)
  - Private access (Auto Manufacturer)

## Database Location

- **Default**: `signals_agent.db` (in project root)
- **Configurable**: Set `DATABASE_PATH` in `.env` file

## WAL Mode

The database uses WAL mode for:
- Better concurrent read/write performance
- Improved reliability
- Non-blocking reads during writes

Files created:
- `signals_agent.db` - Main database file
- `signals_agent.db-shm` - Shared memory file
- `signals_agent.db-wal` - Write-ahead log file

## Indices

Performance indices are automatically created for:
- Context lookups (type, principal, parent)
- Signal segments (provider, type, access)
- Platform deployments (platform, live status)
- Principal access (principal ID)
- LiveRamp segments (provider, type)

## Verification

### Check Database Status
```bash
# Verify tables exist
sqlite3 signals_agent.db ".tables"

# Check data counts
sqlite3 signals_agent.db "SELECT COUNT(*) FROM signal_segments;"
sqlite3 signals_agent.db "SELECT COUNT(*) FROM platform_deployments;"

# Verify platforms
sqlite3 signals_agent.db "SELECT DISTINCT platform FROM platform_deployments;"
```

### Check Indices
```bash
sqlite3 signals_agent.db ".indexes"
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   # Ensure write permissions
   chmod 644 signals_agent.db*
   ```

2. **Locked Database**
   ```bash
   # Check for active connections
   lsof signals_agent.db
   
   # Restart if needed
   ./manage_servers.sh restart
   ```

3. **Corrupted Database**
   ```bash
   # Remove and reinitialize
   rm signals_agent.db*
   python init_db.py
   ```

### Logs

Database operations are logged with timestamps:
- Initialization progress
- Data insertion counts
- Error messages with context

## Development

### Adding New Segments

1. Add to `segments` list in `database.py`
2. Include required fields (id, name, description, etc.)
3. Run `python init_db.py` to update

### Adding New Platforms

1. Add platform deployments to `deployments` list
2. Use consistent platform names (lowercase with hyphens)
3. Set appropriate scope and live status

### Schema Changes

1. Modify `create_tables()` function
2. Add migration logic if needed
3. Test with `python init_db.py`
4. Update this documentation
