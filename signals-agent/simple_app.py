#!/usr/bin/env python3
"""Simple FastAPI app for Signals Agent with required endpoints."""

import logging
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

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

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        logger.info("Health check requested")
        return {
            "status": "healthy",
            "ok": True,
            "mode": MODE,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "ok": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }



@app.post("/discovery", tags=["Discovery"])
async def discovery(request: DiscoveryRequest):
    """Discover signals based on query with AI ranking and fallback."""
    logger.info(f"Discovery request: {request.query}")
    
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    db_connection = get_db_connection()
    
    try:
        # Initialize services
        discovery_service = SignalDiscoveryService(db_connection)
        ai_service = AIRankingService()
        validator = ProposalValidator(db_connection, debug_mode=debug_mode)
        
        # Step 1: Get candidate signals from database
        logger.info("Step 1: Getting candidate signals from database")
        candidate_signals = discovery_service.get_candidate_signals(
            query=request.query,
            platforms=request.platforms,
            limit=200  # Get more candidates for AI to choose from
        )
        
        # If no signals found, get all signals as fallback
        if not candidate_signals:
            logger.warning("No signals found for query, using all signals as fallback")
            candidate_signals = discovery_service.get_all_signals(limit=20)
        
        if not candidate_signals:
            logger.error("No signals available in database")
            return DiscoveryResponse(
                matches=[],
                proposals=[],
                using_fallback=True,
                ranking_method="fallback",
                debug={"error": "No signals available"} if debug_mode else None,
                total_matches=0,
                total_proposals=0
            )
        
        # Step 2: Rank signals using AI or fallback
        logger.info("Step 2: Ranking signals")
        ranked_signals, ranking_method = ai_service.rank_signals(
            query=request.query,
            candidate_signals=candidate_signals,
            max_results=request.limit or 5
        )
        
        # Step 3: Generate proposals using AI or fallback
        logger.info("Step 3: Generating proposals")
        # Calculate proposal count: use request limit, but cap at 10 for performance
        proposal_count = min(request.limit or 5, 10)
        proposals, generation_method = ai_service.generate_proposals(
            query=request.query,
            ranked_signals=ranked_signals,
            max_proposals=proposal_count
        )
        
        # Step 4: Validate proposals
        logger.info("Step 4: Validating proposals")
        valid_proposals, invalid_proposals, validation_report = validator.validate(proposals)
        
        # Step 5: Determine if using fallback
        using_fallback = (
            ranking_method == "fallback" or 
            generation_method == "fallback" or 
            len(valid_proposals) == 0
        )
        
        # If all proposals are invalid, create fallback proposals
        if len(valid_proposals) == 0 and len(invalid_proposals) > 0:
            logger.warning("All AI-generated proposals are invalid, creating fallback proposals")
            fallback_proposals = ai_service._fallback_proposals(ranked_signals[:3], proposal_count)
            valid_proposals, _, _ = validator.validate(fallback_proposals)
            using_fallback = True
        
        # Step 6: Prepare response
        final_ranking_method = f"{ranking_method}_{generation_method}"
        if using_fallback:
            final_ranking_method = "fallback"
        
        # Add debug info if DEBUG_MODE is enabled
        debug_info = None
        if debug_mode:
            debug_info = {
                "query_processed": request.query,
                "limit_requested": request.limit,
                "platforms_filter": request.platforms,
                "candidate_signals_count": len(candidate_signals),
                "ranked_signals_count": len(ranked_signals),
                "proposals_generated": len(proposals),
                "valid_proposals": len(valid_proposals),
                "invalid_proposals": len(invalid_proposals),
                "ranking_method": ranking_method,
                "generation_method": generation_method,
                "using_fallback": using_fallback,
                "validation_report": {
                    "request_id": validation_report.request_id,
                    "validation_errors": validation_report.validation_errors,
                    "debug_info": validation_report.debug_info
                }
            }
        
        response = DiscoveryResponse(
            matches=ranked_signals,
            proposals=valid_proposals,
            using_fallback=using_fallback,
            ranking_method=final_ranking_method,
            debug=debug_info,
            total_matches=len(ranked_signals),
            total_proposals=len(valid_proposals)
        )
        
        logger.info(
            f"Discovery response: {len(valid_proposals)} valid proposals, "
            f"{len(ranked_signals)} matches, using_fallback={using_fallback}"
        )
        return response
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        # Complete fallback response
        return DiscoveryResponse(
            matches=[],
            proposals=[],
            using_fallback=True,
            ranking_method="fallback",
            debug={"error": str(e)} if debug_mode else None,
            total_matches=0,
            total_proposals=0
        )
    
    finally:
        db_connection.close()

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
    
    db_connection = get_db_connection()
    
    try:
        # Initialize activation service
        activation_service = ActivationService(db_connection)
        
        # Process activation
        activation_id, allowed_platforms, activation_details = activation_service.process_activation(request)
        
        # Store activation in memory for backward compatibility
        activations[activation_id] = activation_details
        
        response = ActivationResponse(
            activation_id=activation_id,
            status="queued",
            message=f"{activation_details['target_type'].capitalize()} activation queued successfully",
            allowed_platforms=allowed_platforms,
            estimated_duration_minutes=activation_details.get("estimated_duration_minutes", 60)
        )
        
        logger.info(f"Activation queued: {activation_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Activation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Activation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")
    finally:
        db_connection.close()

