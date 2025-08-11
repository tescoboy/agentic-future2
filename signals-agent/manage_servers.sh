#!/bin/bash

# Server management script for Signals Agent
# Usage: ./manage_servers.sh [start|stop|status]

set -e

BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_PID_FILE="backend.pid"
FRONTEND_PID_FILE="frontend.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

find_free_port() {
    local start_port=$1
    local port=$start_port
    while check_port $port; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 100)) ]; then
            error "Could not find free port starting from $start_port"
            exit 1
        fi
    done
    echo $port
}

start_backend() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            warn "Backend already running with PID $pid"
            return
        else
            rm -f "$BACKEND_PID_FILE"
        fi
    fi

    if check_port $BACKEND_PORT; then
        error "Port $BACKEND_PORT is already in use"
        exit 1
    fi

    log "Starting backend server on port $BACKEND_PORT..."
    
    # Activate virtual environment and start backend
    source .venv/bin/activate
    nohup python -m uvicorn simple_app:app --host 127.0.0.1 --port $BACKEND_PORT > backend.log 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    
    # Wait a moment for server to start
    sleep 2
    
    if check_port $BACKEND_PORT; then
        log "Backend server started successfully (PID: $(cat $BACKEND_PID_FILE))"
    else
        error "Failed to start backend server"
        exit 1
    fi
}

start_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            warn "Frontend already running with PID $pid"
            return
        else
            rm -f "$FRONTEND_PID_FILE"
        fi
    fi

    # Check if frontend directory exists
    if [ ! -d "../frontend" ]; then
        warn "Frontend directory not found, skipping frontend start"
        return
    fi

    local actual_port=$FRONTEND_PORT
    if check_port $FRONTEND_PORT; then
        actual_port=$(find_free_port $FRONTEND_PORT)
        warn "Port $FRONTEND_PORT is busy, using port $actual_port instead"
    fi

    log "Starting frontend server on port $actual_port..."
    
    # Start frontend (assuming it's a React/Vite app)
    cd ../frontend
    nohup npm run dev -- --port $actual_port > ../signals-agent/frontend.log 2>&1 &
    echo $! > "../signals-agent/$FRONTEND_PID_FILE"
    cd ../signals-agent
    
    # Wait a moment for server to start
    sleep 3
    
    if check_port $actual_port; then
        log "Frontend server started successfully on port $actual_port (PID: $(cat $FRONTEND_PID_FILE))"
    else
        warn "Frontend server may not have started properly"
    fi
}

stop_server() {
    local pid_file=$1
    local server_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            log "Stopping $server_name (PID: $pid)..."
            kill $pid
            rm -f "$pid_file"
            log "$server_name stopped"
        else
            warn "$server_name not running (stale PID file)"
            rm -f "$pid_file"
        fi
    else
        warn "$server_name not running (no PID file)"
    fi
}

show_status() {
    echo "=== Server Status ==="
    
    # Backend status
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "Backend: ${GREEN}Running${NC} (PID: $pid, Port: $BACKEND_PORT)"
        else
            echo -e "Backend: ${RED}Not running${NC} (stale PID file)"
        fi
    else
        echo -e "Backend: ${RED}Not running${NC}"
    fi
    
    # Frontend status
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "Frontend: ${GREEN}Running${NC} (PID: $pid)"
        else
            echo -e "Frontend: ${RED}Not running${NC} (stale PID file)"
        fi
    else
        echo -e "Frontend: ${RED}Not running${NC}"
    fi
    
    echo ""
    echo "=== Port Status ==="
    if check_port $BACKEND_PORT; then
        echo -e "Port $BACKEND_PORT: ${GREEN}In use${NC}"
    else
        echo -e "Port $BACKEND_PORT: ${RED}Free${NC}"
    fi
    
    if check_port $FRONTEND_PORT; then
        echo -e "Port $FRONTEND_PORT: ${GREEN}In use${NC}"
    else
        echo -e "Port $FRONTEND_PORT: ${RED}Free${NC}"
    fi
}

case "${1:-start}" in
    start)
        start_backend
        start_frontend
        log "All servers started"
        show_status
        ;;
    stop)
        stop_server "$BACKEND_PID_FILE" "Backend"
        stop_server "$FRONTEND_PID_FILE" "Frontend"
        log "All servers stopped"
        ;;
    status)
        show_status
        ;;
    restart)
        stop_server "$BACKEND_PID_FILE" "Backend"
        stop_server "$FRONTEND_PID_FILE" "Frontend"
        sleep 2
        start_backend
        start_frontend
        log "All servers restarted"
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo "  start   - Start all servers"
        echo "  stop    - Stop all servers"
        echo "  status  - Show server status"
        echo "  restart - Restart all servers"
        exit 1
        ;;
esac
