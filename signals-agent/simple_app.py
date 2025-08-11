#!/usr/bin/env python3
"""Simple FastAPI app for Railway deployment."""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow Railway health checks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including Railway
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
async def health(request: Request):
    """Health check endpoint for Railway - handles healthcheck.railway.app hostname."""
    # Log the hostname for debugging
    host = request.headers.get("host", "unknown")
    print(f"Health check from host: {host}")
    
    # Allow health checks from Railway's hostname
    if "healthcheck.railway.app" in host:
        print("Railway health check detected")
    
    return {"ok": True, "mode": "production", "host": host}

@app.get("/")
async def root(request: Request):
    """Root endpoint for Railway health checks."""
    host = request.headers.get("host", "unknown")
    return {
        "message": "Signals Agent API", 
        "status": "running",
        "host": host
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("simple_app:app", host="0.0.0.0", port=port, reload=False)
