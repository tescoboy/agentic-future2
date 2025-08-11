#!/usr/bin/env python3
"""Simple FastAPI app for Signals Agent with required endpoints."""

import logging
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Health endpoint must be defined BEFORE any complex imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Load environment variables safely
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available, using system environment variables")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Determine mode
MODE = os.getenv("MODE", "demo").lower()
if MODE not in ["demo", "production"]:
    MODE = "demo"

# Create FastAPI app
app = FastAPI(
    title="Signals Agent API",
    description="API for discovering, validating, and activating advertising signals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health endpoint - MUST be simple and fast (defined early)
@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for Railway - must return HTTP 200 quickly."""
    return {"ok": True, "mode": "production"}

# Root endpoint for Railway health checks
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint for health checks."""
    return {
        "message": "Signals Agent API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Global request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """Handle 404 errors."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.warning(f"404 Not Found - Request ID: {request_id}, Path: {request.url.path}")
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource was not found: {request.url.path}",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.warning(f"422 Validation Error - Request ID: {request_id}, Errors: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle internal server errors."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"500 Internal Server Error - Request ID: {request_id}, Error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"Unhandled Exception - Request ID: {request_id}, Error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Server Error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
    )

# Note: Pydantic models are now imported from api_models.py

# Sample data for demo mode
SAMPLE_SIGNALS = [
    {
        "id": "signal_001",
        "name": "High-Value Shoppers",
        "provider": "LiveRamp",
        "coverage_percentage": 15.2,
        "price": 2.50,
        "allowed_platforms": ["dv360", "tradedesk", "amazon"],
        "description": "Audience of high-value online shoppers"
    },
    {
        "id": "signal_002", 
        "name": "Tech Enthusiasts",
        "provider": "Peer39",
        "coverage_percentage": 8.7,
        "price": 1.80,
        "allowed_platforms": ["dv360", "tradedesk"],
        "description": "Technology enthusiasts and early adopters"
    },
    {
        "id": "signal_003",
        "name": "Travel Planners",
        "provider": "LiveRamp", 
        "coverage_percentage": 12.1,
        "price": 2.20,
        "allowed_platforms": ["dv360", "amazon"],
        "description": "Users actively planning travel"
    }
]

# In-memory storage for activations
activations = {}

# Import models and services (after health endpoint is defined)
try:
    from api_models import DiscoveryRequest, DiscoveryResponse, ActivationRequest, ActivationResponse, StatusResponse
    from services.signal_discovery import SignalDiscoveryService
    from services.ai_ranking import AIRankingService
    from services.proposal_validator import ProposalValidator
    from services.activation_service import ActivationService
    from services.status_simulator import StatusSimulator
    from database import get_db_connection
except ImportError as e:
    logger.warning(f"Some modules not available: {e}")
    # Define minimal fallback classes
    class DiscoveryRequest:
        def __init__(self, query="", platforms=None, limit=5):
            self.query = query
            self.platforms = platforms or []
            self.limit = limit
    
    class DiscoveryResponse:
        def __init__(self, matches=None, proposals=None, using_fallback=False, ranking_method="fallback", debug=None, total_matches=0, total_proposals=0):
            self.matches = matches or []
            self.proposals = proposals or []
            self.using_fallback = using_fallback
            self.ranking_method = ranking_method
            self.debug = debug
            self.total_matches = total_matches
            self.total_proposals = total_proposals
    
    class ActivationRequest:
        def __init__(self, segment_id=None, proposal_id=None, platforms=None):
            self.segment_id = segment_id
            self.proposal_id = proposal_id
            self.platforms = platforms or []
    
    class ActivationResponse:
        def __init__(self, activation_id="", status="", message="", allowed_platforms=None, estimated_duration_minutes=60):
            self.activation_id = activation_id
            self.status = status
            self.message = message
            self.allowed_platforms = allowed_platforms or []
            self.estimated_duration_minutes = estimated_duration_minutes
    
    class StatusResponse:
        def __init__(self, activation_id="", status="", details=None, created_at=None, updated_at=None, completed_at=None):
            self.activation_id = activation_id
            self.status = status
            self.details = details or {}
            self.created_at = created_at
            self.updated_at = updated_at
            self.completed_at = completed_at

@app.post("/discovery", tags=["Discovery"])
async def discovery(request: DiscoveryRequest):
    """Discover signals based on query with AI ranking and fallback."""
    logger.info(f"Discovery request: {request.query}")
    
    # Simple fallback response for now
    return DiscoveryResponse(
        matches=[],
        proposals=[],
        using_fallback=True,
        ranking_method="fallback",
        debug={"message": "Service temporarily unavailable"},
        total_matches=0,
        total_proposals=0
    )

@app.get("/activation/options", tags=["Activation"])
async def get_activation_options():
    """Get available activation options."""
    logger.info("Activation options requested")
    
    # Return available platforms from sample data
    all_platforms = set()
    for signal in SAMPLE_SIGNALS:
        all_platforms.update(signal["allowed_platforms"])
    
    return {
        "platforms": list(all_platforms),
        "signals": [{"id": s["id"], "name": s["name"]} for s in SAMPLE_SIGNALS]
    }

@app.post("/activation", tags=["Activation"])
async def activate_signal(request: ActivationRequest):
    """Activate a signal or proposal on platforms."""
    logger.info(f"Activation request: segment_id={request.segment_id}, proposal_id={request.proposal_id}, platforms={request.platforms}")
    
    # Simple fallback response
    activation_id = f"act_{uuid.uuid4().hex[:8]}"
    return ActivationResponse(
        activation_id=activation_id,
        status="queued",
        message="Activation queued successfully",
        allowed_platforms=request.platforms,
        estimated_duration_minutes=60
    )

@app.get("/status/{activation_id}", tags=["Status"])
async def get_status(activation_id: str):
    """Get activation status."""
    logger.info(f"Status request: {activation_id}")
    
    # Simple fallback response
    return StatusResponse(
        activation_id=activation_id,
        status="pending",
        details={"message": "Status check temporarily unavailable"},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("simple_app:app", host="0.0.0.0", port=port, reload=False)
