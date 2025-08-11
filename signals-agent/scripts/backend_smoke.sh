#!/bin/bash

# Signals Agent Backend Smoke Test
# Tests all major endpoints and provides pass/fail summary

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://127.0.0.1:8000"
TIMEOUT=10
MAX_RETRIES=3

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
    ((TOTAL_TESTS++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
    ((TOTAL_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if server is running
check_server_running() {
    log_info "Checking if server is running on $BASE_URL..."
    
    if curl -s --max-time $TIMEOUT "$BASE_URL/health" > /dev/null 2>&1; then
        log_success "Server is running"
        return 0
    else
        log_warning "Server not running, attempting to start..."
        return 1
    fi
}

# Start server if not running
start_server() {
    log_info "Starting server..."
    
    # Check if we're in the right directory
    if [ ! -f "simple_app.py" ]; then
        log_error "simple_app.py not found. Please run from signals-agent directory."
        exit 1
    fi
    
    # Check if virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "Virtual environment not detected. Please activate it first."
        log_info "Run: source .venv/bin/activate"
    fi
    
    # Start server in background
    nohup uvicorn simple_app:app --host 127.0.0.1 --port 8000 --reload > backend.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    log_info "Waiting for server to start..."
    for i in {1..30}; do
        if curl -s --max-time $TIMEOUT "$BASE_URL/health" > /dev/null 2>&1; then
            log_success "Server started successfully (PID: $SERVER_PID)"
            return 0
        fi
        sleep 1
    done
    
    log_error "Server failed to start within 30 seconds"
    return 1
}

# Test health endpoint
test_health() {
    log_info "Testing /health endpoint..."
    
    local response
    response=$(curl -s --max-time $TIMEOUT "$BASE_URL/health")
    
    if echo "$response" | grep -q '"ok":true'; then
        log_success "Health endpoint working"
        echo "Response: $response"
    else
        log_error "Health endpoint failed"
        echo "Response: $response"
        return 1
    fi
}

# Test discovery endpoint
test_discovery() {
    log_info "Testing /discovery endpoint..."
    
    local payload='{
        "query": "high value shoppers",
        "principal_id": "principal_001",
        "limit": 5,
        "platforms": ["index-exchange", "the-trade-desk"]
    }'
    
    local response
    response=$(curl -s --max-time $TIMEOUT \
        -X POST "$BASE_URL/discovery" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if echo "$response" | grep -q '"proposals"'; then
        log_success "Discovery endpoint working"
        echo "Found $(echo "$response" | grep -o '"total_proposals":[0-9]*' | cut -d: -f2) proposals"
    else
        log_error "Discovery endpoint failed"
        echo "Response: $response"
        return 1
    fi
}

# Test activation endpoint
test_activation() {
    log_info "Testing /activation endpoint..."
    
    local payload='{
        "segment_id": "signal_001",
        "principal_id": "principal_001",
        "platforms": ["index-exchange"]
    }'
    
    local response
    response=$(curl -s --max-time $TIMEOUT \
        -X POST "$BASE_URL/activation" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if echo "$response" | grep -q '"activation_id"'; then
        log_success "Activation endpoint working"
        local activation_id=$(echo "$response" | grep -o '"activation_id":"[^"]*"' | cut -d'"' -f4)
        echo "Activation ID: $activation_id"
        
        # Store activation ID for status test
        echo "$activation_id" > /tmp/smoke_test_activation_id
    else
        log_error "Activation endpoint failed"
        echo "Response: $response"
        return 1
    fi
}

# Test status endpoint
test_status() {
    log_info "Testing /status endpoint..."
    
    if [ ! -f /tmp/smoke_test_activation_id ]; then
        log_warning "No activation ID found, skipping status test"
        return 0
    fi
    
    local activation_id=$(cat /tmp/smoke_test_activation_id)
    local response
    response=$(curl -s --max-time $TIMEOUT "$BASE_URL/status/$activation_id")
    
    if echo "$response" | grep -q '"status"'; then
        log_success "Status endpoint working"
        local status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        echo "Activation status: $status"
    else
        log_error "Status endpoint failed"
        echo "Response: $response"
        return 1
    fi
}

# Test status simulation
test_status_simulation() {
    log_info "Testing status simulation..."
    
    if [ ! -f /tmp/smoke_test_activation_id ]; then
        log_warning "No activation ID found, skipping simulation test"
        return 0
    fi
    
    local activation_id=$(cat /tmp/smoke_test_activation_id)
    local response
    response=$(curl -s --max-time $TIMEOUT \
        -X POST "$BASE_URL/status/$activation_id/simulate")
    
    if echo "$response" | grep -q '"status"'; then
        log_success "Status simulation working"
        local status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        echo "New status: $status"
    else
        log_error "Status simulation failed"
        echo "Response: $response"
        return 1
    fi
}

# Test pending activations
test_pending_activations() {
    log_info "Testing pending activations endpoint..."
    
    local response
    response=$(curl -s --max-time $TIMEOUT "$BASE_URL/status/list/pending")
    
    if echo "$response" | grep -q '"pending_activations"'; then
        log_success "Pending activations endpoint working"
        local count=$(echo "$response" | grep -o '"count":[0-9]*' | cut -d: -f2)
        echo "Pending activations: $count"
    else
        log_error "Pending activations endpoint failed"
        echo "Response: $response"
        return 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    rm -f /tmp/smoke_test_activation_id
}

# Main test execution
main() {
    echo "=========================================="
    echo "Signals Agent Backend Smoke Test"
    echo "=========================================="
    echo ""
    
    # Set up cleanup on exit
    trap cleanup EXIT
    
    # Check and start server if needed
    if ! check_server_running; then
        if ! start_server; then
            log_error "Failed to start server"
            exit 1
        fi
    fi
    
    echo ""
    log_info "Running smoke tests..."
    echo ""
    
    # Run tests
    test_health
    test_discovery
    test_activation
    test_status
    test_status_simulation
    test_pending_activations
    
    echo ""
    echo "=========================================="
    echo "Smoke Test Summary"
    echo "=========================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
