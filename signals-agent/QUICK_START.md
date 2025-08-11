# Quick Start Reference

## Essential Commands

### Setup (One-time)
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

### Daily Development
```bash
# Start backend server
./manage_servers.sh start

# Run smoke tests
./scripts/backend_smoke.sh

# Stop servers
./manage_servers.sh stop

# Check server status
./manage_servers.sh status
```

### Manual Testing
```bash
# Health check
curl http://127.0.0.1:8000/health

# API documentation
open http://127.0.0.1:8000/docs

# Discovery test
curl -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "high value shoppers", "limit": 5}'
```

## Port Configuration
- **Backend**: 8000
- **Frontend**: 3000 (with auto-fallback)

## Directory Discipline
- **Backend code**: `signals-agent/`
- **Frontend code**: `frontend/` (separate directory)
- **Logs**: `logs/` and `backend.log`
- **Database**: `signals_agent.db`

## Troubleshooting
```bash
# Port conflicts
lsof -i :8000
pkill -f uvicorn

# Permission issues
chmod +x scripts/backend_smoke.sh
chmod +x manage_servers.sh

# Database reset
python init_db.py
```
