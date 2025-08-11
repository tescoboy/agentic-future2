#!/usr/bin/env python3
"""Minimal FastAPI app for testing Railway deployment."""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Signals Agent API - Minimal",
    description="Minimal API for testing deployment",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint for health checks."""
    return {
        "message": "Signals Agent API - Minimal",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "ok": True,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/test", tags=["Test"])
async def test():
    """Test endpoint."""
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat()
    }
