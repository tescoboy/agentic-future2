#!/usr/bin/env python3
"""Minimal FastAPI app for testing Railway deployment."""

from fastapi import FastAPI, Request
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Signals Agent API - Minimal",
    description="Minimal API for testing deployment",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint for health checks."""
    logger.info("Root endpoint called")
    return {
        "message": "Signals Agent API - Minimal",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Health check endpoint for Railway."""
    logger.info(f"Health check called from: {request.client.host}")
    return {
        "status": "healthy",
        "ok": True,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "host": request.client.host if request.client else "unknown"
    }

@app.get("/test", tags=["Test"])
async def test():
    """Test endpoint."""
    logger.info("Test endpoint called")
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat()
    }
