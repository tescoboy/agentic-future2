# Signals Agent Backend

A FastAPI-based backend for discovering, validating, and activating advertising signals following the Ad Context Protocol.

## Quick Start

### Prerequisites

- Python 3.8+
- `uv` package manager (recommended) or `pip`
- Git

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd signals-agent
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv pip install -r requirements.txt
   
   # Or using pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy and edit .env file
   cp .env.example .env
   # Edit .env with your GEMINI_API_KEY and other settings
   ```

## Backend Commands

### Initialize Database

Initialize the database with sample data:

```bash
# From signals-agent directory
python init_db.py
```

This creates:
- SQLite database (`signals_agent.db`)
- Sample signal segments
- Platform deployments
- Principal access controls

### Start Server

**Option 1: Using manage_servers.sh (recommended)**
```bash
# Start backend only
./manage_servers.sh start

# Start both backend and frontend
./manage_servers.sh start

# Stop servers
./manage_servers.sh stop

# Check status
./manage_servers.sh status
```

**Option 2: Direct uvicorn**
```bash
# Development mode with auto-reload
uvicorn simple_app:app --host 127.0.0.1 --port 8000 --reload

# Production mode
uvicorn simple_app:app --host 0.0.0.0 --port 8000
```

### Run Smoke Tests

Test all major endpoints:

```bash
# From signals-agent directory
./scripts/backend_smoke.sh
```

The smoke test will:
- Check if server is running (start if needed)
- Test `/health` endpoint
- Test `/discovery` with sample query
- Test `/activation` with known segment
- Test `/status` endpoints
- Provide pass/fail summary

## API Endpoints

### Health & Status
- `GET /health` - Health check with mode info
- `GET /docs` - Interactive API documentation

### Discovery
- `POST /discovery` - Discover signals with AI ranking
- `GET /activation/options` - Get available activation options

### Activation
- `POST /activation` - Activate signals or proposals

### Status Management
- `GET /status/{activation_id}` - Get activation status
- `POST /status/{activation_id}/simulate` - Simulate status transition
- `POST /status/simulate/bulk` - Bulk status simulation
- `GET /status/list/pending` - List pending activations
- `POST /status/{activation_id}/force` - Force specific status

## Configuration

### Environment Variables (.env)

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
DEBUG_MODE=true                    # Enable debug mode
DATABASE_PATH=signals_agent.db     # Database file path
PORT=8000                         # Server port
MODE=demo                         # demo or production
```

### Port Configuration

- **Backend**: 8000 (default)
- **Frontend**: 3000 (with auto-fallback to 3001, 3002, etc.)

## Directory Structure

```
signals-agent/
├── simple_app.py              # Main FastAPI application
├── api_models.py              # Pydantic models
├── database.py                # Database initialization
├── init_db.py                 # Database setup script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── manage_servers.sh          # Server management script
├── scripts/
│   └── backend_smoke.sh       # Smoke test script
├── services/                  # Business logic services
│   ├── activation_service.py
│   ├── ai_ranking.py
│   ├── proposal_validator.py
│   ├── signal_discovery.py
│   └── status_simulator.py
└── logs/                      # Application logs
    └── proposal_validation.log
```

## Development Workflow

1. **Start development:**
   ```bash
   source .venv/bin/activate
   ./manage_servers.sh start
   ```

2. **Run tests:**
   ```bash
   ./scripts/backend_smoke.sh
   ```

3. **View logs:**
   ```bash
   tail -f backend.log
   tail -f logs/proposal_validation.log
   ```

4. **Access API docs:**
   - Open http://127.0.0.1:8000/docs
   - Interactive Swagger UI with all endpoints

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8000

# Kill process if needed
pkill -f uvicorn
```

**Database errors:**
```bash
# Reinitialize database
python init_db.py
```

**Virtual environment issues:**
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Permission denied on scripts:**
```bash
chmod +x scripts/backend_smoke.sh
chmod +x manage_servers.sh
```

### Logs

- **Application logs**: `backend.log`
- **Validation logs**: `logs/proposal_validation.log`
- **Server logs**: Check `manage_servers.sh` output

## API Documentation

- **Interactive docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI spec**: http://127.0.0.1:8000/openapi.json

## Testing

### Manual Testing

```bash
# Health check
curl http://127.0.0.1:8000/health

# Discovery
curl -X POST http://127.0.0.1:8000/discovery \
  -H "Content-Type: application/json" \
  -d '{"query": "high value shoppers", "limit": 5}'

# Activation
curl -X POST http://127.0.0.1:8000/activation \
  -H "Content-Type: application/json" \
  -d '{"segment_id": "signal_001", "principal_id": "principal_001", "platforms": ["index-exchange"]}'
```

### Automated Testing

```bash
# Run full smoke test
./scripts/backend_smoke.sh

# Run specific tests
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/status/list/pending
```

## Production Deployment

For production deployment:

1. Set `MODE=production` in `.env`
2. Use production uvicorn settings
3. Set up proper logging
4. Configure reverse proxy (nginx)
5. Set up monitoring and health checks

```bash
# Production start
uvicorn simple_app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Support

For issues and questions:
1. Check the logs in `backend.log`
2. Run smoke tests: `./scripts/backend_smoke.sh`
3. Verify environment setup
4. Check API documentation at `/docs`