@app.get("/status/{activation_id}", tags=["Status"])
async def get_status(activation_id: str):
    """Get activation status."""
    logger.info(f"Status request: {activation_id}")
    
    db_connection = get_db_connection()
    
    try:
        # Initialize status simulator (which handles database retrieval)
        status_simulator = StatusSimulator(db_connection)
        
        # Get status from database
        activation_status = status_simulator.get_activation_status(activation_id)
        
        if not activation_status:
            # Fallback to in-memory storage
            if activation_id not in activations:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Activation not found: {activation_id}. Please check the activation ID and try again."
                )
            
            activation = activations[activation_id]
            response = StatusResponse(
                activation_id=activation_id,
                status=activation["status"],
                details=activation,
                created_at=datetime.fromisoformat(activation["created_at"]),
                updated_at=datetime.fromisoformat(activation["updated_at"])
            )
        else:
            # Use database status
            response = StatusResponse(
                activation_id=activation_status["activation_id"],
                status=activation_status["status"],
                details=activation_status,
                created_at=datetime.fromisoformat(activation_status["created_at"]),
                updated_at=datetime.fromisoformat(activation_status["updated_at"]),
                completed_at=datetime.fromisoformat(activation_status["completed_at"]) if activation_status["completed_at"] else None
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status request failed: {str(e)}")
    finally:
        db_connection.close()


@app.post("/status/{activation_id}/simulate", tags=["Status"])
async def simulate_status_transition(activation_id: str):
    """Simulate the next status transition for an activation (demo purposes)."""
    logger.info(f"Status simulation request: {activation_id}")
    
    db_connection = get_db_connection()
    
    try:
        status_simulator = StatusSimulator(db_connection)
        
        # Simulate status transition
        updated_status = status_simulator.simulate_status_transition(activation_id)
        
        if not updated_status:
            raise HTTPException(
                status_code=404, 
                detail=f"Activation not found or cannot be transitioned: {activation_id}"
            )
        
        response = StatusResponse(
            activation_id=updated_status["activation_id"],
            status=updated_status["status"],
            details=updated_status,
            created_at=datetime.fromisoformat(updated_status["created_at"]),
            updated_at=datetime.fromisoformat(updated_status["updated_at"]),
            completed_at=datetime.fromisoformat(updated_status["completed_at"]) if updated_status["completed_at"] else None
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status simulation failed: {str(e)}")
    finally:
        db_connection.close()


@app.post("/status/simulate/bulk", tags=["Status"])
async def simulate_bulk_transitions(max_transitions: int = 10):
    """Simulate status transitions for multiple pending activations (demo purposes)."""
    logger.info(f"Bulk status simulation request: max_transitions={max_transitions}")
    
    db_connection = get_db_connection()
    
    try:
        status_simulator = StatusSimulator(db_connection)
        
        # Simulate bulk transitions
        updated_activations = status_simulator.simulate_bulk_transitions(max_transitions)
        
        return {
            "message": f"Bulk simulation completed: {len(updated_activations)} activations updated",
            "updated_activations": updated_activations,
            "count": len(updated_activations)
        }
        
    except Exception as e:
        logger.error(f"Bulk status simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk status simulation failed: {str(e)}")
    finally:
        db_connection.close()


@app.get("/status/list/pending", tags=["Status"])
async def get_pending_activations():
    """Get all pending activations."""
    logger.info("Pending activations request")
    
    db_connection = get_db_connection()
    
    try:
        status_simulator = StatusSimulator(db_connection)
        
        pending_activations = status_simulator.get_pending_activations()
        
        return {
            "pending_activations": pending_activations,
            "count": len(pending_activations)
        }
        
    except Exception as e:
        logger.error(f"Pending activations request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pending activations request failed: {str(e)}")
    finally:
        db_connection.close()


@app.post("/status/{activation_id}/force", tags=["Status"])
async def force_activation_status(activation_id: str, status: str):
    """Force an activation to a specific status (for testing)."""
    logger.info(f"Force status request: {activation_id} -> {status}")
    
    db_connection = get_db_connection()
    
    try:
        status_simulator = StatusSimulator(db_connection)
        
        # Force status
        updated_status = status_simulator.force_status(activation_id, status)
        
        if not updated_status:
            raise HTTPException(
                status_code=404, 
                detail=f"Activation not found or invalid status: {activation_id}, {status}"
            )
        
        response = StatusResponse(
            activation_id=updated_status["activation_id"],
            status=updated_status["status"],
            details=updated_status,
            created_at=datetime.fromisoformat(updated_status["created_at"]),
            updated_at=datetime.fromisoformat(updated_status["updated_at"]),
            completed_at=datetime.fromisoformat(updated_status["completed_at"]) if updated_status["completed_at"] else None
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Force status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Force status failed: {str(e)}")
    finally:
        db_connection.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port, reload=True)
